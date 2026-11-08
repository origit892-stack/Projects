#!/bin/zsh
echo '=== Searching RobloxStudio AX tree for Play/Stop/Server controls ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set frontmost to true
    delay 0.5
    set foundList to {}
    -- Search buttons at window level and one level deep
    repeat with w in (every window)
      try
        repeat with el in (entire contents of w)
          try
            set r to role of el
            if r is "AXButton" or r is "AXToolbarButton" or r is "AXMenuItem" then
              set d to ""
              try
                set d to description of el
              end try
              set t to ""
              try
                set t to title of el
              end try
              set combined to d & " | " & t
              if (combined contains "Play") or (combined contains "Stop") or (combined contains "Server") or (combined contains "Run") or (combined contains "Solo") or (combined contains "Client") then
                set end of foundList to (r & " :: desc=[" & d & "] title=[" & t & "]")
              end if
            end if
          end try
        end repeat
      end try
    end repeat
    if (count of foundList) is 0 then
      log "NO matching controls found. Dumping all button descriptions:"
      repeat with w in (every window)
        try
          repeat with el in (entire contents of w)
            try
              if (role of el) is "AXButton" then
                set d to ""
                try
                  set d to description of el
                end try
                log "  BTN desc=[" & d & "]"
              end if
            end try
          end repeat
        end try
      end repeat
    else
      repeat with f in foundList
        log f
      end repeat
    end if
  end tell
end tell
EOF