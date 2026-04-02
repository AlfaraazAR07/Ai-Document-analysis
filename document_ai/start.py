#!/usr/bin/env python3
"""
Simple startup script for Document AI API
"""
import os
import sys
import subprocess

def main():
    print("Starting Document AI API...")
    print()
    
    # Set PYTHONPATH
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = script_dir
    
    print(f"PYTHONPATH set to: {script_dir}")
    print()
    
    # Check if Redis is running
    print("Checking Redis connection...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
        r.ping()
        print("Redis is running")
    except Exception as e:
        print(f"Warning: Redis is not running or not accessible: {e}")
        print("  - Async tasks will not work without Redis")
        print("  - The API will still work in synchronous mode")
    print()
    
    # Start uvicorn
    print("Starting Uvicorn server...")
    print("API will be available at: http://127.0.0.1:8000")
    print("API documentation at: http://127.0.0.1:8000/docs")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 60)
    
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, cwd=script_dir, check=True)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Server stopped")
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"Server failed to start: {e}")
        return 1
    except FileNotFoundError:
        print("\n" + "=" * 60)
        print("Error: uvicorn not found")
        print("Please install dependencies: pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
