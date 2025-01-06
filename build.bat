@echo off
:: Setting up colors for the output
set "COLOR_SUCCESS=0A"
set "COLOR_ERROR=0C"
set "COLOR_INFO=0E"

:: Change console color for the script
color 0E

:: Title for the batch file
title Build Script - EngageX Project

:: Display banner
echo.
echo ============================================================
echo            EngageX Build Script - by Raghav
echo ============================================================
echo.

:: Cleaning up old build files
echo.
echo Cleaning up old build files...
echo.

:: Delete the main.spec file if it exists
if exist main.spec (
    del /f main.spec
    echo [INFO] Removed main.spec
) else (
    echo [INFO] No main.spec file to delete
)

:: Delete the build directory if it exists
if exist build (
    rmdir /s /q build
    echo [INFO] Removed build directory
) else (
    echo [INFO] No build directory to delete
)

:: Delete the dist/main.exe file if it exists
if exist dist\main.exe (
    del /f dist\main.exe
    echo [INFO] Removed dist\main.exe
) else (
    echo [INFO] No main.exe file to delete
)

:: Build the project
echo.
echo Building the project...
pyinstaller --hidden-import "pyrogram" --onefile --console "main.py"

:: Check if the build succeeded
if exist dist\main.exe (
    echo.
    color %COLOR_SUCCESS%
    echo ============================================================
    echo            Build Completed Successfully!
    echo ============================================================
    echo [SUCCESS] Your executable is ready at dist\main.exe
) else (
    echo.
    color %COLOR_ERROR%
    echo ============================================================
    echo            Build Failed!
    echo ============================================================
    echo [ERROR] Please check the output for errors.
)

:: Pause to review output
echo.
color 07
pause
