# Karate BDD Automation Generator Backend

This is the FastAPI backend for the Karate BDD Automation Generator. It provides endpoints for parsing OpenAPI specifications, generating Karate BDD test cases, and setting up WireMock stubs.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The server will start at http://localhost:8000

## API Endpoints

- `POST /parse-openapi`: Parse uploaded OpenAPI specification files
- `POST /generate-tests`: Generate Karate BDD test cases
- `POST /generate`: LLM integration endpoint for processing JIRA stories
- `POST /setup-wiremock`: Generate WireMock stubs

## Testing

Run tests using pytest:
```bash
pytest
```

## Development

The server runs in development mode with auto-reload enabled. API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc