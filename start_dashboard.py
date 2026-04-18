import subprocess
import os
import time
import webbrowser
import signal

def kill_port(port):
    """Kill process listening on a specific port on Windows."""
    try:
        command = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(command, shell=True).decode()
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) > 4:
                pid = parts[-1]
                if pid != '0':
                    print(f"Cleaning up port {port} (PID: {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
    except:
        pass

def start_system():
    # 0. Clean up any existing instances
    print("Pre-flight system check: Cleaning up active ports...")
    for port in [8000, 8800, 2100]:
        kill_port(port)
    
    time.sleep(1)

    # 1. Start the backend servers
    print("Starting FTP/Web Backend Servers...")
    python_exe = os.path.join(".venv", "Scripts", "python.exe")
    subprocess.Popen([python_exe, "run_servers.py"])
    
    # 2. Start the FastAPI API
    print("Starting FastAPI Orchestrator API...")
    # Add environment variable to suppress warnings
    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"
    subprocess.Popen([python_exe, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"], env=env)

    # Wait for API to be ready
    time.sleep(2)

    # 3. Open the UI via the API server
    print("System ready. Opening Dashboard...")
    webbrowser.open("http://localhost:8000/dashboard/")

if __name__ == "__main__":
    start_system()

if __name__ == "__main__":
    start_system()
