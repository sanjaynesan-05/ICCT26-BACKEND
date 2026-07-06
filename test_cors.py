import subprocess
import time
import urllib.request
import urllib.error
import sys

print("Starting backend server for testing...")
proc = subprocess.Popen(["cmd.exe", "/c", "run_server.bat"])

print("Waiting 10 seconds for server to start...")
time.sleep(10)

print("Testing CORS request for Origin: https://icct27.netlify.app")
req = urllib.request.Request("http://127.0.0.1:8000/")
req.add_header("Origin", "https://icct27.netlify.app")
req.add_header("Access-Control-Request-Method", "GET")
req.get_method = lambda: "OPTIONS"

try:
    with urllib.request.urlopen(req) as response:
        print(f"\n--- SUCCESS ---")
        print(f"Status: {response.status}")
        print("CORS Headers received:")
        for k, v in response.headers.items():
            if 'access-control' in k.lower():
                print(f"{k}: {v}")
except urllib.error.URLError as e:
    print(f"\n--- ERROR ---")
    print(f"Error connecting: {e}")

# Kill the process tree (cmd -> batch -> python)
subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("\nTest completed.")
