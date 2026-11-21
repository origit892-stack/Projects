-- MapBootstrap.server.lua
-- Runs the generated build when the place is played (ServerScriptService).
-- For an Edit-mode build without pressing Play, use CommandBar_Install.lua or the Idea2World
-- Studio bridge, which call MapBootstrap.build() directly.
local MapBootstrap = require(script.Parent:WaitForChild("MapBootstrap"))

local report = MapBootstrap.build({ verbose = false })

if report.passed then
	print(("[Idea2World] '%s' ready — %d landmarks, %d placements, %.1fs")
		:format(report.title, report.stats.pois, report.stats.placements, report.stats.seconds))
else
	warn(("[Idea2World] '%s' built with validation issues: %s")
		:format(report.title, table.concat(report.validation.failures or {}, ", ")))
end

-- Expose a small API for live debugging from the command bar while the game runs.
_G.Idea2World = {
	Build = MapBootstrap.build,
	Validate = MapBootstrap.validate,
	Clear = MapBootstrap.clear,
	Info = MapBootstrap.info,
}
