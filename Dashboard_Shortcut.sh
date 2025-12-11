#!/bin/bash
echo "🚀 Opening Multi-Sports Betting Dashboard..."
if which xdg-open > /dev/null; then
    xdg-open http://localhost:3000
elif which open > /dev/null; then
    open http://localhost:3000
else
    echo "❌ Could not detect browser opener. Please open http://localhost:3000 manually."
fi
