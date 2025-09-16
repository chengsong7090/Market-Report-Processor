@echo off
echo Building PDF Watermark Remover Executable...
echo ============================================
echo.

echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Building executable with PyInstaller...
pyinstaller pdf_remover.spec

echo.
if exist "dist\PDF_Watermark_Remover.exe" (
    echo ✅ Build successful!
    echo.
    echo Executable created: dist\PDF_Watermark_Remover.exe
    echo.
    echo You can now distribute this single .exe file to other users.
    echo They just need to double-click it to run the application.
    echo.
    echo Note: The executable is quite large (~200MB) because it includes
    echo all the required libraries (OpenCV, PyMuPDF, etc.)
) else (
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause
