#!/bin/bash
# 🚀 Fix VS Code File Watcher Limit (ENOSPC Error)
# This script increases the inotify file watcher limit to prevent VS Code errors

echo "🔍 Checking current file watcher limit..."
CURRENT_LIMIT=$(cat /proc/sys/fs/inotify/max_user_watches)
echo "✅ Current limit: $CURRENT_LIMIT"

if [ "$CURRENT_LIMIT" -lt 524288 ]; then
    echo "⚠️  Limit is below recommended value (524288)"
    echo "🔧 Attempting to increase the limit..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        # Check if the setting already exists in sysctl.conf
        if grep -q "fs.inotify.max_user_watches" /etc/sysctl.conf; then
            echo "⚠️  Setting already exists in /etc/sysctl.conf, updating..."
            sed -i 's/^fs.inotify.max_user_watches=.*/fs.inotify.max_user_watches=524288/' /etc/sysctl.conf
        else
            echo "➕ Adding fs.inotify.max_user_watches=524288 to /etc/sysctl.conf"
            echo "" >> /etc/sysctl.conf
            echo "# VS Code file watcher limit (fixes ENOSPC error)" >> /etc/sysctl.conf
            echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf
        fi
        
        # Apply the setting immediately
        sysctl -p > /dev/null 2>&1
        sysctl fs.inotify.max_user_watches=524288
        
        NEW_LIMIT=$(cat /proc/sys/fs/inotify/max_user_watches)
        echo "✅ New limit applied: $NEW_LIMIT"
        echo "🎯 File watcher limit has been increased successfully!"
    else
        echo "❌ This script needs to be run with sudo privileges"
        echo "📝 Please run: sudo $0"
        echo ""
        echo "Or manually run these commands:"
        echo "  sudo sh -c 'echo \"fs.inotify.max_user_watches=524288\" >> /etc/sysctl.conf'"
        echo "  sudo sysctl -p"
        echo "  sudo sysctl fs.inotify.max_user_watches=524288"
        exit 1
    fi
else
    echo "✅ Limit is already at or above recommended value"
fi

echo ""
echo "🎉 File watcher limit fix complete!"
echo "💡 Note: You may need to restart VS Code for changes to take full effect"

