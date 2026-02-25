@echo off
title Push to GitHub - Telegram Bot
color 0A

echo.
echo ========================================
echo   PUSHING BOT TO GITHUB + RAILWAY
echo ========================================
echo.

cd /d "C:\telegram-audio-bot"

echo [1/5] Staging ALL changes (including cleanup of old files)...
git add -A
echo Done staging.
echo.

echo [2/5] Committing...
for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set TODAY=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ("%time%") do set NOW=%%a:%%b
git commit -m "Update bot - %TODAY% %NOW%"
echo (If it says "nothing to commit" that is OK)
echo.

echo [3/5] Pulling latest from GitHub first...
git pull origin main --rebase
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo   PULL FAILED. Trying merge strategy instead...
    color 0A
    git pull origin main
    if %ERRORLEVEL% NEQ 0 (
        color 0C
        echo   STILL FAILED. See error above.
        pause
        exit /b 1
    )
)
echo Pull done.
echo.

echo [4/5] Pushing to GitHub...
git push origin main
echo.

echo [5/5] Done!
echo ========================================
if %ERRORLEVEL% EQU 0 (
    color 0A
    echo   SUCCESS! Railway will auto-deploy now.
    echo   Check: https://railway.app/dashboard
) else (
    color 0C
    echo   Something went wrong. See error above.
)
echo ========================================
echo.
pause
