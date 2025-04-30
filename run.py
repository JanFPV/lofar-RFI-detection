import sys
import subprocess

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error. Please provide the directory to watch.")
        sys.exit(1)
    watch_dir = sys.argv[1]
    subprocess.run(["python", "scripts/realtime_movie_generation.py", watch_dir])
