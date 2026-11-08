local ok, err = pcall(function()
	warn("ARGONPING| studio reachable | place=" .. tostring(game.PlaceId))
end)
if not ok then
	warn("ARGONPING| error: " .. tostring(err))
end