"""
Main entry point for the Robotaxi OSINT Agent.
"""
import json
import logging
from datetime import datetime, UTC
from typing import List, Optional
from pathlib import Path

from config import Config
from models import SightingCandidate
from reddit_poller import RedditPoller
from llm_analyzer import LLMAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('robotaxi_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RobotaxiAgent:
    """Main orchestrator for the OSINT agent."""
    
    def __init__(self):
        """Initialize the agent with all components."""
        Config.validate()
        self.poller = RedditPoller()
        self.analyzer = LLMAnalyzer()
        self.output_file = Path(Config.OUTPUT_FILE)
        self.state_file = Path(Config.STATE_FILE)
        self.last_check = self._load_last_check()
        logger.info("RobotaxiAgent initialized")
    
    def _load_last_check(self) -> Optional[datetime]:
        """Load the last check timestamp from state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    last_check_str = state.get('last_check')
                    if last_check_str:
                        # Parse ISO format string and ensure UTC timezone
                        # Handle different formats
                        last_check_str = last_check_str.strip()
                        # Remove trailing 'Z' if present
                        if last_check_str.endswith('Z'):
                            last_check_str = last_check_str[:-1] + '+00:00'
                        # Handle double timezone issue (e.g., "2025-12-28T21:18:40.323267+00:00+00:00")
                        if last_check_str.count('+00:00') > 1:
                            last_check_str = last_check_str.replace('+00:00+00:00', '+00:00')
                        dt = datetime.fromisoformat(last_check_str)
                        # Ensure timezone-aware (UTC)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=UTC)
                        return dt
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"Could not parse state file: {e}")
        return None
    
    def _save_last_check(self, timestamp: datetime):
        """Save the last check timestamp to state file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_check': timestamp.isoformat() + "Z"
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
    
    def _load_existing_candidates(self) -> List[dict]:
        """Load existing candidates from the output file."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("Could not parse existing candidates file")
                return []
        return []
    
    def _save_candidates(self, candidates: List[SightingCandidate]):
        """Save candidates to the output file."""
        # Load existing candidates
        existing = self._load_existing_candidates()
        existing_dict = {c['source_id']: c for c in existing}
        
        # Add new candidates or update existing ones
        new_count = 0
        updated_count = 0
        for candidate in candidates:
            candidate_dict = candidate.model_dump(mode='json')
            source_id = candidate.source_id
            
            if source_id not in existing_dict:
                # New candidate
                existing.append(candidate_dict)
                new_count += 1
            else:
                # Update existing candidate (replace with newer data)
                existing_index = next(i for i, c in enumerate(existing) if c['source_id'] == source_id)
                existing[existing_index] = candidate_dict
                updated_count += 1
        
        # Save to file
        with open(self.output_file, 'w') as f:
            json.dump(existing, f, indent=2, default=str)
        
        if new_count > 0 or updated_count > 0:
            logger.info(f"Saved {new_count} new candidate(s) and updated {updated_count} existing candidate(s) to {self.output_file}")
            logger.info(f"Total candidates in file: {len(existing)}")
        else:
            logger.info(f"No changes to save")
    
    def run_once(self) -> int:
        """
        Run a single scan cycle.
        
        Returns:
            Number of valid candidates found
        """
        logger.info("=" * 60)
        logger.info("Starting scan cycle")
        logger.info("=" * 60)
        
        # Fetch posts
        if self.last_check:
            logger.info(f"Fetching posts since last check: {self.last_check}")
            candidates = self.poller.fetch_new_posts_since(self.last_check)
        else:
            logger.info("No previous state found, fetching recent posts from last day")
            candidates = self.poller.fetch_recent_posts(limit=50, time_filter="day")
        
        # Update and save last check timestamp
        self.last_check = datetime.now(UTC)
        self._save_last_check(self.last_check)
        
        if not candidates:
            logger.info("No potential candidates found in this cycle")
            return 0
        
        # Analyze each candidate
        valid_candidates = []
        for candidate in candidates:
            analyzed = self.analyzer.analyze(candidate)
            
            # Only save candidates with decent confidence
            if analyzed.confidence_score >= 0.5:
                valid_candidates.append(analyzed)
        
        # Save results
        if valid_candidates:
            self._save_candidates(valid_candidates)
            logger.info(f"Found {len(valid_candidates)} valid sightings")
        else:
            logger.info("No high-confidence candidates found")
        
        return len(valid_candidates)


def main():
    """Main entry point."""
    agent = RobotaxiAgent()
    valid_count = agent.run_once()
    logger.info(f"Scan complete. Found {valid_count} valid candidates.")


if __name__ == "__main__":
    main()
