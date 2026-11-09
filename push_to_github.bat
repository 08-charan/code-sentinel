@echo off
echo ========================================================
echo  CodeSentinel - Pushing to GitHub (github.com/08-charan)
echo ========================================================

git remote set-url origin https://github.com/08-charan/code-sentinel.git
git branch -M main

echo.
echo Step 1: Checking if remote repo exists or creating via gh CLI...
where gh >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    gh repo create 08-charan/code-sentinel --public --source=. --remote=origin --push 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Repository created and pushed via GitHub CLI!
        goto :done
    )
)

echo.
echo Step 2: Pushing directly with git push...
git push -u origin main
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code pushed successfully to https://github.com/08-charan/code-sentinel !
) else (
    echo.
    echo [NOTE] If you saw an authentication prompt or permission error:
    echo 1. Ensure you have created the repository 'code-sentinel' on https://github.com/new
    echo 2. Or run: gh auth login
    echo 3. Then rerun this script or run: git push -u origin main
)

:done
pause
