#!/bin/bash
# Simple script to find model files - you can tell us where the drive is mounted

echo "Please tell us where your T9 SD drive is mounted, or we can search common locations:"
echo ""

# Check if user provided a path
if [ "$1" != "" ]; then
    SEARCH_PATH="$1"
    echo "Searching: $SEARCH_PATH"
else
    echo "Checking common mount locations..."
    # Common locations
    for loc in "/media" "/mnt" "/run/media/$USER" "$HOME/Desktop" "$HOME/Downloads" "$HOME/Documents"; do
        if [ -d "$loc" ]; then
            echo "Checking: $loc"
            find "$loc" -maxdepth 5 -type f \( -name "*.pkl" -o -name "*.joblib" \) 2>/dev/null | grep -i -E "model|train|nhl|nba|nfl|basketball|hockey|football" | head -10
        fi
    done
    echo ""
    echo "If your drive is mounted elsewhere, run:"
    echo "  $0 /path/to/mounted/drive"
    exit 0
fi

# Search the provided path
echo "Searching for model files in: $SEARCH_PATH"
find "$SEARCH_PATH" -type f \( -name "*.pkl" -o -name "*.joblib" \) 2>/dev/null | grep -i -E "model|train|nhl|nba|nfl|basketball|hockey|football|baseball" | while read file; do
    echo "Found: $file"
done


