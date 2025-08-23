@echo off
echo Setting up SportsBet Pro with Kendo React UI
echo ==============================================

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js >= 16.0.0
    pause
    exit /b 1
)

echo Node.js check passed

:: Install dependencies
echo Installing dependencies...
call npm install

if %errorlevel% equ 0 (
    echo Dependencies installed successfully
) else (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo To start the development server:
echo   npm start
echo.
echo To build for production:
echo   npm run build
echo.
echo Happy coding!
pause