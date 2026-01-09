# How to Sync Your Laptop Work to GitHub

## 🎯 Quick Answer

You have **two options** depending on where your laptop changes are:

### Option 1: Push from Your Laptop (Recommended)

If you still have your laptop with you:

1. **On your laptop**, open Git Bash or PowerShell
2. Navigate to the repo:
   ```bash
   cd MultiSportsBettingPlatform
   ```
3. Check what changes you have:
   ```bash
   git status
   ```
4. If you have changes, commit them:
   ```bash
   git add .
   git commit -m "Work from laptop"
   ```
5. Push to GitHub:
   ```bash
   git push origin master
   ```

✅ Done! Your laptop work is now on GitHub.

---

### Option 2: Check if Already Pushed

If you already pushed from your laptop, you can pull those changes on your desktop:

1. **On your desktop** (where you are now):
   ```bash
   cd /home/ryan/MultiSportsBettingPlatform
   git fetch origin
   git pull origin master
   ```

This will download any changes that are on GitHub but not on your desktop.

---

## 🔍 How to Check What's on GitHub vs Your Machines

### Check what's on GitHub:
```bash
git fetch origin
git log origin/master --oneline -10
```

### Check what's on your laptop:
On your laptop, run:
```bash
git log --oneline -10
```

Compare the commit hashes. If they're different, you need to sync.

---

## ⚠️ If You Have Conflicting Changes

If you made changes on **both** laptop and desktop:

1. **First, push from laptop** (if you haven't already):
   ```bash
   # On laptop
   git add .
   git commit -m "Laptop changes"
   git push origin master
   ```

2. **Then pull on desktop**:
   ```bash
   # On desktop
   git pull origin master
   ```

If there are conflicts, Git will tell you which files need to be resolved.

---

## 📋 Step-by-Step Checklist

- [ ] Open your laptop
- [ ] Open Git Bash or PowerShell
- [ ] Go to the repo: `cd MultiSportsBettingPlatform`
- [ ] Check status: `git status`
- [ ] If you have uncommitted changes:
  - [ ] `git add .`
  - [ ] `git commit -m "Description of your work"`
  - [ ] `git push origin master`
- [ ] On your desktop, pull latest: `git pull origin master`

---

## 🆘 Troubleshooting

### "Permission denied" when pushing from laptop:
- Make sure you added your laptop's SSH key to GitHub
- Check: `ssh -T git@github.com` (should say "Hi ryandakine!")

### "Your branch is behind":
- Someone (or you from another machine) pushed changes
- Run: `git pull origin master` first, then push

### "Merge conflicts":
- Git will mark conflicted files with `<<<<<<<` markers
- Edit those files to resolve conflicts
- Then: `git add .` and `git commit`

---

## 💡 Best Practice Going Forward

**Always pull before you start working:**
```bash
git pull origin master
```

**Always push when you're done:**
```bash
git add .
git commit -m "What you did"
git push origin master
```

This keeps everything in sync! 🎯



