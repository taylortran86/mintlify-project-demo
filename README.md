# Mintie Calendar Application

A simple, intuitive full-stack application for managing tasks and calendar events. Built with FastAPI (Python) backend and vanilla JavaScript frontend.

## Features

### Tasks
- Create, read, update, and delete tasks
- Mark tasks as complete/incomplete
- Set optional due dates
- Filter tasks by status (all, active, completed)

### Calendar Events
- Create, read, update, and delete calendar events
- Set start and end times for events
- View all upcoming events
- Filter events by date range

## Project Structure

```
mintlify-project-demo/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and API endpoints
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic validation schemas
│   └── database.py      # Database configuration
├── frontend/
│   ├── index.html       # Main HTML file
│   ├── style.css        # Application styles
│   └── app.js           # JavaScript frontend logic
├── pyproject.toml       # Poetry configuration and dependencies
├── requirements.txt     # Python dependencies (legacy)
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Poetry (recommended) - [Installation Guide](https://python-poetry.org/docs/#installation)
- OR pip (Python package installer) for traditional setup

## Installation

### Option 1: Using Poetry (Recommended)

1. Clone or navigate to the project directory:
```bash
cd mintlify-project-demo
```

2. Install dependencies using Poetry:
```bash
poetry install
```

This will create a virtual environment and install all dependencies automatically.

**Note:** Poetry automatically manages the virtual environment. You don't need to manually activate it - just prefix commands with `poetry run` (see examples below).

#### IDE Integration (Optional)

If you prefer to work within an activated virtual environment in your IDE or terminal:

1. Find your Poetry virtual environment path:
```bash
poetry env info --path
```

2. Configure your IDE to use this Python interpreter, or activate it manually:
```bash
# On macOS/Linux
source $(poetry env info --path)/bin/activate

# On Windows
& "$(poetry env info --path)\Scripts\activate.ps1"
```

### Option 2: Using pip

1. Clone or navigate to the project directory:
```bash
cd mintlify-project-demo
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Using Poetry

Start the FastAPI backend server with any of these commands:

```bash
# Option 1: Direct uvicorn command (recommended)
poetry run uvicorn backend.main:app --reload

# Option 2: Use the custom Poetry script
poetry run start
```

### Using pip

1. Start the FastAPI backend server:
```bash
python -m uvicorn backend.main:app --reload
```

### Accessing the Application

The API will be available at `http://localhost:8000`

Open the frontend in your browser:
- Navigate to `http://localhost:8000/static/index.html`
- Or open `frontend/index.html` directly in your browser

## API Documentation

This project includes two separate API surfaces:

### Public API (For Documentation & External Customers)
The public API represents what you would document for external API consumers:
- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/public/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/public/redoc
- **OpenAPI Schema**: http://localhost:8000/public/openapi.json

The public API includes typical SaaS product features:
- API Key Management (`/public/v1/api-keys`)
- Webhook Configuration (`/public/v1/webhooks`)
- Usage Analytics (`/public/v1/analytics`)
- Account Information (`/public/v1/account`)

### Internal Application Routes
The internal routes power the web interface:
- **Internal API Documentation**: http://localhost:8000/internal/docs
- **OpenAPI Schema**: http://localhost:8000/internal/openapi.json

These routes handle the actual task and event CRUD operations for the application.

### Exporting OpenAPI Schema

You can export the **Public API** OpenAPI schema to a file for documentation generation, API client tools, or version control:

**Using Poetry:**
```bash
# Export as JSON (default) - using the Poetry script
poetry run export-schema

# Or run directly
poetry run python export_openapi.py

# Export as YAML
poetry run export-schema --format yaml

# Export both formats
poetry run export-schema --format both

# Custom output filename
poetry run export-schema --output my-api-schema
```

**Using pip:**
```bash
# Export as JSON (default)
python export_openapi.py

# Export as YAML
python export_openapi.py --format yaml

# Export both formats
python export_openapi.py --format both
```

This generates `openapi.json` and/or `openapi.yaml` files containing the **Public API** specification (not the internal routes). These files can be used with:
- **Mintlify** and other documentation generators
- **Swagger Editor** for API design
- **OpenAPI Generator** for client SDK generation
- **Postman** for API testing

## Public API Endpoints

The Public API provides customer-facing endpoints that would typically be documented for external developers:

### API Key Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/public/v1/api-keys` | Create a new API key |
| GET | `/public/v1/api-keys` | List all API keys |
| GET | `/public/v1/api-keys/{key_id}` | Get API key details |
| DELETE | `/public/v1/api-keys/{key_id}` | Revoke an API key |

### Webhook Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/public/v1/webhooks` | Create a webhook subscription |
| GET | `/public/v1/webhooks` | List all webhooks |
| GET | `/public/v1/webhooks/{webhook_id}` | Get webhook details |
| PATCH | `/public/v1/webhooks/{webhook_id}` | Update a webhook |
| DELETE | `/public/v1/webhooks/{webhook_id}` | Delete a webhook |

### Analytics & Account

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/public/v1/analytics` | Get usage analytics |
| GET | `/public/v1/analytics/usage` | Get usage statistics |
| GET | `/public/v1/account` | Get account information |
| GET | `/public/v1/health` | API health check |

## Internal Application Endpoints

These endpoints power the web application (not typically documented externally):

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks` | Get all tasks (optional filter: `?completed=true/false`) |
| GET | `/api/tasks/{task_id}` | Get a specific task |
| PATCH | `/api/tasks/{task_id}` | Update a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/events` | Create a new event |
| GET | `/api/events` | Get all events (optional filters: `?start_date=...&end_date=...`) |
| GET | `/api/events/{event_id}` | Get a specific event |
| PATCH | `/api/events/{event_id}` | Update an event |
| DELETE | `/api/events/{event_id}` | Delete an event |

## Example API Usage

### Public API Examples

#### Create an API Key
```bash
curl -X POST "http://localhost:8000/public/v1/api-keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "scopes": ["read", "write"],
    "expires_at": "2025-12-31T23:59:59Z"
  }'
```

#### Create a Webhook
```bash
curl -X POST "http://localhost:8000/public/v1/webhooks" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhooks",
    "events": ["task.created", "task.completed"],
    "description": "Production webhook"
  }'
```

#### Get Analytics
```bash
curl "http://localhost:8000/public/v1/analytics?period=last_30_days"
```

#### Get Account Info
```bash
curl "http://localhost:8000/public/v1/account"
```

### Internal Application Examples

#### Create a Task
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "item_type": "task",
    "due_date": "2025-12-01T17:00:00"
  }'
```

#### Create an Event
```bash
curl -X POST "http://localhost:8000/api/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly sync with the team",
    "item_type": "event",
    "start_time": "2025-11-15T10:00:00",
    "end_time": "2025-11-15T11:00:00"
  }'
```

## Database

The application uses SQLite as the database, which will be automatically created as `calendar_todo.db` when you first run the application. No additional database setup is required.

## Development

### Running in Development Mode

The `--reload` flag enables auto-reload when code changes:

**With Poetry:**
```bash
poetry run uvicorn backend.main:app --reload
```

**With pip:**
```bash
python -m uvicorn backend.main:app --reload
```

### Adding New Dependencies

**With Poetry:**
```bash
poetry add package-name
```

For development dependencies:
```bash
poetry add --group dev package-name
```

**With pip:**
```bash
pip install package-name
pip freeze > requirements.txt
```

### Code Formatting and Linting

If you're using Poetry, development tools are included:

```bash
# Format code with Black
poetry run black backend/

# Lint code with Ruff
poetry run ruff check backend/
```

### Testing the API

You can test the API using:
- The built-in Swagger UI at http://localhost:8000/docs
- cURL commands (examples above)
- Postman or similar API testing tools
- The provided frontend interface

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server implementation
- **Poetry**: Dependency management and packaging

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables
- **Vanilla JavaScript**: No frameworks, pure JS for simplicity

### Development Tools
- **Black**: Code formatter
- **Ruff**: Fast Python linter
- **pytest**: Testing framework (included for future tests)
- **httpx**: HTTP client for testing (included for future tests)

## Future Enhancements

Potential features for documentation showcasing:
- User authentication and authorization
- Task categories and tags
- Recurring events
- Email notifications
- File attachments
- Search functionality
- Export to calendar formats (iCal)
- Mobile responsive improvements
- Dark mode theme

## License

This is a demo project for documentation purposes.
