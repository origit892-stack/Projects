#!/bin/zsh
echo '=== RobloxStudio window UI buttons ==='
osascript <<'EOF' 2>&1
tell application "System Events"
  tell process "RobloxStudio"
    set frontmost to true
    delay 0.5
    try
      repeat with w in (every window)
        log "WINDOW: " & (name of w)
        try
          repeat with b in (every button of w)
            set bdesc to description of b
            set btitle to ""
            try
              set btitle to title of b
            end try
            log "  BUTTON: desc=[" & bdesc & "] title=[" & btitle & "]"
          end repeat
        end try
      end repeat
    on error errMsg
      log "ERROR: " & errMsg
    end try
  end tell
end tell
EOF