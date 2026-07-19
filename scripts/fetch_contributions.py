#!/usr/bin/env python3
"""
Fetch GitHub contribution data from public profile.
No token required - scrapes the contributions HTML.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', 'beautifulsoup4'], check=True)
    import requests
    from bs4 import BeautifulSoup

USERNAME = "softwarelincoln26"


def fetch_contributions(username=None):
    """Fetch contribution data from GitHub profile"""
    if username is None:
        username = USERNAME

    url = f"https://github.com/users/{username}/contributions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }

    print(f"Fetching contributions for {username}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching contributions: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    days = soup.find_all('td', class_='ContributionCalendar-day')

    contributions = []
    for day in days:
        date = day.get('data-date')
        count_str = day.get('data-level', '0')
        tooltip = day.get('aria-label', '')

        try:
            count = int(count_str)
        except ValueError:
            count = 0

        if date:
            contributions.append({
                'date': date,
                'count': count,
                'tooltip': tooltip
            })

    contributions.sort(key=lambda x: x['date'])

    stats = calculate_stats(contributions)

    result = {
        'username': username,
        'fetched_at': datetime.now().isoformat(),
        'total_contributions': len([c for c in contributions if c['count'] > 0]),
        'days': contributions,
        'stats': stats
    }

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    output_path = data_dir / "contributions.json"
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Saved {len(contributions)} days to {output_path}")

    return result


def calculate_stats(contributions):
    """Calculate useful stats from contribution data"""
    if not contributions:
        return {}

    active_days = [c for c in contributions if c['count'] > 0]

    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    for c in reversed(contributions):
        if c['count'] > 0:
            temp_streak += 1
            current_streak = max(current_streak, temp_streak)
        else:
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            temp_streak = 0

    if temp_streak > longest_streak:
        longest_streak = temp_streak

    best_day = max(contributions, key=lambda x: x['count']) if contributions else None

    monthly = {}
    for c in contributions:
        month = c['date'][:7]
        monthly[month] = monthly.get(month, 0) + c['count']

    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'best_day': best_day,
        'active_days': len(active_days),
        'monthly': monthly
    }


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else None
    fetch_contributions(username)
