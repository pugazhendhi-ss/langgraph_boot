# ERP Task Analyzer 🔍

A LangGraph-powered workflow system that fetches and analyzes ERP tasks to provide productivity insights through natural language processing.

## Features

- **Smart Query Routing**: Analyzes user input to determine the most efficient workflow path
- **Password Management**: Securely fetches credentials from database
- **ERP Integration**: Connects to ERP systems to retrieve task data
- **AI-Powered Analysis**: Uses OpenAI GPT-4o-mini for task summarization and productivity insights
- **Web Interface**: Clean, responsive frontend for easy interaction


## Quick Start

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) for dependency management


### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd langgraph_boot
```

2. **Install dependencies**
```bash
uv sync
```

3. **Configure environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-ka....
ERP_LOGIN_URL=https://erp.softsua...
ERP_PASSWORD=#PK@200....
```

4. **Run the application**
```bash
uv run python main.py
```

The API will be available at `http://127.0.0.1:8900`

## Usage

### API Endpoint

**POST** `/chat`

```bash
curl -X 'POST' \
  'http://127.0.0.1:8900/chat' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Analyze my productivity, my email is user@company.com"}'
```

**Response:**

```json
{
  "llm_response": "Your productivity analysis based on ERP tasks..."
}
```


### Web Interface

Open the frontend HTML file in your browser for a user-friendly chat interface.

## Workflow Logic

The system intelligently routes queries based on available information:

- **Email provided**: Fetches password → Retrieves tasks → Analyzes
- **Email + Password provided**: Retrieves tasks → Analyzes
- **Tasks provided directly**: Analyzes immediately
- **General inquiry**: Provides capability information


## Project Structure

```
langgraph_boot/
├── .venv/                      # Virtual environment
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── setup.py           # Database setup
│   ├── pydantics/
│   │   ├── __init__.py
│   │   └── base_schema.py     # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── nudge.py           # API routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── erp_extractor.py   # ERP integration service
│   │   ├── tools.py           # Utility tools
│   │   └── workflow.py        # LangGraph workflow
│   └── templates/
│       ├── __init__.py
│       ├── index.html         # Web interface
│       └── system_prompt.py   # AI prompts
├── __init__.py
├── .env                       # Environment variables
├── .gitignore                # Git ignore rules
├── .python-version           # Python version
├── main.py                   # FastAPI application entry point
├── pyproject.toml            # Project configuration
├── README.md                 # This file
└── uv.lock                   # Dependency lock file
```


## Core Components

### Services

- **workflow.py**: Main LangGraph workflow implementation with supervisor and processing nodes
- **erp_extractor.py**: ERP system integration and task extraction
- **tools.py**: Utility functions and helper methods


### Configuration

- **settings.py**: Application settings and environment variable management
- **base_schema.py**: Pydantic models for request/response validation


### API

- **main.py**: FastAPI application setup and server configuration
- **nudge.py**: API route handlers for chat endpoints


## Dependencies

Add your `requirements.txt` after setup. Core dependencies include:

- `langgraph` - Workflow orchestration
- `openai` - AI model integration
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation


## Environment Variables

| Variable | Description |
| :-- | :-- |
| `OPENAI_API_KEY` | OpenAI API key for GPT model access |
| `ERP_LOGIN_URL` | Your ERP system login endpoint |
| `ERP_PASSWORD` | ERP system password |

## Development

### Running in Development Mode

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8900
```


### Workflow Visualization

The LangGraph workflow can be visualized for debugging and documentation:

```python
from app.services.workflow import create_workflow
from IPython.display import Image, display

app = create_workflow()
display(Image(app.get_graph().draw_mermaid_png()))
```
