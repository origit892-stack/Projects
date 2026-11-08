local function mark(s) return "ARGONPROOF| " .. s end
print(mark("PLACEID=" .. tostring(game.PlaceId)))
local function names(svc)
	local out = {}
	for _, c in svc:GetChildren() do
		local ex = ""
		if c:IsA("Model") then ex = "(n=" .. tostring(#c:GetChildren()) .. ")" end
		table.insert(out, c.Name .. "[" .. c.ClassName .. "]" .. ex)
	end
	return table.concat(out, ", ")
end
for _, name in ipairs({"Workspace", "ServerScriptService", "ReplicatedStorage", "StarterGui", "StarterPlayer"}) do
	print(mark(name .. " => " .. names(game:GetService(name))))
end
local ws = game:GetService("Workspace")
local total = 0
for _ in ws:GetDescendants() do total += 1 end
print(mark("WS_TOTAL_DESCENDANTS=" .. total))
