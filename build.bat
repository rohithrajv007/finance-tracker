@echo off
echo ============================================
echo   Finance Tracker - Building .exe
echo ============================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo.
echo Running PyInstaller...
pyinstaller finance_tracker.spec --clean

echo.
if exist dist\FinanceTracker\FinanceTracker.exe (
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo   Location: dist\FinanceTracker\
    echo ============================================
) else (
    echo ============================================
    echo   BUILD FAILED - check errors above
    echo ============================================
)
pause