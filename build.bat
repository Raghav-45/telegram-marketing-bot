@echo off
echo Cleaning up old build files...

:: Delete the main.spec file if it exists
if exist main.spec del /f main.spec

:: Delete the build directory if it exists
if exist build rmdir /s /q build

:: Delete the dist/main.exe file if it exists
if exist dist\main.exe del /f dist\main.exe

echo Building the project...

:: Run the PyInstaller command
pyinstaller --hidden-import "pyrogram" --onefile --console "main.py"

echo Build process complete!
pause
