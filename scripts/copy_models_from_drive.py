#!/usr/bin/env python3
"""
Copy trained model files from external drive to project.
Run this after mounting your T9 SD drive.
"""

import os
import shutil
from pathlib import Path

def find_model_files(search_paths):
    """Find model files in given paths."""
    model_files = []
    extensions = ['.pkl', '.joblib']
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        print(f"🔍 Searching: {search_path}")
        for root, dirs, files in os.walk(search_path):
            # Skip hidden and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    # Check if it's likely a model file
                    if any(keyword in file.lower() for keyword in ['model', 'train', 'nhl', 'nba', 'nfl', 'basketball', 'hockey', 'football', 'baseball']):
                        full_path = os.path.join(root, file)
                        model_files.append(full_path)
    
    return model_files

def copy_models_to_project(model_files, dest_dir):
    """Copy model files to project models directory."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    copied = []
    for model_file in model_files:
        filename = os.path.basename(model_file)
        dest_path = dest_dir / filename
        
        try:
            shutil.copy2(model_file, dest_path)
            copied.append(filename)
            print(f"✅ Copied: {filename}")
        except Exception as e:
            print(f"❌ Failed to copy {filename}: {e}")
    
    return copied

def main():
    project_root = Path(__file__).parent.parent
    models_dir = project_root / "models" / "trained"
    
    print("=" * 60)
    print("🔍 Finding Model Files on External Drive")
    print("=" * 60)
    print()
    
    # Common mount points and search locations
    search_paths = [
        "/mnt/t9_drive",
        "/media",
        "/run/media",
        str(Path.home() / "Desktop"),
        str(Path.home() / "Downloads"),
        str(Path.home() / "Documents"),
        "/mnt",
    ]
    
    # Also check if user specified a path
    import sys
    if len(sys.argv) > 1:
        search_paths.insert(0, sys.argv[1])
        print(f"📁 Using custom path: {sys.argv[1]}")
        print()
    
    print("Searching for model files...")
    model_files = find_model_files(search_paths)
    
    if not model_files:
        print("\n⚠️  No model files found!")
        print("\nMake sure your T9 SD drive is mounted.")
        print("\nTo mount it:")
        print("  1. Find the device: lsblk")
        print("  2. Create mount point: sudo mkdir -p /mnt/t9_drive")
        print("  3. Mount it: sudo mount /dev/sdX1 /mnt/t9_drive")
        print("  4. Run this script with the mount path:")
        print(f"     python3 {__file__} /mnt/t9_drive")
        return
    
    print(f"\n📦 Found {len(model_files)} model file(s):")
    for f in model_files:
        size = os.path.getsize(f) / (1024 * 1024)  # Size in MB
        print(f"   {f} ({size:.1f} MB)")
    
    print(f"\n📂 Copying to: {models_dir}")
    copied = copy_models_to_project(model_files, models_dir)
    
    if copied:
        print(f"\n✅ Successfully copied {len(copied)} model file(s)!")
        print(f"\nModels are now in: {models_dir}")
        print("\nThe system will automatically use these models on next startup.")
    else:
        print("\n❌ Failed to copy any files.")

if __name__ == "__main__":
    main()


