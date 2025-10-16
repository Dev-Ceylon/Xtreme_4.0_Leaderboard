import requests
import csv
import json
from datetime import datetime
import time

def fetch_leaderboard_with_headers(contest_slug, offset=0, limit=100):
    """
    Fetch leaderboard data from HackerRank with proper headers
    """
    url = f"https://www.hackerrank.com/rest/contests/{contest_slug}/leaderboard"
    
    # Add headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': f'https://www.hackerrank.com/contests/{contest_slug}/leaderboard',
        'Origin': 'https://www.hackerrank.com',
    }
    
    params = {
        'offset': offset,
        'limit': limit
    }
    
    try:
        print(f"Attempting to fetch data (offset: {offset})...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def manual_json_input():
    """
    Allow user to manually paste JSON data
    """
    print("\n" + "="*60)
    print("MANUAL DATA ENTRY MODE")
    print("="*60)
    print("\nPlease follow these steps:")
    print("1. Open your browser and go to:")
    print(f"   https://www.hackerrank.com/contests/sliit-xtreme-25/leaderboard")
    print("\n2. Open Browser Developer Tools (F12)")
    print("3. Go to the 'Network' tab")
    print("4. Refresh the page")
    print("5. Look for a request to 'leaderboard' in the Network tab")
    print("6. Click on it and copy the JSON response")
    print("\n7. Paste the JSON data below and press Enter twice:")
    print("-"*60)
    
    lines = []
    print("\nPaste JSON data (press Enter twice when done):\n")
    
    while True:
        line = input()
        if line == "" and len(lines) > 0:
            break
        lines.append(line)
    
    json_str = '\n'.join(lines)
    
    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"\nError parsing JSON: {e}")
        return None

def generate_csv_from_data(data, output_file='leaderboard.csv'):
    """
    Generate CSV file from leaderboard data
    """
    if not data or 'models' not in data:
        print("Invalid data format. Expected 'models' key in JSON.")
        return False
    
    participants = data['models']
    
    if not participants:
        print("No participants found in data.")
        return False
    
    print(f"\nWriting {len(participants)} participants to {output_file}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
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
    
    print(f"✓ CSV file generated successfully: {output_file}")
    print(f"✓ Total participants: {len(participants)}")
    
    # Generate metadata
    metadata = {
        'total_participants': len(participants),
        'generated_at': datetime.now().isoformat(),
        'top_score': participants[0].get('score', 0) if participants else 0
    }
    
    with open('leaderboard_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata file generated: leaderboard_metadata.json")
    return True

def generate_sample_csv():
    """
    Generate a sample CSV file for testing
    """
    print("\nGenerating sample CSV file for testing...")
    
    sample_data = []
    for i in range(1, 51):
        sample_data.append({
            'rank': i,
            'hacker': f'participant_{i}',
            'score': max(0, 100 - (i * 2)),
            'time_taken': 3600 + (i * 60),
            'country': ['Sri Lanka', 'India', 'USA', 'UK', 'Australia'][i % 5],
            'school': 'SLIIT',
            'avatar': ''
        })
    
    with open('sample_leaderboard.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['rank', 'hacker', 'score', 'time_taken', 'country', 'school', 'avatar']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    print("✓ Sample CSV generated: sample_leaderboard.csv")
    print("✓ You can use this file to test the leaderboard webpage")

if __name__ == "__main__":
    CONTEST_SLUG = 'sliit-xtreme-25'
    OUTPUT_FILE = 'leaderboard.csv'
    
    print("=" * 60)
    print("HackerRank Leaderboard CSV Generator")
    print("=" * 60)
    print()
    
    # Try automatic fetch first
    print("Attempting automatic data fetch...")
    all_participants = []
    offset = 0
    limit = 100
    
    # Try to fetch first page
    data = fetch_leaderboard_with_headers(CONTEST_SLUG, offset, limit)
    
    if data and 'models' in data:
        print("✓ Automatic fetch successful!")
        
        # Fetch all pages
        while True:
            if not data or 'models' not in data:
                break
            
            participants = data['models']
            if not participants:
                break
            
            all_participants.extend(participants)
            print(f"Fetched {len(participants)} participants (Total: {len(all_participants)})")
            
            if len(participants) < limit:
                break
            
            offset += limit
            time.sleep(1)  # Be nice to the server
            data = fetch_leaderboard_with_headers(CONTEST_SLUG, offset, limit)
        
        if all_participants:
            generate_csv_from_data({'models': all_participants}, OUTPUT_FILE)
    else:
        print("✗ Automatic fetch failed (403 Forbidden)")
        print("\nThis usually means:")
        print("- The API requires authentication")
        print("- The contest is private")
        print("- Rate limiting is in effect")
        
        print("\n" + "="*60)
        print("CHOOSE AN OPTION:")
        print("="*60)
        print("1. Manual JSON input (paste data from browser)")
        print("2. Generate sample CSV for testing")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            data = manual_json_input()
            if data:
                generate_csv_from_data(data, OUTPUT_FILE)
            else:
                print("\n✗ Failed to parse JSON data")
        elif choice == '2':
            generate_sample_csv()
        else:
            print("\nExiting...")
    
    print()
    print("=" * 60)
    print("Process completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open leaderboard.html in your browser")
    print("2. Upload the generated CSV file")
    print("3. View your leaderboard!")
    print("="*60)