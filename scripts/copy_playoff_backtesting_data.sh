#!/bin/bash
# Copy playoff/backtesting related files from external drive

SOURCE_DIR="/media/ryan/ROOTFS/home/kali/ryan_offload/repos/football_betting_system_full"
TARGET_DIR="$HOME/MultiSportsBettingPlatform/data/playoff_backtesting/existing_backtests"

mkdir -p "$TARGET_DIR"

echo "📦 Copying playoff/backtesting files from external drive..."
echo "Source: $SOURCE_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Copy NCAA-specific backtesting files
if [ -f "$SOURCE_DIR/backtest_ncaa_parlays_REALISTIC.py" ]; then
    cp "$SOURCE_DIR/backtest_ncaa_parlays_REALISTIC.py" "$TARGET_DIR/"
    echo "✅ Copied: backtest_ncaa_parlays_REALISTIC.py"
fi

if [ -f "$SOURCE_DIR/backtest_ncaa_parlays_10_years.py" ]; then
    cp "$SOURCE_DIR/backtest_ncaa_parlays_10_years.py" "$TARGET_DIR/"
    echo "✅ Copied: backtest_ncaa_parlays_10_years.py"
fi

if [ -f "$SOURCE_DIR/backtest_ncaa_r1_system.py" ]; then
    cp "$SOURCE_DIR/backtest_ncaa_r1_system.py" "$TARGET_DIR/"
    echo "✅ Copied: backtest_ncaa_r1_system.py"
fi

if [ -f "$SOURCE_DIR/prop_backtest_framework.py" ]; then
    cp "$SOURCE_DIR/prop_backtest_framework.py" "$TARGET_DIR/"
    echo "✅ Copied: prop_backtest_framework.py"
fi

if [ -f "$SOURCE_DIR/backtesting_engine.py" ]; then
    cp "$SOURCE_DIR/backtesting_engine.py" "$TARGET_DIR/"
    echo "✅ Copied: backtesting_engine.py"
fi

# Copy season backtest results
echo ""
echo "📊 Copying season backtest results..."
for file in "$SOURCE_DIR"/backtest_season_*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$TARGET_DIR/"
        echo "✅ Copied: $filename"
    fi
done

# Copy backtest results
if [ -f "$SOURCE_DIR/backtest_enhanced_results.json" ]; then
    cp "$SOURCE_DIR/backtest_enhanced_results.json" "$TARGET_DIR/"
    echo "✅ Copied: backtest_enhanced_results.json"
fi

if [ -f "$SOURCE_DIR/backtest_2024_extended_20251105_085343.json" ]; then
    cp "$SOURCE_DIR/backtest_2024_extended_20251105_085343.json" "$TARGET_DIR/"
    echo "✅ Copied: backtest_2024_extended_20251105_085343.json"
fi

echo ""
echo "✅ Done! Files copied to: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "1. Review the copied backtesting scripts"
echo "2. Extract any playoff-specific logic"
echo "3. Integrate with our playoff backtesting framework"


