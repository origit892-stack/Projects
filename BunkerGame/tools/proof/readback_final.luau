local function mark(s) return "ARGONPROOF2| " .. s end
print(mark("PLACEID=" .. tostring(game.PlaceId)))
local ws = game:GetService("Workspace")
local kids = {}
for _, c in ws:GetChildren() do
	table.insert(kids, c.Name .. "[" .. c.ClassName .. "]")
end
print(mark("WS_CHILDREN(" .. #kids .. ")=" .. table.concat(kids, ", ")))
local total = 0
for _ in ws:GetDescendants() do total += 1 end
print(mark("WS_TOTAL_DESCENDANTS=" .. total))
local proof = game:FindFirstChild("ArgonProof", true)
print(mark("PROOF_INSTANCES_IN_PLACE=" .. tostring(proof ~= nil)))
