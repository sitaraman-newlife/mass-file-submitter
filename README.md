# Mass File Submitter

**Professional Python Desktop Application for Bulk File Submission with Advanced Features**

Submit multiple files to multiple destinations simultaneously with intelligent retry logic, anti-throttling protection, and secure credential management. A production-ready GUI tool built with Python and Tkinter.

## Features

### Core Functionality
- ✅ **Bulk File Submission**: Submit multiple files to multiple endpoints simultaneously
- ✅ **Multi-Credential Support**: Add and manage multiple user credentials with automatic cycling
- ✅ **Secure Credential Storage**: Credentials encrypted using Fernet encryption algorithm
- ✅ **Smart Retry Logic**: Configurable automatic retries (1-10 attempts per file)
- ✅ **Anti-Throttling**: Customizable delays between submissions (1-30 seconds)
- ✅ **Progress Tracking**: Real-time progress bar with detailed status updates
- ✅ **Comprehensive Logging**: Detailed output log showing success/failure for each submission
- ✅ **Custom Headers**: Support for custom HTTP headers in JSON format
- ✅ **Real-time Status**: Last file status indicator with visual feedback (✓/✗)

### User Interface
- 🎨 **Modern GUI**: Professional Tkinter interface with improved layout (1200x700)
- 🎨 **Scrollable Interface**: Smooth vertical scrolling with mousewheel support
- 🎨 **Wide Input Fields**: 70-character wide entry fields for better usability
- 🎨 **Improved Spacing**: 15px padding for better visual organization
- 🎨 **Responsive Design**: Works seamlessly on modern displays
- 🎨 **Clear Visual Feedback**: Color-coded success/failure indicators

### Technical Features
- 🔒 **Multi-threaded**: Non-blocking UI during submissions
- 🔒 **Cross-platform**: Works on Windows, macOS, and Linux
- 🔒 **Error Handling**: Graceful handling of network failures and timeouts
- 🔒 **Session Management**: Remembers settings between sessions
- 🔒 **Configurable**: Easy to customize timeouts, retries, and delays

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package manager)
- 50 MB disk space

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

### Getting Started

1. **Add Credentials**
   - Enter URL, Username, Password in the Credentials section
   - Optionally add custom headers (JSON format)
   - Click "Add Credential" to add to the list
   - Use "Save Credentials" to securely store for future use

2. **Select Files**
   - Click "Select Files" to choose files for submission
   - Multiple files can be selected at once
   - Currently supports any file type

3. **Configure Settings** (Optional)
   - Set delay between submissions (default: 2 seconds)
   - Set max retries per file (default: 3 attempts)
   - Click "Set" to apply changes

4. **Submit Files**
   - Click "Start Submission" to begin batch submission
   - Monitor progress with the progress bar
   - View real-time logs in the output window
   - Submit button disables during submission process

### Example Workflow

```
1. Add credentials for your destination servers
2. Select 10-100 files to submit
3. Configure retry and delay settings
4. Click "Start Submission"
5. Watch the progress bar and output log
6. All files will be submitted to all credential endpoints
```

## Project Structure

```
mass-file-submitter/
├── main.py              # Main application (298 lines)
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── LICENSE             # MIT License
```

## Technical Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.7+ |
| **GUI Framework** | Tkinter (Python built-in) |
| **HTTP Requests** | requests library |
| **Security** | cryptography (Fernet) |
| **Threading** | Python threading module |
| **File I/O** | pathlib & json |

## Version History

### v1.2 (Current - November 2025)
✨ **Latest Release**
- ✅ Improved UI layout (1200x700 window size)
- ✅ Scrollable interface with mousewheel support
- ✅ Wider input fields (70 characters)
- ✅ Better spacing and padding (15px)
- ✅ Enhanced visual feedback
- ✅ Code optimization and cleanup

### v1.1 (Previous)
- ✅ Added scrollbar functionality
- ✅ Canvas-based scrollable frame
- ✅ Mousewheel scrolling support

### v1.0 (Initial Release)
- ✅ Basic GUI interface
- ✅ Credential management
- ✅ File selection and submission
- ✅ Progress tracking
- ✅ Retry logic

## Configuration

### Default Settings
- Window Size: 1200x700 pixels
- Entry Field Width: 70 characters
- Default Delay: 2 seconds between submissions
- Default Retries: 3 attempts per file
- Frame Padding: 15 pixels
- Timeout: 30 seconds per request

### Customizable Parameters
```python
self.delay_seconds = 2      # Delay between submissions
self.max_retries = 3        # Maximum retry attempts
self.root.geometry("1200x700")  # Window dimensions
```

## Security Notes

⚠️ **Important Security Information:**

1. **Credential Encryption**: Credentials are encrypted using Fernet (AES-128)
2. **Local Storage Only**: All data stored locally on your machine
3. **No Cloud Sync**: No automatic backup or cloud synchronization
4. **File Permissions**: Keep your `key.key` and `credentials.dat` files secure
5. **SSL/TLS**: Supports HTTPS endpoints with standard SSL verification
6. **Custom Headers**: Can include authentication tokens in headers

### Best Practices
- Store key.key file securely
- Don't share credentials.dat file
- Use HTTPS endpoints when possible
- Test with small file batches first
- Verify destination URLs before bulk submission

## Performance

- **File Processing**: 50-100+ files per batch
- **Concurrent Requests**: Sequential with configurable delays
- **Memory Usage**: Minimal (~50-100 MB)
- **CPU Usage**: Low (<5% during idle)
- **Network**: Optimized for HTTP/HTTPS

## Troubleshooting

### Common Issues

**Issue**: "No credentials added" error
- **Solution**: Add at least one credential before submitting

**Issue**: "No files selected" error
- **Solution**: Click "Select Files" and choose at least one file

**Issue**: Submissions timeout
- **Solution**: Increase delay between submissions or check network connectivity

**Issue**: Failed retries continue
- **Solution**: Verify destination URL, credentials, and network access

**Issue**: Scrollbar not visible
- **Solution**: Maximize window or resize to see scrollbar

## Development Status

**Current Status**: ✅ **Production Ready**

- [x] Core functionality implemented
- [x] GUI improvements completed
- [x] Scrollable interface
- [x] Secure credential storage
- [x] Comprehensive logging
- [x] Error handling
- [x] Cross-platform support
- [ ] Command-line interface (planned)
- [ ] Executable packaging (planned)
- [ ] Web-based interface (planned)

## Contributing

Contributions are welcome! This is an active development project.

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

You are free to use, modify, and distribute this software commercially or personally.

## Support

- 📧 **Email**: sitaraman-newlife@example.com
- 🐛 **Issue Tracker**: GitHub Issues
- 📚 **Documentation**: This README file
- 🔄 **Updates**: Check GitHub for latest version

## Author

**Sitaramudu Eediga**
- Role: Python Developer | ERP Specialist
- Expertise: Python Automation, Desktop Applications, System Integration
- GitHub: [@sitaraman-newlife](https://github.com/sitaraman-newlife)

**Last Updated**: November 12, 2025
**Status**: Active Development | Maintained

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

**Made with ❤️ by Sitaramudu Eediga**
