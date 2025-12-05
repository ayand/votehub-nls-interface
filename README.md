# VoteHub ChatBot - Full Stack Docker Application

A full-stack application with a Python Flask backend (Python 3.13) and a NextJS frontend, fully containerized with Docker.

## Project Structure

```
votehub-chatbot/
├── backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker configuration
├── frontend/
│   ├── app/
│   │   ├── layout.tsx      # NextJS layout
│   │   └── page.tsx        # Main page component
│   ├── package.json        # Node dependencies
│   ├── next.config.js      # NextJS configuration
│   ├── tsconfig.json       # TypeScript configuration
│   └── Dockerfile          # Frontend Docker configuration
└── docker-compose.yml      # Docker Compose orchestration
```

## Prerequisites

- Docker Desktop or Docker Engine installed
- Docker Compose installed (usually comes with Docker Desktop)
- OpenAI API key (required for chatbot functionality)

## Environment Setup

Before running the application, you need to configure your OpenAI API key:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. The `.env` file is already in `.gitignore` and will not be committed to version control.

**Note**: You can obtain an OpenAI API key from [OpenAI's platform](https://platform.openai.com/api-keys).

## Running the Application

### Option 1: Using Docker Compose (Recommended)

1. Build and start both services:
```bash
docker-compose up --build
```

2. Access the applications:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:5001

3. Stop the services:
```bash
docker-compose down
```

### Option 2: Running Individual Services

#### Backend Only
```bash
cd backend
docker build -t flask-backend .
docker run -p 5001:5000 -e OPENAI_API_KEY=your-openai-api-key flask-backend
```

#### Frontend Only
```bash
cd frontend
docker build -t nextjs-frontend .
docker run -p 3000:3000 nextjs-frontend
```

## API Endpoints

The Flask backend exposes the following endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/polls?q=<query>` - Polls endpoint that accepts a URL-encoded query string parameter and returns polls that match that query

## Development

### Backend Development
The Flask backend is configured with:
- Python 3.13
- Flask 3.1.0
- CORS enabled for frontend communication
- Running on port 5000

### Frontend Development
The NextJS frontend is configured with:
- NextJS 14.2
- TypeScript
- React 18
- Running on port 3000

## Notes

- The frontend is configured to fetch data from `http://localhost:5001` (host port mapped to container port 5000)
- Both services are connected via a Docker bridge network for inter-container communication
- The frontend depends on the backend and will wait for it to start
