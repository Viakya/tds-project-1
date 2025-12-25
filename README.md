# TDS Project 1 - AI-Powered Web App Generator

An intelligent FastAPI-based automation system that generates complete web applications using OpenAI's GPT models and automatically deploys them to GitHub repositories with GitHub Pages enabled. Designed for multi-round iterative development with comprehensive attachment support.

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [File Structure](#file-structure)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Deployment](#deployment)
- [Security Notes](#security-notes)
- [Error Handling](#error-handling)
- [Limitations & Future Improvements](#limitations--future-improvements)
- [License](#license)
- [Contributing](#contributing)

## Project Overview

This is a FastAPI-based automation system that generates web applications using OpenAI's GPT models and automatically deploys them to GitHub repositories with GitHub Pages enabled. It's designed to handle multi-round iterative development with attachment support.

The system receives project briefs via API, generates complete web applications using AI, manages the entire GitHub workflow (repository creation, file commits, Pages deployment), and notifies evaluation servers upon completion.

## Key Features

### 1. AI-Powered Code Generation
- **OpenAI Integration**: Uses OpenAI's GPT-5 Responses API to generate complete web applications
- **Dual Output**: Generates both functional code (`index.html`) and comprehensive documentation (`README.md`)
- **Iterative Development**: Supports multi-round improvements with context awareness
- **Fallback Mechanism**: Automatically falls back to simple HTML template if OpenAI API fails
- **Smart Code Parsing**: Strips code block markers and formats output appropriately

### 2. GitHub Integration
- **Automatic Repository Management**: Creates new repositories or reuses existing ones
- **File Operations**: Handles creation and updates for both text and binary files
- **GitHub Pages Deployment**: Automatic deployment automation with proper configuration
- **License Generation**: Automatically generates and commits MIT License
- **Commit Tracking**: Tracks and manages commit SHAs for verification
- **Branch Management**: Works with main branch by default

### 3. Multi-Round Development
- **Round 1**: Build from scratch based on initial brief
  - Fresh repository creation with all files
  - Initial GitHub Pages setup
  - Complete project scaffolding
- **Round 2**: Revise and improve based on previous work
  - Loads previous README for context-aware improvements
  - Updates existing repository
  - Reuses GitHub Pages configuration
  - Iterative enhancements based on new requirements

### 4. Attachment Handling
- **Format Support**: Decodes base64-encoded attachments (CSV, images, JSON, and more)
- **Temporary Storage**: Saves attachments to `/tmp/llm_attachments/` for processing
- **Repository Commits**: Commits both text and binary files to repository
- **Binary Backups**: Creates base64 backup versions for binary files in `attachments/` directory
- **Metadata Summarization**: Generates attachment summaries for LLM context
- **Preview Generation**: Creates content previews for text files to enhance AI understanding

### 5. Asynchronous Processing
- **Non-Blocking Architecture**: FastAPI background tasks for async request handling
- **Immediate Acknowledgment**: Returns HTTP 200 response immediately
- **Background Execution**: Long-running tasks processed without blocking API
- **Duplicate Detection**: Tracks processed requests to prevent redundant work
- **Re-notification Support**: Handles duplicate requests by re-notifying evaluation server

### 6. Evaluation Server Integration
- **Automatic Notification**: Sends completion notifications to evaluation server
- **Retry Mechanism**: Implements exponential backoff with up to 5 retry attempts
- **Complete Payload**: Includes repository URL, commit SHA, and GitHub Pages URL
- **Deployment Wait**: 120-second wait time to ensure GitHub Pages is fully deployed
- **Error Resilience**: Continues operation even if notification fails

### 7. Request Persistence
- **JSON-Based Storage**: Tracks processed requests in `/tmp/processed_requests.json`
- **Duplicate Prevention**: Prevents processing the same request multiple times
- **Re-notification Support**: Allows re-sending notifications for duplicate requests
- **Unique Keys**: Uses composite key: `email::task::round::nonce` for tracking

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.118.0 |
| **ASGI Server** | Uvicorn | 0.37.0 |
| **GitHub API** | PyGithub | 2.8.1 |
| **AI/LLM** | OpenAI API | 1.109.1 |
| **HTTP Client** | httpx | 0.28.1 |
| **Environment Management** | python-dotenv | 1.1.1 |
| **Python Runtime** | Python | 3.12.3 |

## File Structure

```
tds-project-1/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application & endpoints
│   ├── github_utils.py          # GitHub API operations (repo, files, Pages)
│   ├── llm_generator.py         # OpenAI integration & code generation
│   ├── notify.py                # Evaluation server notification with retries
│   └── signature.py             # Placeholder for future signature validation
├── test_github.py               # GitHub & OpenAI API connection tests
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Python version specification (3.12.3)
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules (Python cache, .env, venv)
└── README.md                    # This file - comprehensive documentation
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username_here

# User Authentication
USER_SECRET=your_secret_for_request_validation_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

### Variable Details:
- **GITHUB_TOKEN**: Personal Access Token with `repo` and `admin:repo_hook` permissions
- **GITHUB_USERNAME**: Your GitHub username (used for repository creation and Pages URLs)
- **USER_SECRET**: Secret key for validating incoming API requests (acts as authentication)
- **OPENAI_API_KEY**: OpenAI API key with access to GPT models

**Note**: Copy `.env.example` to `.env` and replace placeholder values with your actual credentials. Never commit `.env` to version control.

## API Endpoints

### `POST /problem-pipeline`
Main endpoint for receiving application generation requests.

**Description**: Accepts project briefs, validates credentials, and triggers asynchronous web application generation with GitHub deployment.

**Request Body**:
```json
{
  "secret": "your_user_secret",
  "email": "user@example.com",
  "task": "my-todo-app",
  "round": 1,
  "nonce": "unique-request-identifier-12345",
  "brief": "Create a responsive todo application with local storage persistence",
  "checks": [
    "Must have responsive design",
    "Must use vanilla JavaScript (no frameworks)",
    "Must persist data in localStorage"
  ],
  "attachments": [
    {
      "name": "data.csv",
      "url": "data:text/csv;base64,bmFtZSxhZ2UKSm9obiwzMA=="
    },
    {
      "name": "logo.png",
      "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
    }
  ],
  "evaluation_url": "https://eval-server.example.com/submit"
}
```

**Request Fields**:
- `secret` (required): User secret for authentication
- `email` (required): User email identifier
- `task` (required): Repository name to create
- `round` (required): Development round (1 = new project, 2 = revision)
- `nonce` (required): Unique request identifier for deduplication
- `brief` (required): Project description and requirements
- `checks` (optional): List of evaluation criteria
- `attachments` (optional): Array of base64-encoded files
- `evaluation_url` (required): Callback URL for completion notification

**Response** (Success - 200 OK):
```json
{
  "status": "accepted",
  "note": "processing round 1 started"
}
```

**Response** (Duplicate Request - 200 OK):
```json
{
  "status": "ok",
  "note": "duplicate handled & re-notified"
}
```

**Response** (Authentication Error):
```json
{
  "error": "Invalid secret"
}
```

### `GET /ping`
Keep-alive endpoint for monitoring and preventing service sleep on platforms like Render.

**Query Parameters**:
- `q` (optional): Timestamp or identifier for logging purposes

**Response**: `"ok"`

**Example**:
```bash
curl "http://localhost:8000/ping?q=2024-01-15T10:30:00Z"
```

## Installation & Setup

### Prerequisites
- **Python**: 3.10 or higher (3.12.3 recommended)
- **GitHub Account**: With ability to create Personal Access Tokens
- **GitHub Personal Access Token**: With `repo` and `admin:repo_hook` permissions
- **OpenAI Account**: With valid API key and access to GPT models

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/Viakya/tds-project-1.git
cd tds-project-1
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

5. **Test GitHub and OpenAI connections**
```bash
python test_github.py
```

**Expected output**:
```
👤 GitHub Authenticated as: your_username

📂 Your first 5 GitHub repos:
- repo1
- repo2
...

✅ OpenAI Authenticated. Available models:
- gpt-4
- gpt-3.5-turbo
...
```

## Running the Application

### Development Mode
Start the server with auto-reload enabled (recommended for development):

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Production Mode
Start the server for production use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing the API
You can test the API using curl or any HTTP client:

```bash
# Example: Send a test request
curl -X POST http://127.0.0.1:8000/problem-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "your_secret_here",
    "email": "test@example.com",
    "task": "test-app",
    "round": 1,
    "nonce": "test-12345",
    "brief": "Create a simple hello world page",
    "checks": ["Must display Hello World"],
    "evaluation_url": "http://localhost:8000/ping"
  }'
```

## How It Works

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Request Received                                             │
│    ├─ POST /problem-pipeline                                    │
│    ├─ Secret validation                                         │
│    └─ Duplicate check against processed requests               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Background Task Started                                      │
│    ├─ Immediate HTTP 200 response                              │
│    └─ Async processing begins                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Attachments Processing                                       │
│    ├─ Decode base64 attachments                                │
│    ├─ Save to /tmp/llm_attachments/                            │
│    └─ Generate metadata summaries                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. AI Code Generation                                           │
│    ├─ Call OpenAI GPT-5 Responses API                          │
│    ├─ Include brief, checks, and attachment context            │
│    ├─ Parse response (index.html + README.md)                  │
│    └─ Fallback to simple template if API fails                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. GitHub Repository Setup                                      │
│    ├─ Create new repo or reuse existing                        │
│    └─ Repository configured as public                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. Files Committed                                              │
│    ├─ index.html (generated code)                              │
│    ├─ README.md (generated docs)                               │
│    ├─ Attachments (text and binary)                            │
│    ├─ Binary backups (.b64 files)                              │
│    └─ LICENSE (MIT)                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. GitHub Pages Setup                                           │
│    ├─ Enable Pages (Round 1) or reuse (Round 2)               │
│    └─ Configure to deploy from main branch                     │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. Deployment Wait                                              │
│    └─ Wait 120 seconds for Pages deployment                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. Evaluation Notification                                      │
│    ├─ Send results to evaluation_url                           │
│    ├─ Include: repo_url, commit_sha, pages_url                │
│    └─ Retry with exponential backoff (up to 5 attempts)       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. Request Marked as Processed                                 │
│     ├─ Store in /tmp/processed_requests.json                   │
│     └─ Enable duplicate detection for future requests          │
└─────────────────────────────────────────────────────────────────┘
```

### Round-Specific Behavior

**Round 1 - Fresh Build**:
- Creates new repository from scratch
- Generates initial code and documentation
- Commits all files including attachments
- Enables GitHub Pages for the first time
- Sets up complete project structure

**Round 2 - Revision & Enhancement**:
- Loads previous README.md for context
- Updates existing repository
- Improves code based on new requirements
- Reuses existing GitHub Pages configuration
- Maintains project continuity

## Testing

### Manual Testing
The `test_github.py` script verifies API connectivity:

```bash
python test_github.py
```

**What it tests**:
- ✅ GitHub authentication and token validity
- ✅ GitHub repository access and listing
- ✅ OpenAI API authentication
- ✅ Available OpenAI models listing

### Integration Testing
Test the full pipeline with a sample request:

1. Start the server: `uvicorn app.main:app --reload`
2. Send a test request using curl (see "Running the Application" section)
3. Monitor console output for processing steps
4. Check GitHub for created repository
5. Verify GitHub Pages deployment at `https://{username}.github.io/{task}/`

## Deployment

This application can be deployed to various platforms that support Python FastAPI applications.

### Recommended Platforms
- **Render** - Easy deployment with automatic HTTPS
- **Railway** - Simple Git-based deployment
- **Heroku** - Classic PaaS with add-ons
- **Fly.io** - Global deployment with edge capabilities
- **Any VPS** - Full control with Docker or direct Python setup

### Deployment Configuration

The `runtime.txt` specifies Python version for platform compatibility:
```
python-3.12.3
```

### Environment Variables Setup
Ensure all required environment variables are configured in your deployment platform:
- `GITHUB_TOKEN`
- `GITHUB_USERNAME`
- `USER_SECRET`
- `OPENAI_API_KEY`

### Platform-Specific Notes

**Render**:
- Auto-deploys from GitHub repository
- Use the `/ping` endpoint for keep-alive monitoring
- Set environment variables in Render dashboard

**Railway**:
- Automatically detects Python apps
- Configure environment variables in project settings

**Heroku**:
- Requires `Procfile` (create: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
- Set buildpack to Python

## Security Notes

⚠️ **Important Security Considerations**:

1. **Environment Variables**
   - ✅ Always use `.env` for sensitive credentials
   - ❌ Never commit `.env` to version control
   - ✅ Use `.env.example` as template without real values
   - ✅ Ensure `.env` is in `.gitignore`

2. **API Authentication**
   - The `USER_SECRET` validates incoming requests
   - Keep this secret complex and private
   - Rotate secrets periodically

3. **GitHub Token Permissions**
   - Use minimal required permissions (`repo`, `admin:repo_hook`)
   - Consider using fine-grained personal access tokens
   - Never share tokens in code or logs

4. **Production Recommendations**
   - ✅ Implement rate limiting for production use
   - ✅ Add request size limits
   - ✅ Monitor API usage and costs
   - ✅ Use HTTPS in production
   - ✅ Implement proper logging without exposing secrets

5. **Data Handling**
   - Attachments are stored in `/tmp` (ephemeral)
   - Processed requests tracked locally
   - No persistent database of sensitive information

## Error Handling

The application includes comprehensive error handling:

### OpenAI API Failures
- **Behavior**: Falls back to simple HTML template
- **User Impact**: App still gets created, just with basic functionality
- **Logged**: Error details printed to console

### GitHub API Errors
- **Behavior**: Errors logged with detailed messages
- **Repository Creation**: Reuses existing repo if creation fails
- **File Operations**: Attempts continue even if some files fail

### Attachment Decode Errors
- **Behavior**: Logged and skipped, processing continues
- **Impact**: Valid attachments still processed
- **Logged**: Failed attachment names and error details

### Evaluation Notification Failures
- **Behavior**: Retries with exponential backoff
- **Retry Strategy**: Up to 5 attempts with delays (1s, 2s, 4s, 8s, 16s)
- **Fallback**: Request still marked as processed even if notification fails

### Duplicate Requests
- **Behavior**: Re-notifies evaluation server without reprocessing
- **Response**: Returns success with "duplicate handled" message

## Limitations & Future Improvements

### Current Limitations
- 📄 **Single-File Output**: Currently generates single-file HTML applications
- 🎨 **No Multi-File Support**: Cannot create projects with separate CSS/JS files
- 🚦 **No Rate Limiting**: Production deployments should add rate limiting
- 🔔 **No Webhooks**: Doesn't listen for GitHub events
- 🤖 **Hardcoded Model**: LLM model hardcoded to `gpt-5`
- 💾 **Ephemeral Storage**: Uses `/tmp` which may not persist across deployments

### Potential Improvements
- ✨ Support multi-file project structures (separate CSS, JS, assets)
- 🔄 Add webhook support for GitHub events
- 🎛️ Make LLM model configurable via environment variable
- 📊 Add persistent database for request tracking
- 🔐 Implement advanced authentication (JWT, OAuth)
- 📈 Add monitoring and analytics dashboard
- 🧪 Expand test coverage with unit and integration tests
- 🌐 Support multiple LLM providers (Anthropic, Cohere, etc.)
- 📦 Add project templates for common app types
- 🔍 Implement code quality checking before deployment

## License

MIT License - automatically generated for all created repositories.

Repositories created by this system include an MIT License by default, allowing free use, modification, and distribution.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following these guidelines:
   - Code follows existing patterns and style
   - Environment variables documented in `.env.example`
   - Error handling implemented appropriately
   - Console logging added for debugging
4. **Test your changes**: Ensure tests pass successfully
5. **Commit your changes**: `git commit -m 'Add some feature'`
6. **Push to the branch**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

### Code Standards
- Follow PEP 8 style guidelines for Python code
- Add docstrings for new functions
- Include error handling for external API calls
- Log important events and errors
- Update README.md if adding new features or changing behavior

---

**Note**: This project was created as part of the TDS (Tools in Data Science) course project 1.

**Repository**: [https://github.com/Viakya/tds-project-1](https://github.com/Viakya/tds-project-1)
