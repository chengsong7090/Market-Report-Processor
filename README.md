# GTJA Report Processor

A comprehensive GUI application designed for processing PDF reports at GTJA (Guotai Junan Securities). This application provides automated watermark removal, AI-powered summarization, and email distribution capabilities.

## Features

- **PDF Watermark Removal**: Automatically removes watermarks from PDF documents
- **AI-Powered Summarization**: Uses Google Gemini AI to generate intelligent summaries in Chinese
- **Email Distribution**: Sends processed PDFs with formatted summaries via email
- **Lotus Notes Compatibility**: Email formatting optimized for Lotus Notes email clients
- **User-Friendly GUI**: Simple interface for easy operation

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gtja-report-processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select a PDF file to process
3. Specify the watermark text (default: "For the exclusive use of DAPHNE.WOO@GTJAS.COM.HK")
4. Choose output location
5. Optionally enable AI summarization
6. Enter recipient email address (default: charles.song@gtjas.com.hk)
7. Click "Process PDF"

## Features in Detail

### Watermark Removal
- Supports both direct PDF text removal and image-based removal
- Handles various watermark formats and positions
- Preserves original document formatting

### AI Summarization
- Uses Google Gemini AI for intelligent content analysis
- Generates structured summaries with key points, financial data, insights, and risks
- Outputs in Chinese for local business needs
- Fallback to local analysis if AI service unavailable

### Email Distribution
- Sends processed PDFs as attachments
- Includes formatted HTML summaries
- Optimized for Lotus Notes compatibility
- Professional business formatting

## Configuration

### Email Settings
The application uses Gmail SMTP for email delivery. Email credentials are configured in `src/email_sender.py`.

### AI API
Google Gemini API key is configured in `src/llm_summarizer.py`.

## File Structure

```
gtja-report-processor/
├── main.py                 # Main GUI application
├── src/
│   ├── pdf_processor.py    # PDF processing logic
│   ├── llm_summarizer.py   # AI summarization
│   └── email_sender.py     # Email functionality
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

- `tkinter` - GUI framework
- `PyMuPDF` - PDF processing
- `google-generativeai` - AI summarization
- `smtplib` - Email functionality
- `Pillow` - Image processing
- `OpenCV` - Advanced image operations

## License

This project is proprietary software developed for GTJA internal use.

## Support

For technical support or questions, please contact the development team.