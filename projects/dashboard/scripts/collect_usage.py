"""
Usage Statistics Collector
Reads session files and updates usage_stats in the database
"""
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

OPENCLAW_DIR = Path(r"C:\Users\Administrator\.openclaw")
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "dashboard.db"

# Cost per 1K tokens (default values)
COSTS = {
    'claude-opus-4-5': {'input': 0.015, 'output': 0.075},
    'claude-sonnet-4-20250514': {'input': 0.003, 'output': 0.015},
    'gpt-4o': {'input': 0.005, 'output': 0.015},
}

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def collect_session_usage():
    """Collect usage from session files"""
    sessions_dir = OPENCLAW_DIR / "sessions"
    if not sessions_dir.exists():
        print("No sessions directory found")
        return
    
    conn = get_db()
    c = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    total_input = 0
    total_output = 0
    session_count = 0
    
    for session_file in sessions_dir.glob("*.json"):
        try:
            with open(session_file) as f:
                data = json.load(f)
            
            # Extract token usage if available
            if 'usage' in data:
                usage = data['usage']
                total_input += usage.get('input_tokens', 0)
                total_output += usage.get('output_tokens', 0)
            
            session_count += 1
            
        except Exception as e:
            print(f"Error reading {session_file}: {e}")
    
    # Calculate estimated cost
    model = 'claude-opus-4-5'  # Default model
    cost_config = COSTS.get(model, {'input': 0.01, 'output': 0.03})
    estimated_cost = (total_input / 1000 * cost_config['input']) + (total_output / 1000 * cost_config['output'])
    
    # Update or insert today's stats
    c.execute('''
        INSERT INTO usage_stats (date, model, input_tokens, output_tokens, cost, session_count)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            input_tokens = input_tokens + excluded.input_tokens,
            output_tokens = output_tokens + excluded.output_tokens,
            cost = cost + excluded.cost,
            session_count = session_count + excluded.session_count
    ''', (today, model, total_input, total_output, estimated_cost, session_count))
    
    conn.commit()
    conn.close()
    
    print(f"Collected: {session_count} sessions, {total_input} input tokens, {total_output} output tokens")

if __name__ == '__main__':
    collect_session_usage()
