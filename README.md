# Robotaxi OSINT Agent

An autonomous intelligence agent that monitors public forums and social media for Tesla Robotaxi sightings.

> **Status:** MVP done

## Phase 1: Reddit MVP ✅

## Features

- **Reddit Monitoring**: Monitors r/TeslaLounge, r/SelfDrivingCars, and r/teslamotors using public JSON endpoints (no API credentials required!)
- **Keyword Filtering**: Fast heuristic filtering using keywords like "robotaxi", "cybercab", "manufacturer plate"
- **LLM Analysis**: Uses GPT-4o-mini to extract structured data from posts
- **Image Support**: Extracts and processes images from Reddit posts
- **Deduplication**: Prevents duplicate alerts for the same post
- **JSON Output**: Stores candidates in a structured format for downstream processing

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

- `OPENAI_API_KEY`: Your OpenAI API key

**Note:** No Reddit API credentials needed! The agent uses Reddit's public JSON endpoints.

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

- ✅ Phase 1: Reddit MVP (Current)
- ⬜ Phase 2: Add support for scraping X posts through Google Search and improve agent with LangGraph
- ⬜ Phase 3: Integrate with robotaxi tracker repo once it becomes open-source

