@echo off
echo Building Small PDF Watermark Remover...
echo ======================================
echo.

echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Building ultra-small executable (PyMuPDF only)...
pyinstaller --onefile ^
    --windowed ^
    --name "PDF_Watermark_Remover_Small" ^
    --exclude-module matplotlib ^
    --exclude-module pandas ^
    --exclude-module scipy ^
    --exclude-module sklearn ^
    --exclude-module tensorflow ^
    --exclude-module torch ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module IPython ^
    --exclude-module pytest ^
    --exclude-module sphinx ^
    --exclude-module setuptools ^
    --exclude-module distutils ^
    --exclude-module email ^
    --exclude-module http ^
    --exclude-module xml ^
    --exclude-module multiprocessing ^
    --exclude-module concurrent ^
    --exclude-module asyncio ^
    --exclude-module unittest ^
    --exclude-module doctest ^
    --exclude-module pdb ^
    --exclude-module profile ^
    --exclude-module pstats ^
    --exclude-module cProfile ^
    --exclude-module trace ^
    --exclude-module pydoc ^
    --exclude-module difflib ^
    --exclude-module test ^
    --exclude-module tests ^
    --exclude-module testing ^
    --exclude-module cv2 ^
    --exclude-module opencv ^
    --exclude-module numpy ^
    --exclude-module PIL ^
    --exclude-module Pillow ^
    --exclude-module pdf2image ^
    --exclude-module PyPDF2 ^
    --exclude-module pathlib2 ^
    --strip ^
    main_small.py

echo.
if exist "dist\PDF_Watermark_Remover_Small.exe" (
    echo ✅ Build successful!
    echo.
    echo Executable created: dist\PDF_Watermark_Remover_Small.exe
    echo.
    for %%I in ("dist\PDF_Watermark_Remover_Small.exe") do (
        set /a size=%%~zI/1024/1024
        echo File size: !size! MB
    )
    echo.
    echo This version is much smaller as it only uses PyMuPDF!
    echo It can only remove text-based watermarks, not image watermarks.
    echo.
    echo You can now distribute this small .exe file to other users.
) else (
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause
