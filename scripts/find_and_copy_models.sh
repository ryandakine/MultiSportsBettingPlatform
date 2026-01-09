#!/bin/bash
# Script to find and copy trained model files from external drive

echo "🔍 Searching for model files..."
echo ""

# Create models directory
mkdir -p models/trained

# Common mount points to check
MOUNT_POINTS=("/media" "/mnt" "/run/media" "$HOME/Desktop" "$HOME/Downloads" "$HOME/Documents")

echo "Checking common mount points..."
for mount_point in "${MOUNT_POINTS[@]}"; do
    if [ -d "$mount_point" ]; then
        echo "  Checking: $mount_point"
        find "$mount_point" -maxdepth 4 -type f \( -name "*.pkl" -o -name "*.joblib" \) 2>/dev/null | \
            grep -i -E "model|train|nhl|nba|nfl|basketball|hockey|football" | \
            head -20
    fi
done

echo ""
echo "If you see model files above, copy them to models/trained/"
echo ""
echo "Example:"
echo "  cp /path/to/found/model.pkl models/trained/"
echo ""
echo "Or if the external drive is at /mnt/t9_drive:"
echo "  find /mnt/t9_drive -name '*.pkl' -o -name '*.joblib' | xargs -I {} cp {} models/trained/"
echo ""

# Check if models directory was created and has files
if [ -d "models/trained" ] && [ "$(ls -A models/trained 2>/dev/null)" ]; then
    echo "✅ Found models in models/trained/:"
    ls -lh models/trained/
else
    echo "⚠️  No models found yet. Make sure the external drive is mounted."
    echo ""
    echo "To mount the external drive:"
    echo "  1. Find the device: lsblk"
    echo "  2. Create mount point: sudo mkdir -p /mnt/t9_drive"
    echo "  3. Mount: sudo mount /dev/sdX1 /mnt/t9_drive"
    echo "  4. Then search: find /mnt/t9_drive -name '*.pkl' -o -name '*.joblib'"
fi


