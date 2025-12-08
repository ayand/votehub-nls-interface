# VoteHub Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (required for AI agent functionality)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Getting API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (it will only be shown once)

**Important**: Keep your API key secure and never commit it to version control.

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd votehub-chatbot
   ```

2. **Create the `.env` file** with your API keys (see above)
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Start all services**:
   ```bash
   docker-compose up --build
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
   # View all logs
   docker-compose logs -f
   
   # View backend logs only
   docker-compose logs -f backend
   
   # View frontend logs only
   docker-compose logs -f frontend
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001
   - Health check: http://localhost:5001/api/health

### Stop Services

```bash
# Stop services
docker-compose down

# Stop services and remove volumes
docker-compose down -v
```

### Restart Services

```bash
# Restart without rebuilding
docker-compose restart

# Restart with rebuild
docker-compose up --build
```

## Local Development (without Docker)

If you prefer to run the services locally without Docker:

### Backend

1. **Set up Python environment** (Python 3.13 recommended):
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   # On macOS/Linux
   export OPENAI_API_KEY=your_openai_api_key
   
   # On Windows (Command Prompt)
   set OPENAI_API_KEY=your_openai_api_key
   
   # On Windows (PowerShell)
   $env:OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Run the backend**:
   ```bash
   python app.py
   ```
   
   The backend will be available at http://localhost:5000

### Frontend

1. **Install dependencies** (Node.js 18+ required):
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Access the frontend**: http://localhost:3000

### Running Both Services

Open two terminal windows:
- Terminal 1: Run backend (from `backend/` directory)
- Terminal 2: Run frontend (from `frontend/` directory)

## Verifying Installation

### 1. Check Backend Health
```bash
curl http://localhost:5001/api/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test Polls Endpoint
```bash
curl "http://localhost:5001/api/polls?q=Biden+approval"
```

You should receive JSON data with poll results.

### 3. Check Frontend
Open http://localhost:3000 in your browser and try searching for "Biden approval ratings"

## Features

### Natural Language Queries

The application accepts natural language queries like:
- "Biden approval ratings last month"
- "2024 GOP primary polls"
- "Generic ballot polls"
- "Trump vs Biden polls from 2024"

### AI Agent Features

The backend uses multiple AI agents:
- **Query Parser**: Converts natural language to API parameters
- **Name Corrector**: Normalizes candidate name variations
- **Party Identifier**: Determines candidate party affiliations
- **Color Assigner**: Intelligently assigns colors to poll choices

## Troubleshooting

### API Key Issues

**Problem**: Errors about missing or invalid API keys

**Solutions**:
1. Verify `.env` file exists in the root directory
2. Check that API key is valid and not expired
3. Ensure no extra spaces or quotes around the key
4. Restart Docker containers to pick up new environment variables:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Port Conflicts

**Problem**: Ports 3000 or 5001 are already in use

**Solutions**:
1. Check what's using the ports:
   ```bash
   # On macOS/Linux
   lsof -i :3000  # Frontend
   lsof -i :5001  # Backend
   
   # On Windows
   netstat -ano | findstr :3000
   netstat -ano | findstr :5001
   ```

2. Either stop the conflicting service or modify `docker-compose.yml`:
   ```yaml
   # Change port mappings in docker-compose.yml
   ports:
     - "3001:3000"  # Frontend on 3001 instead
     - "5002:5000"  # Backend on 5002 instead
   ```

### Docker Build Failures

**Problem**: Docker build fails

**Solutions**:
1. Clear Docker cache and rebuild:
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose up --build
   ```

2. Check Docker daemon is running:
   ```bash
   docker ps
   ```

3. Ensure sufficient disk space:
   ```bash
   docker system df
   ```

### Backend Import Errors

**Problem**: Python import errors when running locally

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. Check Python version (3.13 recommended):
   ```bash
   python --version
   ```

### Frontend Build Errors

**Problem**: npm errors or build failures

**Solutions**:
1. Clear npm cache and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Node.js version (18+ required):
   ```bash
   node --version
   ```

3. Try using npm instead of other package managers:
   ```bash
   npm install  # Not yarn or pnpm
   ```

### CORS Errors

**Problem**: Browser shows CORS errors when accessing API

**Solutions**:
1. Ensure backend is running and accessible
2. Check that CORS is enabled in `backend/app.py`
3. Use correct API URL (http://localhost:5001)
4. Don't access frontend via file:// protocol (use http://localhost:3000)

### Slow API Responses

**Problem**: Queries take a long time to complete

**Explanation**: This is expected behavior:
- AI agents need time to process queries
- Web searches for party affiliations add latency
- First query after startup is slower (agent initialization)

**Tips**:
- Subsequent queries for similar data are faster
- Consider implementing caching for better performance

## Development Tips

### Backend Development

1. **Enable debug mode** (for local development):
   ```python
   # In app.py
   application.run(host='0.0.0.0', port=5000, debug=True)
   ```

2. **View detailed logs**:
   ```bash
   docker-compose logs -f backend
   ```

3. **Hot reload**: Flask automatically reloads on code changes in debug mode

### Frontend Development

1. **NextJS auto-reload**: The dev server automatically reloads on file changes

2. **View console errors**: Open browser DevTools (F12) to see errors

3. **Type checking**:
   ```bash
   npm run type-check
   ```

### Database (Future Enhancement)

Currently, the application doesn't use a database. All data is fetched from the VoteHub API in real-time. Consider adding a database for:
- Caching API responses
- Storing party affiliations
- User preferences
- Historical queries

## Performance Optimization

### For Production Deployment

1. **Environment variables**:
   - Set `NODE_ENV=production` for frontend
   - Use production-grade WSGI server (Gunicorn) for backend

2. **Caching**:
   - Implement Redis for caching agent results
   - Cache VoteHub API responses

3. **Monitoring**:
   - Add application monitoring (DataDog, New Relic)
   - Track API response times
   - Monitor agent call frequency and costs

4. **Rate Limiting**:
   - Implement rate limiting for API endpoints
   - Add request throttling for OpenAI API calls

## Additional Documentation

- [README.md](README.md) - Project overview and quick start
- [docker-compose.yml](docker-compose.yml) - Container orchestration configuration

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: `docker-compose logs -f`
2. **Review error messages**: Check browser console (F12) and terminal output
3. **Verify environment**: Ensure all environment variables are set correctly
4. **Check API status**: Verify OpenAI API is working and you have credits
5. **Review the code**: Check backend services and processors for implementation details

## Next Steps

After setup, you can:

1. **Query polls**: Try different natural language queries
2. **Explore the code**: Review the backend services and processors
3. **Extend functionality**: Add new features or agent capabilities
4. **Optimize performance**: Implement caching and monitoring
5. **Deploy to production**: Use cloud hosting (AWS, GCP, Azure)
