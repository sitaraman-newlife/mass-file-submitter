# Mass File Submission Tool

Submit text and PDF files to 100-200 destinations simultaneously. Python desktop app for bulk posting with anti-throttling and secure credential storage.

## Features

- Submit text and PDF files in bulk
- Handle 100-200 destinations per batch
- CSV import for destination URLs  
- Progress tracking with visual indicators
- Multi-threaded concurrent uploads
- Simple and intuitive GUI
- Cross-platform (Windows/Mac/Linux)

## Installation

### Requirements
- Python 3.8+
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/sitaraman-newlife/mass-file-submitter.git
cd mass-file-submitter

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Usage

1. **Add Files**: Click "Add Files" to select text/PDF files
2. **Load URLs**: Click "Load URLs from CSV" to import destination URLs
3. **Submit**: Click "SUBMIT ALL FILES" to start batch submission
4. **Track Progress**: Monitor progress bar and status messages

### CSV Format

Create a CSV file with one URL per line:
```
https://example1.com/submit
https://example2.com/upload  
https://example3.com/post
```

## Project Structure

```
mass-file-submitter/
├── main.py              # Main GUI application
├── requirements.txt     # Python dependencies
├── README.md           # Documentation
└── .gitignore          # Git ignore rules
```

## Development Status

**Current Version**: v1.0 (MVP)

### Completed
- Basic GUI interface
- File selection (text/PDF)
- CSV URL import
- Progress tracking
- Batch submission simulation

### Roadmap
- Multi-threaded HTTP requests
- Anti-throttling mechanisms
- Secure credential storage
- Retry logic for failed submissions
- Detailed logging
- Executable packaging

## Technical Stack

- **Language**: Python 3.x
- **GUI**: Tkinter
- **HTTP**: requests/aiohttp
- **Security**: cryptography

## Contributing

Contributions welcome! This is an active development project.

## License

MIT License

## Contact

Developed by **Eediga Sitaramudu**  
ERP Developer | Python Automation Specialist

---

**Status**: Active Development | **Last Updated**: November 2025
