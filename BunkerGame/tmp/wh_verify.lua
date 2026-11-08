local ws = game:GetService("Workspace")
local wh = ws:FindFirstChild("abandoned_warehouse_interior_01")
local result
if not wh then
    result = "NOT_FOUND"
else
    local count = 0
    local sample = nil
    local minPos, maxPos = nil, nil
    for _, d in ipairs(wh:GetDescendants()) do
        if d:IsA("MeshPart") then
            count = count + 1
            if not sample then sample = d end
            local p = d.Position
            if not minPos then minPos, maxPos = p, p
            else
                minPos = Vector3.new(math.min(minPos.X,p.X), math.min(minPos.Y,p.Y), math.min(minPos.Z,p.Z))
                maxPos = Vector3.new(math.max(maxPos.X,p.X), math.max(maxPos.Y,p.Y), math.max(maxPos.Z,p.Z))
            end
        end
    end
    result = string.format("FOUND parts=%d sample_pos=%s sample_meshid=%s min=%s max=%s", count, tostring(sample and sample.Position), tostring(sample and sample.MeshId), tostring(minPos), tostring(maxPos))
end
local ok, err = pcall(function() writefile("wh_verify", "result.txt", result) end)
if not ok then
    pcall(function() writefile("wh_verify_result.txt", result) end)
end
print(result)