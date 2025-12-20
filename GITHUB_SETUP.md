# GitHub Authentication Setup Guide

## Current Status
- ✅ **SSH Authentication**: Set up and working
- ✅ **Remote**: Using SSH (`git@github.com:ryandakine/MultiSportsBettingPlatform.git`)
- ✅ **All code pushed**: 97 files, 31,080+ lines committed
- 📋 **Windows Guide**: See `GITHUB_SETUP_WINDOWS.md` for Windows-specific instructions

## Option 1: SSH Keys (RECOMMENDED for laptop use)

### Step 1: Check if you have SSH keys
```bash
ls -la ~/.ssh/id_*.pub
```

### Step 2: Generate SSH key (if you don't have one)
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location
# Optionally set a passphrase (or press Enter for no passphrase)
```

### Step 3: Add SSH key to GitHub
```bash
# Copy your public key
cat ~/.ssh/id_ed25519.pub
# Or if using RSA:
# cat ~/.ssh/id_rsa.pub
```

Then:
1. Go to GitHub.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste your public key
4. Click "Add SSH key"

### Step 4: Change remote to SSH
```bash
cd /home/ryan/MultiSportsBettingPlatform
git remote set-url origin git@github.com:ryandakine/MultiSportsBettingPlatform.git
```

### Step 5: Test connection
```bash
ssh -T git@github.com
# Should say: "Hi ryandakine! You've successfully authenticated..."
```

## Option 2: Personal Access Token (Quick HTTPS fix)

### Step 1: Create Personal Access Token
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name it (e.g., "Laptop Access")
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

### Step 2: Use token when pushing
When you push, use the token as your password:
```bash
git push
Username: ryandakine
Password: [paste your token here]
```

### Step 3: Store credentials (optional, saves from entering each time)
```bash
git config --global credential.helper store
# Next time you push, enter token, it will be saved
```

## Quick Setup Script (SSH Keys)

Run this to set up SSH keys automatically:

```bash
# Check if key exists
if [ ! -f ~/.ssh/id_ed25519.pub ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -C "ryan@example.com" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH key generated!"
else
    echo "✅ SSH key already exists"
fi

# Display public key (copy this to GitHub)
echo ""
echo "📋 Copy this public key and add it to GitHub:"
echo "   GitHub.com → Settings → SSH and GPG keys → New SSH key"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""
echo "After adding to GitHub, run:"
echo "  git remote set-url origin git@github.com:ryandakine/MultiSportsBettingPlatform.git"
```

## After Setup - Push Your Code

```bash
cd /home/ryan/MultiSportsBettingPlatform

# Add all changes
git add .

# Commit (adjust message as needed)
git commit -m "Add automated betting system with daily predictions and bet settlement"

# Push
git push
```

## For Your Laptop

1. Generate SSH key on laptop (same process)
2. Add SSH key to GitHub
3. Clone the repo: `git clone git@github.com:ryandakine/MultiSportsBettingPlatform.git`
4. Or if already cloned with HTTPS, change remote: `git remote set-url origin git@github.com:ryandakine/MultiSportsBettingPlatform.git`

