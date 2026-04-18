import sys
import io

# Force UTF-8 encoding for stdout and stderr to handle special characters on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import json
import sqlite3
from typing import List, Dict
import actions.agent_actions
import threading
import queue

app = FastAPI(title="Cyber Agent API")

# Mount the UI directory to serve static files
app.mount("/dashboard", StaticFiles(directory="ui", html=True), name="ui")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active processes or logs
logs_queue = queue.Queue()

@app.get("/scenarios")
async def get_scenarios():
    """List all available scenarios."""
    return list(actions.agent_actions.scenarios.keys())

@app.get("/server-status")
async def get_server_status():
    """Check if the backend servers are reachable."""
    # This is a simplified check
    return {
        "http_server": "Running", # We assume since it's managed by the same system
        "ftp_server": "Running"
    }

@app.post("/run/{scenario_name}")
async def run_scenario_endpoint(scenario_name: str):
    """Run a specific scenario and return the output."""
    if scenario_name not in actions.agent_actions.scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        # Run using the venv python
        python_exe = os.path.join(".venv", "Scripts", "python.exe")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [python_exe, "run_agents.py", scenario_name],
            capture_output=True,
            env=env,
            check=True
        )
        return {"output": result.stdout.decode("utf-8", errors="replace"), "error": result.stderr.decode("utf-8", errors="replace")}
    except subprocess.CalledProcessError as e:
        return {"output": e.stdout.decode("utf-8", errors="replace"), "error": e.stderr.decode("utf-8", errors="replace"), "status": "error"}

@app.get("/logs")
async def get_logs(limit: int = 20):
    """Fetch recent messages from logs.db if available."""
    if not os.path.exists("logs.db"):
        return []
    
    try:
        conn = sqlite3.connect("logs.db")
        cursor = conn.cursor()
        # Query based on AutoGen's log schema (assuming it has chat_messages or similar)
        # Standard AutoGen db logging has 'chat_messages' table
        cursor.execute("SELECT sender, recipient, content, timestamp FROM chat_messages ORDER BY timestamp DESC LIMIT ?", (limit,))
        logs = [{"sender": r[0], "recipient": r[1], "content": r[2], "timestamp": r[3]} for r in cursor.fetchall()]
        conn.close()
        return logs
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
