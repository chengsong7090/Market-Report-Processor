@echo off
echo Building Small PDF Watermark Remover Executable...
echo ==================================================
echo.

echo Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo Building optimized executable...
pyinstaller --onefile ^
    --windowed ^
    --name "PDF_Watermark_Remover" ^
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
    --exclude-module urllib ^
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
    --strip ^
    --upx-dir "C:\Program Files\UPX" ^
    main.py

echo.
if exist "dist\PDF_Watermark_Remover.exe" (
    echo ✅ Build successful!
    echo.
    echo Executable created: dist\PDF_Watermark_Remover.exe
    echo.
    for %%I in ("dist\PDF_Watermark_Remover.exe") do echo File size: %%~zI bytes
    echo.
    echo The executable should now be much smaller!
) else (
    echo ❌ Build failed! Check the output above for errors.
)

echo.
pause
