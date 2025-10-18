import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import schedule

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leaderboard_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LeaderboardFetcher:
    def __init__(self, contest_slug, output_file='leaderboard.csv'):
        self.contest_slug = contest_slug
        self.output_file = output_file
        self.base_url = f"https://www.hackerrank.com/rest/contests/{contest_slug}/leaderboard"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://www.hackerrank.com/contests/{contest_slug}/leaderboard',
            'Origin': 'https://www.hackerrank.com',
        }
        
    def fetch_page(self, offset=0, limit=100):
        """Fetch a single page of leaderboard data"""
        params = {'offset': offset, 'limit': limit}
        
        try:
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=self.headers, 
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data at offset {offset}: {e}")
            return None
    
    def fetch_all_participants(self):
        """Fetch all participants from all pages"""
        all_participants = []
        offset = 0
        limit = 100
        
        logger.info("Starting data fetch...")
        
        while True:
            data = self.fetch_page(offset, limit)
            
            if not data or 'models' not in data:
                break
            
            participants = data['models']
            if not participants:
                break
            
            all_participants.extend(participants)
            logger.info(f"Fetched {len(participants)} participants (Total: {len(all_participants)})")
            
            if len(participants) < limit:
                break
            
            offset += limit
            time.sleep(1)  # Rate limiting
        
        return all_participants
    
    def generate_csv(self, participants):
        """Generate CSV file from participant data"""
        if not participants:
            logger.warning("No participants to write")
            return False
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['rank', 'hacker', 'score', 'time_taken', 'country', 'school', 'avatar']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for participant in participants:
                    writer.writerow({
                        'rank': participant.get('rank', ''),
                        'hacker': participant.get('hacker', ''),
                        'score': participant.get('score', 0),
                        'time_taken': participant.get('time_taken', 0),
                        'country': participant.get('country', ''),
                        'school': participant.get('school', ''),
                        'avatar': participant.get('avatar', '')
                    })
            
            logger.info(f"✓ CSV file generated: {self.output_file} ({len(participants)} participants)")
            
            # Generate metadata
            metadata = {
                'total_participants': len(participants),
                'generated_at': datetime.now().isoformat(),
                'top_score': participants[0].get('score', 0) if participants else 0,
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open('leaderboard_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✓ Metadata updated")
            return True
            
        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            return False
    
    def update_leaderboard(self):
        """Main update function"""
        logger.info("="*60)
        logger.info("Starting leaderboard update")
        logger.info("="*60)
        
        try:
            participants = self.fetch_all_participants()
            
            if participants:
                success = self.generate_csv(participants)
                if success:
                    logger.info("✓ Leaderboard updated successfully")
                    return True
                else:
                    logger.error("✗ Failed to generate CSV")
                    return False
            else:
                logger.error("✗ No participants fetched")
                return False
                
        except Exception as e:
            logger.error(f"✗ Update failed with exception: {e}")
            return False


def run_automation(contest_slug='sliitxtreme-4-final', interval_minutes=15):
    """
    Run the leaderboard fetcher automatically at specified intervals
    """
    fetcher = LeaderboardFetcher(contest_slug)
    
    # Run once immediately on startup
    logger.info("Running initial update...")
    fetcher.update_leaderboard()
    
    # Schedule regular updates
    schedule.every(interval_minutes).minutes.do(fetcher.update_leaderboard)
    
    logger.info(f"Scheduler started. Updates every {interval_minutes} minutes.")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*60)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("Automation stopped by user")
        logger.info("="*60)


if __name__ == "__main__":
    # Configuration
    CONTEST_SLUG = 'sliitxtreme-4-final'
    INTERVAL_MINUTES = 15
    
    print("="*60)
    print("HackerRank Leaderboard - Automated Fetcher")
    print("="*60)
    print(f"Contest: {CONTEST_SLUG}")
    print(f"Update Interval: {INTERVAL_MINUTES} minutes")
    print(f"Output File: leaderboard.csv")
    print(f"Log File: leaderboard_automation.log")
    print("="*60)
    print()
    
    # Check if schedule module is installed
    try:
        import schedule
        run_automation(CONTEST_SLUG, INTERVAL_MINUTES)
    except ImportError:
        print("ERROR: 'schedule' module not found")
        print("Please install it using: pip install schedule")
        print()
        print("Or install all requirements: pip install -r requirements.txt")