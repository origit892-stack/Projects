--!strict

local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")
local ServerStorage = game:GetService("ServerStorage")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local DATASTORE_NAME = Config.Profile.DataStoreName
local LEASE_SECONDS = Config.Persistence.LockLeaseSeconds
local LOAD_DEADLINE_SECONDS = Config.Persistence.LoadDeadlineSeconds
local LOAD_BACKOFF = Config.Persistence.LoadBackoffSeconds

local function copy(value: any): any
	if type(value) ~= "table" then
		return value
	end
	local result = {}
	for key, child in pairs(value) do
		result[copy(key)] = copy(child)
	end
	return result
end

local function profileKey(userId: number): string
	return Config.Profile.RecordKeyPrefix .. tostring(userId)
end

local function boundedJitter(userId: number, attempt: number): number
	return ((userId * 31 + attempt * 17) % 101) / 500
end

local PersistenceRepository = {}
PersistenceRepository.__index = PersistenceRepository

function PersistenceRepository.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_closed = false,
		_mode = "Memory",
		_jobId = if game.JobId ~= "" then game.JobId else "studio-" .. HttpService:GenerateGUID(false),
		_profileSchema = nil,
		_dataStore = nil,
		_memoryRecords = {} :: { [number]: any },
		_knownRevisions = {} :: { [number]: number },
	}, PersistenceRepository)
end

function PersistenceRepository.Init(self, bag)
	if self._initialized then
		return
	end
	self._profileSchema = bag.Context.ProfileSchema
	assert(type(self._profileSchema) == "table", "ProfileSchema shared module is required")
	assert(type(self._profileSchema.CreateDefault) == "function", "ProfileSchema.CreateDefault is required")
	assert(type(self._profileSchema.Validate) == "function", "ProfileSchema.Validate is required")

	local studioDataStoreEnabled = ServerStorage:GetAttribute("FG_UseProductionDataStoreInStudio") == true
	if not RunService:IsStudio() or studioDataStoreEnabled then
		self._mode = "DataStore"
		self._dataStore = DataStoreService:GetDataStore(DATASTORE_NAME)
	else
		self._mode = "Memory"
	end
	self._initialized = true
	self._closed = false
end

function PersistenceRepository.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "PersistenceRepository must initialize before Start")
	self._started = true
end

function PersistenceRepository.GetMode(self): string
	return self._mode
end

function PersistenceRepository:_validateProfile(profile, invalidCode: string?): (boolean, string?)
	if type(profile) ~= "table" then
		return false, invalidCode or "PROFILE_LOAD_FAILED"
	end
	if type(profile.SchemaVersion) == "number" and profile.SchemaVersion ~= Config.Profile.SchemaVersion then
		return false, "PROFILE_VERSION_UNSUPPORTED"
	end
	local ok = self._profileSchema.Validate(profile)
	if not ok then
		return false, invalidCode or "PROFILE_LOAD_FAILED"
	end
	return true, nil
end

function PersistenceRepository:_newRecord(now: number)
	local profile = self._profileSchema.CreateDefault()
	local valid, code = self:_validateProfile(profile, "PROFILE_CONFLICT")
	assert(valid, string.format("ProfileSchema.CreateDefault produced invalid data: %s", tostring(code)))
	return {
		Profile = copy(profile),
		Lock = {
			JobId = self._jobId,
			ExpiresAt = now + LEASE_SECONDS,
		},
	}
end

function PersistenceRepository:Load(userId: number): (boolean, any, string?)
	if self._closed then
		return false, nil, "PROFILE_LOAD_FAILED"
	end
	assert(type(userId) == "number" and userId > 0 and userId % 1 == 0, "userId must be a positive integer")

	if self._mode == "Memory" then
		local now = os.time()
		local record = self._memoryRecords[userId]
		if record == nil then
			record = self:_newRecord(now)
			self._memoryRecords[userId] = record
		else
			if type(record) == "table" and type(record.Profile) == "table" and type(record.Profile.SchemaVersion) == "number" and record.Profile.SchemaVersion ~= Config.Profile.SchemaVersion then
				return false, nil, "PROFILE_VERSION_UNSUPPORTED"
			end
			local recordValid = self._profileSchema.ValidateStoredRecord(record)
			if not recordValid then
				return false, nil, "PROFILE_LOAD_FAILED"
			end
			local valid, code = self:_validateProfile(record.Profile)
			if not valid then
				return false, nil, code
			end
			local lock = record.Lock
			if type(lock) == "table" and lock.JobId ~= self._jobId and lock.JobId ~= "" and lock.ExpiresAt > now then
				return false, nil, "PROFILE_LOCKED"
			end
			record.Lock = {
				JobId = self._jobId,
				ExpiresAt = now + LEASE_SECONDS,
			}
		end
		self._knownRevisions[userId] = record.Profile.Revision
		return true, copy(record.Profile), nil
	end

	local deadline = os.clock() + LOAD_DEADLINE_SECONDS
	local finalCode = "PROFILE_LOAD_FAILED"
	for attempt, delaySeconds in ipairs(LOAD_BACKOFF) do
		if os.clock() >= deadline then
			break
		end
		local acquiredProfile = nil
		local callbackCode = nil
		local ok = pcall(function()
			self._dataStore:UpdateAsync(profileKey(userId), function(stored)
				-- UpdateAsync may rerun this callback after a write conflict. Only the
				-- final invocation may decide whether the lease was acquired.
				acquiredProfile = nil
				callbackCode = nil
				local now = os.time()
				local record = stored
				if record == nil then
					record = self:_newRecord(now)
				else
					if type(record) == "table" and type(record.Profile) == "table" and type(record.Profile.SchemaVersion) == "number" and record.Profile.SchemaVersion ~= Config.Profile.SchemaVersion then
						callbackCode = "PROFILE_VERSION_UNSUPPORTED"
						return nil
					end
					local recordValid = self._profileSchema.ValidateStoredRecord(record)
					if not recordValid then
						callbackCode = "PROFILE_LOAD_FAILED"
						return nil
					end
					local valid, code = self:_validateProfile(record.Profile)
					if not valid then
						callbackCode = code
						return nil
					end
					local lock = record.Lock
					if lock.JobId ~= self._jobId and lock.JobId ~= "" and lock.ExpiresAt > now then
						callbackCode = "PROFILE_LOCKED"
						return nil
					end
					record = copy(record)
					record.Lock = {
						JobId = self._jobId,
						ExpiresAt = now + LEASE_SECONDS,
					}
				end
				acquiredProfile = copy(record.Profile)
				return record
			end)
		end)
		if ok and acquiredProfile ~= nil then
			self._knownRevisions[userId] = acquiredProfile.Revision
			return true, acquiredProfile, nil
		end
		if callbackCode ~= nil then
			finalCode = callbackCode
			if callbackCode == "PROFILE_LOCKED" or callbackCode == "PROFILE_VERSION_UNSUPPORTED" then
				break
			end
		end
		if attempt < #LOAD_BACKOFF then
			local remaining = deadline - os.clock()
			if remaining <= 0 then
				break
			end
			task.wait(math.min(remaining, delaySeconds + boundedJitter(userId, attempt)))
		end
	end
	return false, nil, finalCode
end

function PersistenceRepository:Save(userId: number, profile): (boolean, string?)
	if self._closed then
		return false, "PROFILE_LOAD_FAILED"
	end
	local valid, validationCode = self:_validateProfile(profile, "PROFILE_CONFLICT")
	if not valid then
		return false, validationCode
	end
	local knownRevision = self._knownRevisions[userId]
	if knownRevision == nil then
		return false, "PROFILE_CONFLICT"
	end

	if self._mode == "Memory" then
		local record = self._memoryRecords[userId]
		if record == nil or record.Lock.JobId ~= self._jobId or record.Profile.Revision ~= knownRevision then
			return false, "PROFILE_CONFLICT"
		end
		record.Profile = copy(profile)
		record.Lock.ExpiresAt = os.time() + LEASE_SECONDS
		self._knownRevisions[userId] = profile.Revision
		return true, nil
	end

	local saved = false
	local callbackCode = nil
	local ok = pcall(function()
		self._dataStore:UpdateAsync(profileKey(userId), function(record)
			saved = false
			callbackCode = nil
			local recordValid = self._profileSchema.ValidateStoredRecord(record)
			if not recordValid then
				callbackCode = "PROFILE_CONFLICT"
				return nil
			end
			if record.Lock.JobId ~= self._jobId then
				callbackCode = "PROFILE_LOCKED"
				return nil
			end
			if record.Profile.Revision ~= knownRevision then
				callbackCode = "PROFILE_CONFLICT"
				return nil
			end
			saved = true
			return {
				Profile = copy(profile),
				Lock = {
					JobId = self._jobId,
					ExpiresAt = os.time() + LEASE_SECONDS,
				},
			}
		end)
	end)
	if not ok or not saved then
		return false, callbackCode or "PROFILE_LOAD_FAILED"
	end
	self._knownRevisions[userId] = profile.Revision
	return true, nil
end

function PersistenceRepository:Release(userId: number): (boolean, string?)
	if self._knownRevisions[userId] == nil then
		return true, nil
	end
	if self._mode == "Memory" then
		local record = self._memoryRecords[userId]
		if record ~= nil and record.Lock.JobId == self._jobId then
			record.Lock = { JobId = self._jobId, ExpiresAt = 0 }
		end
		self._knownRevisions[userId] = nil
		return true, nil
	end

	local released = false
	local callbackCode = nil
	local ok = pcall(function()
		self._dataStore:UpdateAsync(profileKey(userId), function(record)
			released = false
			callbackCode = nil
			local recordValid = self._profileSchema.ValidateStoredRecord(record)
			if not recordValid then
				callbackCode = "PROFILE_CONFLICT"
				return nil
			end
			if record.Lock.JobId ~= self._jobId then
				callbackCode = "PROFILE_LOCKED"
				return nil
			end
			local result = copy(record)
			result.Lock = { JobId = self._jobId, ExpiresAt = 0 }
			released = true
			return result
		end)
	end)
	if not ok or not released then
		return false, callbackCode or "PROFILE_LOAD_FAILED"
	end
	self._knownRevisions[userId] = nil
	return true, nil
end

function PersistenceRepository:Close()
	self._closed = true
	self._started = false
	table.clear(self._knownRevisions)
end

function PersistenceRepository.Stop(self)
	if self._closed then
		return
	end
	self:Close()
end

return PersistenceRepository
