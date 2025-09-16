@echo off
echo PDF Watermark Remover - Setup
echo =============================
echo.
echo Installing required dependencies...
echo.

pip install -r requirements.txt

echo.
echo Installing Poppler for PDF processing...
winget install poppler

echo.
echo Setup complete! You can now run the application.
echo.
echo To start the application:
echo 1. Double-click "run_pdf_remover.bat"
echo 2. Or run: python main.py
echo.
pause
