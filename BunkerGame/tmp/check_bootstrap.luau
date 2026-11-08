local mark = function(s) return "BOOT|" .. s end
print(mark("START"))
local sps = game:GetService("StarterPlayer"):FindFirstChild("StarterPlayerScripts")
print(mark("spsExists=" .. tostring(sps ~= nil)))
if sps then
	local gc = sps:FindFirstChild("GameClient")
	print(mark("gameClientExists=" .. tostring(gc ~= nil)))
	if gc then
		local cb = gc:FindFirstChild("ClientBootstrap")
		print(mark("bootstrapExists=" .. tostring(cb ~= nil)))
		if cb then
			print(mark("bootstrapClass=" .. tostring(cb.ClassName)))
			local src = cb.Source or ""
			print(mark("bootstrapCallsStart=" .. tostring(src:find("ui:Start") ~= nil)))
		end
		local ui = gc:FindFirstChild("UIController")
		print(mark("uiControllerExists=" .. tostring(ui ~= nil)))
		if ui then
			print(mark("uiClass=" .. tostring(ui.ClassName)))
		end
	end
end
print(mark("DONE"))