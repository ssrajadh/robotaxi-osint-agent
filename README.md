# Robotaxi OSINT Agent

An autonomous intelligence agent that monitors public forums and social media for Tesla Robotaxi sightings.

## Features

- **Reddit Monitoring**: Monitors r/TeslaLounge, r/SelfDrivingCars, and r/teslamotors using public JSON endpoints (no API credentials required!)
- **X/Twitter Monitoring**: Monitors X/Twitter for robotaxi-related posts via Google Custom Search API (optional, requires Google API keys)
- **Keyword Filtering**: Fast heuristic filtering using keywords like "robotaxi", "cybercab", "manufacturer plate"
- **LLM Analysis**: Uses GPT-4o-mini to extract structured data from posts
- **Image Support**: Extracts and processes images from Reddit posts and X/Twitter
- **Deduplication**: Prevents duplicate alerts for the same post
- **JSON Output**: Stores candidates in a structured format for downstream processing

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

This includes:
- Core dependencies (pydantic, openai, requests)
- **LangGraph** and LangChain for workflow orchestration

## Usage

Run one scan cycle:

```bash
python main.py
```

The script will:
- Fetch new posts since the last run (or recent posts from the last day if no previous state)
- Analyze candidates using the LLM
- Save results to `candidates.json`
- Update `state.json` with the timestamp of this run

### Output

Results are saved to `candidates.json` with the following structure:

```json
{
  "source_id": "reddit_t3_1h4x9z",
  "source_url": "https://reddit.com/r/...",
  "timestamp_detected": "2025-12-27T10:00:00Z",
  "confidence_score": 0.95,
  "extracted_data": {
    "license_plate": "934MFG231",
    "vehicle_type": "Model Y",
    "location": "Palo Alto, CA",
    "coordinates_approx": null
  },
  "media": {
    "image_url": "https://i.redd.it/..."
  },
  "status": "PENDING_REVIEW"
}
```

## GitHub Actions Setup

The project includes a GitHub Actions workflow for automated daily scanning.

### 1. Configure Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `GOOGLE_API_KEY`: Your Google Custom Search API key (optional, for X/Twitter polling)
- `GOOGLE_CSE_ID`: Your Google Custom Search Engine ID (optional, for X/Twitter polling)

**Note:** 
- No Reddit API credentials needed! The agent uses Reddit's public JSON endpoints.
- X/Twitter polling via Google Custom Search API is optional. If not configured, the agent will only monitor Reddit.

### 2. Schedule Configuration

Edit `.github/workflows/daily-scan.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

Use [crontab.guru](https://crontab.guru/) to customize the schedule.

### 3. How It Works

- **State Persistence**: The workflow saves `state.json` (last check timestamp) and `candidates.json` as artifacts between runs
- **Automatic Downloads**: Each run automatically downloads previous state to resume from where it left off
- **Deduplication**: Existing candidates prevent duplicate entries
- **Manual Trigger**: Use "Run workflow" button in GitHub Actions tab for manual runs

### 4. Viewing Results

After each run, download the `robotaxi-state` artifact to view:
- `candidates.json`: All discovered sightings
- `state.json`: Last check timestamp

## Roadmap

- ✅ Phase 1: Reddit MVP
- ✅ X/Twitter Monitoring via Google Custom Search (keyword-based search across X/Twitter)
- ✅ Phase 2: Improve agent with LangGraph
- ⬜ Phase 3: Integrate with robotaxi tracker repo once it becomes open-source

## Architecture

### LangGraph Workflow

The agent uses **LangGraph** for workflow orchestration, providing:

- **State Management**: Centralized state flow through the workflow with type-safe state schema
- **Modular Nodes**: Separate nodes for fetching, analyzing, and routing candidates
- **Error Handling**: Accumulated error tracking across the workflow
- **Statistics**: Processing metrics tracked throughout execution
- **Extensibility**: Easy to add new nodes or modify the workflow

#### Workflow Structure

The workflow consists of three main nodes:

```
START → fetch_posts → analyze_candidates → route_candidates → END
```

1. **`fetch_posts`**: Fetches candidates from Reddit and X/Twitter sources
2. **`analyze_candidates`**: Analyzes each candidate using LLM to extract structured data
3. **`route_candidates`**: Routes candidates into valid/rejected buckets based on confidence score (≥0.5)

#### Project Structure

```
robotaxi-osint-agent/
├── graph/                      # LangGraph workflow package
│   ├── __init__.py            # Package exports
│   ├── graph_state.py         # State schema (AgentState)
│   ├── graph_nodes.py         # Node functions
│   └── graph_builder.py       # Graph construction
├── main.py                     # Entry point
├── config.py                  # Configuration
├── models.py                  # Data models (SightingCandidate, etc.)
├── llm_analyzer.py            # LLM analysis logic
├── reddit_poller.py           # Reddit data source
└── x_poller.py                # X/Twitter data source
```

#### State Schema

The `AgentState` TypedDict defines the workflow state:

- **Input**: `last_check` - Timestamp of last run
- **Processing**: `candidates`, `analyzed_candidates` - Intermediate data
- **Output**: `valid_candidates`, `rejected_candidates` - Final results
- **Metadata**: `errors`, `stats` - Error tracking and statistics

#### Extending the Workflow

To add new nodes or modify the workflow:

1. Add node functions to `graph/graph_nodes.py`
2. Register nodes in `graph/graph_builder.py`
3. Add edges to connect nodes in the workflow
4. Update `AgentState` in `graph/graph_state.py` if new state fields are needed


