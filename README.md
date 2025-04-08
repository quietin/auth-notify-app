# Auth Notify App

A simple web application built with **FastAPI**, providing:

- User registration and login (email + password)
- Real-time notification via WebSocket when a new user registers

This project is designed as a minimal, well-structured implementation of real-time authentication flows using FastAPI, with proper session handling and basic test coverage.

## Features

### User Authentication
- Registration page (email + password)
- Login page with JWT-based authentication
- Session stored securely in HTTP-only cookies
- Welcome page shown after login

### Simple Frontend
- Built with plain HTML + JavaScript
- Served directly by FastAPI using static files

### Real-time Notifications
- All users currently on the **welcome page** receive a live notification when a new user registers
- Notification includes the new user's email
- Powered by **WebSocket**, ensuring real-time message delivery with minimal latency

### Testing
- Unit tests and integration tests using `pytest` and `httpx`
- All tests run against an in-memory SQLite database for isolation and speed

### Environment-based Configuration
- Supports `.env.local` for local development
- Supports `.env.docker` for Docker-based setup
- Easily extendable for different environments

## Design Decisions & Trade-offs

### Design Decisions

#### Project Structure
- Domain-based layout: Code is organized into `api/`, `models/`, `services/`, and `utils/` for clarity and maintainability.
- Path handling: All file references (e.g., static files, logs) use `pathlib.Path` based on `__file__`, ensuring reliability across environments.

#### Robustness and Observability
- Custom logging: A daily-rotating file-based logger improves debugging and operational visibility.
- Graceful error handling: Exceptions are caught and logged at key operations to improve debuggability and runtime robustness.
- Graceful shutdown: WebSocket connections are cleanly closed when the server is terminated to avoid runtime errors.

#### Security and Validation
- RESTful authentication: JWT tokens are stored in HTTP-only cookies for secure session management in a stateless API design.
- Input validation: Request payloads are validated using Pydantic models to ensure strict type enforcement and input safety.

#### Configuration and Deployment
- Environment-based configuration: Supports `.env.local` for local development and `.env.docker` for Docker deployment.
- Docker-ready: A Dockerfile is provided to enable reproducible environments and quick setup across machines.

#### Frontend Integration
- WebSocket resilience: The frontend includes automatic reconnect logic for maintaining persistent real-time connections with the server.

### Trade-offs

- Simplified frontend: The frontend is implemented using plain HTML and JavaScript without a framework. This reduces complexity but limits scalability and dynamic UI features.
- SQLite for testing: Integration tests use in-memory SQLite for performance and isolation, but it may not fully replicate MySQL behaviors such as transaction semantics.
- Minimal authentication scope: The authentication system is intentionally minimal, omitting features like password reset, email verification, and third-party login to maintain simplicity and focus on core logic.


## Getting Started

You can run the application in two ways:

- **Option 1:** Run locally with Python environment (for development)
- **Option 2:** Run with Docker and Docker Compose (recommended)

---

### Option 1: Run locally

#### Prerequisites

- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/) for package management

#### 1. Clone the repository

```bash
git clone https://github.com/quietin/auth-notify-app.git
cd auth-notify-app
```


#### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure environment variables

A sample `.env.local` file is already provided in the project root.  
You may need to update the values to match your environment (e.g., database connection, secret key):

```env
APP_ENV=local

# change to use your configs
SECRET_KEY=supersecretkey
DB_HOST=localhost
DB_DATABASE=auth_db
DB_USER=root
DB_PASSWORD=passwd

```

#### 5. Run the application

```bash
uvicorn app.main:app --reload
```

The app will be available at: http://localhost:8000

### Option 2: Run with Docker (recommended)

This is the easiest way to start the project without installing Python, pip, or MySQL locally.

#### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

#### 1. Clone the repository

```bash
git clone https://github.com/quietin/auth-notify-app.git
cd auth-notify-app
```

#### 2. Use the provided `.env.docker` file

The project includes a pre-configured `.env.docker` file for the Docker environment. You can modify it if needed.

#### 3. Start the app with Docker Compose

```bash
docker-compose up --build
```

The application will be available at: http://localhost:8000

To stop the app, press `Ctrl+C` in the terminal.


## Running Tests

The project includes both unit tests and integration tests written with `pytest`.

Tests are located in the `tests/` directory, and use an in-memory SQLite database to ensure speed and isolation.

### Run tests locally

First, activate your virtual environment if not already:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Then run:

```bash
pytest
```

You can run a specific test file:

```bash
pytest tests/integration/test_auth_flow.py
```

### Run tests in Docker (if needed)

If you're using Docker, you can run tests inside the container (assuming Dockerfile includes test dependencies):

```bash
docker-compose run --rm web pytest
```

This assumes that your `docker-compose.yml` defines a `web` service and installs all required test dependencies.


## Project Structure

```
auth-notify-app/
├── app/                          # Main application package
│   ├── api/                      # API route definitions (e.g., auth, websocket)
│   ├── models/                   # Pydantic and SQLModel models
│   ├── services/                 # Business logic (user management, notification manager)
│   ├── static/                   # Frontend HTML and JavaScript files
│   ├── utils/                    # Utility modules (e.g., logger, config)
│   ├── main.py                   # FastAPI app initialization
│   └── database.py               # Database session setup
│
├── tests/                        # Unit and integration tests
│   ├── integration/              # Integration tests for APIs and workflows
│   └── unit/                     # Unit tests (e.g., services, utils)
│
├── snapshots/                   # UI screenshots for documentation or reference
├── .env.local                   # Local environment variables
├── .env.docker                  # Docker environment variables
├── Dockerfile                   # Docker build instructions
├── docker-compose.yml           # Docker multi-service configuration
├── requirements.txt             # Project dependencies
├── pytest.ini                   # Pytest configuration
├── .gitignore                   # Files and folders to exclude from Git
└── README.md
```

## Future Improvements

- **Static analysis and linting**: Integrate tools like `pyright` and `pylint` to enforce type safety and coding standards, improving readability and robustness.
- **Persistent notifications**: Store notification events in the database, enabling support for offline users and historical message replay.
- **CI/CD integration**: Add GitHub Actions or similar pipelines to automate testing, linting, and deployment.
- **Authentication enhancements**: Add production-level features such as password reset, email verification, or third-party login via OAuth.

