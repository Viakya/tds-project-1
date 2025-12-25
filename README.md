# TDS Project 1 - AI-Powered GitHub Repository Generator

An AI-powered FastAPI service that automatically generates web applications using OpenAI's GPT models and deploys them to GitHub repositories with GitHub Pages enabled. The service receives problem briefs, generates complete web applications with code and documentation, commits them to GitHub, and notifies an evaluation server.

## Table of Contents
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [File Structure](#file-structure)
- [Environment Variables](#environment-variables)
- [Installation & Setup](#installation--setup)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Workflow](#workflow)
- [Code Generation Process](#code-generation-process)
- [Testing](#testing)
- [Features](#features)
- [Deployment](#deployment)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [License](#license)
- [Contributing](#contributing)
- [Future Enhancements](#future-enhancements)

## Key Features

### Core Functionality
1. **FastAPI Web Service**
   - RESTful API endpoint `/problem-pipeline` for receiving generation requests
   - Background task processing for non-blocking operations
   - Request deduplication and persistence
   - Keep-alive `/ping` endpoint for server uptime

2. **AI-Powered Code Generation**
   - Uses OpenAI GPT-5 API to generate complete web applications
   - Supports attachments (CSV, images, text files) via base64 encoding
   - Two-round workflow: initial generation and revision
   - Automatic README.md generation for each project
   - Fallback HTML generation if OpenAI API fails

3. **GitHub Integration**
   - Automatic repository creation via PyGithub
   - File and binary file commits (text, images, CSV)
   - GitHub Pages enablement via REST API
   - MIT License generation
   - Support for both text and binary attachments

4. **Request Processing**
   - Secret-based authentication
   - Round-based workflow (Round 1: fresh build, Round 2: revision)
   - Previous README context loading for Round 2
   - Duplicate request detection
   - 120-second deployment wait for GitHub Pages

5. **Notification System**
   - Callback to evaluation server with repo details
   - Exponential backoff retry logic (up to 5 attempts)
   - Payload includes: repo URL, commit SHA, Pages URL, task details

## Technology Stack
- **Backend Framework**: FastAPI 0.118.0
- **Web Server**: Uvicorn 0.37.0
- **AI/ML**: OpenAI API 1.109.1 (GPT-5 model)
- **GitHub API**: PyGithub 2.8.1
- **HTTP Client**: httpx 0.28.1
- **Environment**: python-dotenv 1.1.1
- **Validation**: Pydantic 2.11.9
- **Python Runtime**: Python 3.x

## File Structure
```
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application & endpoints
│   ├── llm_generator.py         # OpenAI integration & code generation
│   ├── github_utils.py          # GitHub API utilities
│   ├── notify.py                # Evaluation server notification
│   └── signature.py             # (Empty - future use)
├── test_github.py               # GitHub & OpenAI API testing script
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Python version specification
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```

## Environment Variables
Required in `.env` file:
- `GITHUB_TOKEN`: GitHub Personal Access Token with repo permissions
- `GITHUB_USERNAME`: GitHub username for repository creation
- `OPENAI_API_KEY`: OpenAI API key for GPT-5 access
- `USER_SECRET`: Secret key for request authentication

## Installation & Setup
```bash
# 1. Clone repository
git clone https://github.com/Viakya/tds-project-1.git
cd tds-project-1

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Test API connections
python test_github.py
```

## Running the Service
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/problem-pipeline`
Receives project generation requests and processes them in the background.

**Request Body:**
```json
{
  "secret": "your_secret_key",
  "email": "user@example.com",
  "task": "task-name",
  "round": 1,
  "nonce": "unique-nonce",
  "brief": "Create a todo list app with local storage",
  "checks": ["Must have add/delete functionality", "Must persist data"],
  "attachments": [
    {
      "name": "data.csv",
      "url": "data:text/csv;base64,<base64_encoded_content>"
    }
  ],
  "evaluation_url": "https://eval-server.com/callback"
}
```

**Response:**
```json
{
  "status": "accepted",
  "note": "processing round 1 started"
}
```

### GET `/ping`
Keep-alive endpoint for server monitoring.

**Response:** `"ok"`

## Workflow

### Round 1: Initial Generation
1. Receive request via API endpoint
2. Decode and save attachments to `/tmp/llm_attachments/`
3. Generate web application code using OpenAI GPT-5
4. Create GitHub repository (or use existing)
5. Commit generated files (index.html, README.md)
6. Commit attachments (text and binary files)
7. Add MIT License
8. Enable GitHub Pages
9. Wait 120 seconds for Pages deployment
10. Notify evaluation server with repository details

### Round 2: Revision
1. Receive revision request
2. Load previous README.md from repository
3. Generate revised code with context from Round 1
4. Update existing files in repository
5. Re-enable GitHub Pages (if needed)
6. Notify evaluation server

## Code Generation Process
- **Input**: Project brief, attachments, evaluation checks
- **Processing**: OpenAI GPT-5 generates complete HTML/CSS/JS application
- **Output Format**: `index.html` and `README.md` separated by `---README.md---`
- **Fallback**: If OpenAI fails, generates simple fallback HTML

## Testing
Run the test script to verify GitHub and OpenAI authentication:
```bash
python test_github.py
```

Expected output:
- GitHub authentication status
- List of first 5 repositories
- OpenAI authentication status
- Available AI models

## Features
✅ AI-powered web app generation  
✅ Automatic GitHub repository creation  
✅ GitHub Pages deployment  
✅ Multi-round iterative development  
✅ Binary file support (images, PDFs)  
✅ Attachment handling (CSV, JSON, images)  
✅ Duplicate request prevention  
✅ Automatic documentation generation  
✅ MIT License auto-generation  
✅ Evaluation server integration  
✅ Retry logic with exponential backoff  

## Deployment
This service can be deployed on platforms like:
- Render.com
- Heroku
- Railway
- AWS EC2
- Google Cloud Run

Set environment variables on your hosting platform and ensure the `/tmp` directory is writable.

## Error Handling
- Invalid secret: Returns `{"error": "Invalid secret"}`
- Duplicate requests: Re-notifies evaluation server with previous payload
- OpenAI API failures: Falls back to simple HTML template
- GitHub API failures: Logged with detailed error messages
- Evaluation server failures: Retries up to 5 times with exponential backoff

## Security Considerations
- Secret-based authentication required
- Environment variables for sensitive credentials
- GitHub token with minimal required permissions
- Request deduplication prevents replay attacks

## License
This project automatically generates MIT licenses for created repositories.

## Contributing
Contributions welcome! Please ensure:
- Code follows Python PEP 8 style guide
- All API endpoints are documented
- Environment variables are documented in `.env.example`

## Future Enhancements
- Support for more programming languages/frameworks
- Multi-file project generation
- Custom templates
- Database integration
- User authentication system
- Web UI for request submission
