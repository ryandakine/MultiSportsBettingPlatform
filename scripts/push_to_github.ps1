# PowerShell script to push MultiSportsBettingPlatform to GitHub
Write-Host "Setting up MultiSportsBettingPlatform for GitHub..." -ForegroundColor Green

# Configure Git
git config user.name "ryandakine"
git config user.email "himselfjesus710@gmail.com"

# Add all files (excluding those in .gitignore)
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Initial commit: MultiSportsBettingPlatform with Advanced AI Features V4"

# Add remote
Write-Host "Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin https://github.com/ryandakine/MultiSportsBettingPlatform.git

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin master

Write-Host "Done! Your repository is now on GitHub!" -ForegroundColor Green
Write-Host "Visit: https://github.com/ryandakine/MultiSportsBettingPlatform" -ForegroundColor Cyan 