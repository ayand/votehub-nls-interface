# VoteHub ChatBot - AI-Powered Poll Analysis

A full-stack application that uses AI agents to analyze and visualize political polling data. Built with Python Flask backend (Python 3.13) and NextJS frontend, fully containerized with Docker.

## Overview

VoteHub ChatBot allows users to query political polls using natural language. The system uses OpenAI agents to:
- Parse natural language queries into API parameters
- Normalize candidate names across different polls
- Determine party affiliations
- Generate intelligent color mappings for visualizations

## Data Source

This project uses the [VoteHub Polls API](https://votehub.com/polls/api/) to fetch political polling data. The API provides comprehensive access to poll results, including approval ratings, primary elections, general elections, and more.

**License**: The VoteHub API data is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), which allows sharing and adaptation with appropriate attribution.

## Project Structure

```
votehub-chatbot/
├── backend/
│   ├── app.py                    # Flask application (OOP refactored)
│   ├── services/                 # Business logic services
│   │   ├── agent_service.py      # Base class for AI agents
│   │   ├── api_service.py        # HTTP communication
│   │   ├── choice_service.py     # Choice processing
│   │   ├── color_service.py      # Color mapping
│   │   ├── name_correction_service.py    # Name correction agent
│   │   ├── party_affiliation_service.py  # Party lookup agent
│   │   └── poll_params_service.py        # Query parsing agent
│   ├── processors/               # Workflow orchestration
│   │   └── poll_processor.py     # Poll processing workflow
│   ├── models.py                 # Pydantic data models
│   ├── tools.py                  # Agent tools
│   ├── supporting_agents.py      # Agent utilities
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend Docker configuration
├── frontend/
│   ├── app/
│   │   ├── components/           # React components
│   │   │   ├── Attribution.tsx
│   │   │   ├── ChartView.tsx
│   │   │   ├── ChoicesSummary.tsx
│   │   │   ├── ColorLegend.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── PollsTable.tsx
│   │   ├── layout.tsx            # NextJS layout
│   │   ├── page.tsx              # Main page component
│   │   ├── models/               # TypeScript models
│   │   └── utils/                # Utility functions
│   ├── package.json              # Node dependencies
│   ├── next.config.js            # NextJS configuration
│   ├── tsconfig.json             # TypeScript configuration
│   └── Dockerfile                # Frontend Docker configuration
├── docker-compose.yml            # Docker Compose orchestration
├── README.md                     # This file
└── SETUP.md                      # Setup instructions
```

## Architecture

### Backend (Python Flask)

The backend follows object-oriented principles with clear separation of concerns:

**Service Layer** - Reusable business logic:
- `ApiService`: External API communication
- `ChoiceService`: Choice normalization and statistics
- `ColorService`: Intelligent color assignment
- `AgentService`: Base class for AI agents
  - `NameCorrectionService`: Corrects name variations
  - `PartyAffiliationService`: Determines party affiliations
  - `PollParamsService`: Parses natural language queries

**Processor Layer** - Workflow orchestration:
- `PollProcessor`: Coordinates the poll processing workflow

**Application Layer** - HTTP routing and dependency injection:
- `VoteHubApplication`: Main Flask app with dependency wiring

### Frontend (NextJS + TypeScript)

React-based single-page application with:
- Interactive poll data tables
- Chart visualizations using Recharts
- Loading states and error handling
- Responsive design

## Prerequisites

- Docker Desktop or Docker Engine installed
- Docker Compose installed (usually comes with Docker Desktop)
- OpenAI API key (required for AI agent functionality)

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
   - **Health check**: http://localhost:5001/api/health

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

- **`GET /api/health`** - Health check endpoint
  - Returns: `{"status": "healthy"}`

- **`GET /api/polls?q=<query>`** - Polls endpoint
  - Accepts natural language query (URL-encoded)
  - Examples:
    - `?q=Trump approval ratings last month`
    - `?q=2024 GOP primary polls`
    - `?q=Generic ballot polls from Morning Consult`
  - Returns: Processed poll data with statistics and color mappings

### Response Format

```json
{
    "subject_poll-type": {
        "color_map": {
            "KEY1": "VALUE1",
            "KEY2": "VALUE2",
            "KEY3": "VALUE3"
        },
        "polls": [ ... ]
    }
}
```

## Development

### Backend Development
The Flask backend is configured with:
- Python 3.13
- Flask 3.1.0
- CORS enabled for frontend communication
- Running on port 5000 (exposed as 5001)
- Object-oriented architecture with dependency injection

### Frontend Development
The NextJS frontend is configured with:
- NextJS 14.2
- TypeScript
- React 18
- Recharts for visualizations
- Running on port 3000

### Local Development Without Docker

See [SETUP.md](SETUP.md) for detailed instructions on running the application locally without Docker.

## Key Features

### AI-Powered Query Processing
- Natural language to API parameter conversion
- Intelligent date parsing (e.g., "last month", "this year")
- Subject and poll type extraction

### Intelligent Name Normalization
- Corrects variations like "Trump, Jr." vs "Trump Jr"
- Handles punctuation differences
- Consolidates duplicate candidates

### Party Affiliation Detection
- Uses AI with web search to determine candidate parties
- Supports: Democrat, Republican, Independent, Libertarian, Green, Other
- Caches results for performance

### Smart Color Assignment
- Standard color mappings (Dem/Rep, Approve/Disapprove)
- Party-based colors for general election polls
- Distinct colors for primary elections
- Handles edge cases and custom scenarios

### Data Processing
- Groups polls by subject and type
- Calculates statistics (mean, count)
- Deduplicates answers across multiple polls
- Handles missing or incomplete data

## Notes

- The frontend is configured to fetch data from `http://localhost:5001` (host port mapped to container port 5000)
- Both services are connected via a Docker bridge network for inter-container communication
- The frontend depends on the backend and will wait for it to start
- All AI agent functionality requires a valid OpenAI API key

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup and troubleshooting guide

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.
