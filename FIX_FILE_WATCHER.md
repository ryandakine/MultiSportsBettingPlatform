# 🚀 Fix VS Code File Watcher Limit (ENOSPC Error)

## Current Status
- **Current Limit**: 120,316 (below recommended 524,288)
- **VS Code Settings**: ✅ Configured to exclude large directories

## Quick Fix

Run these commands in your terminal:

```bash
# Add the setting to sysctl.conf
sudo sh -c 'echo "" >> /etc/sysctl.conf'
sudo sh -c 'echo "# VS Code file watcher limit (fixes ENOSPC error)" >> /etc/sysctl.conf'
sudo sh -c 'echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf'

# Apply the changes immediately
sudo sysctl -p
sudo sysctl fs.inotify.max_user_watches=524288

# Verify the new limit
cat /proc/sys/fs/inotify/max_user_watches
```

Or use the provided script:
```bash
sudo ./scripts/fix_file_watcher_limit.sh
```

## After Running the Commands

1. ✅ Restart VS Code completely
2. ✅ The ENOSPC error should be resolved
3. ✅ File watching will work properly

## What Was Fixed

1. **VS Code Settings** (`.vscode/settings.json`):
   - Excludes `node_modules`, `__pycache__`, `.git/objects`, `.venv`, `archive/`, and other large directories from file watching
   - Reduces the number of files VS Code needs to watch

2. **System Limit Increase**:
   - Increases the Linux inotify file watcher limit from 120,316 to 524,288
   - This is the maximum recommended value
   - Takes effect immediately and persists after reboot

## Memory Impact

Each file watch uses approximately 1,080 bytes. At the maximum of 524,288 watches, this results in an upper bound of around 540 MiB of memory, which is reasonable for modern systems.




