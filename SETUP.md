# VoteHub Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Tavily API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Getting API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

#### Tavily API Key
1. Go to https://tavily.com/
2. Sign up for an account
3. Navigate to your dashboard
4. Copy your API key

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory**

2. **Create the `.env` file** with your API keys (see above)

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Backend API (port 5001)
   - Frontend (port 3000)

4. **Check service status**:
   ```bash
   docker-compose ps
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Health check: http://localhost:5001/api/health

### Stop Services

```bash
docker-compose down
```

## Local Development (without Docker)

### Backend

1. **Set up Python environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export TAVILY_API_KEY=your_tavily_api_key
   ```

3. **Run the backend**:
   ```bash
   python app.py
   ```

### Frontend

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Access the frontend**: http://localhost:3000

## Features

### Search Integration

The application uses Tavily Search API for finding party affiliations:
- Provides accurate, up-to-date information about politicians
- Integrated with LangChain for intelligent searching
- Rate-limited to prevent API quota issues

## Troubleshooting

### API Key Issues

If you see errors about missing API keys:

1. Verify `.env` file exists in the root directory
2. Check API keys are valid and not expired
3. Restart Docker containers to pick up new environment variables:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Port Conflicts

If ports are already in use:

1. Check what's using the ports:
   ```bash
   lsof -i :3000  # Frontend
   lsof -i :5001  # Backend
   ```

2. Either stop the conflicting service or modify `docker-compose.yml` to use different ports

## Additional Documentation

- API Documentation - Coming soon

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review error messages in the browser console (F12)
3. Ensure all environment variables are set correctly
