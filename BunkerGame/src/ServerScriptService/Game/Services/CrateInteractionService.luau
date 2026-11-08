local TweenService = game:GetService("TweenService")

-- 1. מוצאים את הארגז ישירות ב-Workspace
local crate = workspace:WaitForChild("old_military_ammo_crate_01")
-- מניחים שלחלק העליון קוראים "Lid" (אם השם שונה במודל, שנה אותו כאן)
local lid = crate:FindFirstChild("Lid") or crate:FindFirstChild("Top") 

-- 2. יוצרים את כפתור ה-E (ProximityPrompt)
local prompt = Instance.new("ProximityPrompt")
prompt.Name = "OpenCratePrompt"
prompt.ActionText = "Open Crate"
prompt.KeyboardKeyCode = Enum.KeyCode.E
prompt.HoldDuration = 1
prompt.Parent = crate -- מחברים את הכפתור לארגז

-- 3. מה קורה כשלוחצים E
prompt.Triggered:Connect(function(player)
	print("Ammo Crate Opened by " .. player.Name .. "!")
	
	-- מכבים את הכפתור כדי שאי אפשר יהיה לפתוח שוב
	prompt.Enabled = false
	
	-- מפעילים את אנימציית הפתיחה
	if lid then
		local tweenInfo = TweenInfo.new(1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
		-- מסובבים את המכסה אחורה ב-60 מעלות (math.rad הופך מעלות לרדיאנים)
		local goal = {CFrame = lid.CFrame * CFrame.Angles(math.rad(60), 0, 0)}
		local tween = TweenService:Create(lid, tweenInfo, goal)
		tween:Play()
	else
		warn("Lid not found! The crate needs a part named 'Lid' to animate.")
	end
end)