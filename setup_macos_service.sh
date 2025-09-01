#!/bin/bash
# Setup macOS LaunchAgent to run Telegram bot automatically

PLIST_FILE="$HOME/Library/LaunchAgents/com.jobsearch.telegram.plist"
SCRIPT_PATH="$(pwd)/start_telegram_bot.py"
PYTHON_PATH=$(which python3)

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jobsearch.telegram</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/telegram-bot-error.log</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/telegram-bot.log</string>
</dict>
</plist>
EOF

echo "✅ Created LaunchAgent: $PLIST_FILE"
echo ""
echo "🚀 To start the service:"
echo "   launchctl load $PLIST_FILE"
echo ""
echo "🛑 To stop the service:"
echo "   launchctl unload $PLIST_FILE"
echo ""
echo "📋 To check status:"
echo "   launchctl list | grep telegram"
echo ""
echo "📝 Logs will be in:"
echo "   $HOME/Library/Logs/telegram-bot.log"
