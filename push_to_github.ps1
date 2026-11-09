Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " CodeSentinel - Pushing to GitHub (github.com/08-charan) " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

git remote set-url origin https://github.com/08-charan/code-sentinel.git
git branch -M main

# Try GitHub CLI first
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "`nAttempting to create and push via GitHub CLI..." -ForegroundColor Yellow
    gh repo create 08-charan/code-sentinel --public --source=. --remote=origin --push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] Repository created and pushed via gh CLI!" -ForegroundColor Green
        exit 0
    }
}

# Standard git push
Write-Host "`nPushing directly via git push..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Code pushed successfully to https://github.com/08-charan/code-sentinel !" -ForegroundColor Green
} else {
    Write-Host "`n[ACTION REQUIRED] To complete GitHub push:" -ForegroundColor Yellow
    Write-Host "1. Create repository 'code-sentinel' at: https://github.com/new"
    Write-Host "2. Or authenticate GitHub CLI: gh auth login"
    Write-Host "3. Run: git push -u origin main"
}
