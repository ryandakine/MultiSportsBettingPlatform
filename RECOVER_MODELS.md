# Recovering Trained Models from External Drive

## Step 1: Mount the External Drive

The T9 SD drive needs to be mounted. Try one of these:

### Option A: If it's already mounted but in an unexpected location
```bash
# Check all mount points
mount | grep -i "t9\|sd\|usb"

# Check common locations
ls -la /media/*/
ls -la /mnt/*/
ls -la /run/media/*/
```

### Option B: Mount it manually
```bash
# Create mount point
sudo mkdir -p /mnt/t9_drive

# Find the device (look for something like /dev/sdb1 or /dev/sdc1)
lsblk

# Mount it (replace /dev/sdX1 with your actual device)
sudo mount /dev/sdX1 /mnt/t9_drive

# Check if it mounted
ls /mnt/t9_drive
```

## Step 2: Find Model Files

Once mounted, search for model files:

```bash
# Find all .pkl files
find /mnt/t9_drive -name "*.pkl" -type f 2>/dev/null

# Find all .joblib files
find /mnt/t9_drive -name "*.joblib" -type f 2>/dev/null

# Find files with "model" in the name
find /mnt/t9_drive -iname "*model*" -type f 2>/dev/null

# Find files with "train" in the name
find /mnt/t9_drive -iname "*train*" -type f 2>/dev/null
```

## Step 3: Copy Models to Project

Once found, copy them to the project:

```bash
# Create models directory
cd /home/ryan/MultiSportsBettingPlatform
mkdir -p models/trained

# Copy model files (adjust paths as needed)
cp /mnt/t9_drive/path/to/nhl_model.pkl models/trained/
cp /mnt/t9_drive/path/to/nhl_model.joblib models/trained/
# etc.
```

## Step 4: Verify Models

After copying, verify they're in the right place:

```bash
ls -lh models/trained/
```

## What to Look For

Model files typically have names like:
- `nhl_model.pkl` or `nhl_model.joblib`
- `basketball_model.pkl`
- `football_model.pkl`
- `hockey_model.pkl`
- Or in subdirectories like `models/nhl/`, `trained_models/`, etc.

The system will look for:
- `models/trained/nhl_model.joblib` (for NHL)
- `models/trained/nba_model.joblib` (for NBA/basketball)
- `models/trained/nfl_model.joblib` (for NFL/football)
- etc.

## Once Models Are in Place

The system will automatically:
1. Load models on startup
2. Use them for predictions
3. Log: "✅ Using trained models: nhl, nba, etc."
4. Include `model_used: true` in predictions


