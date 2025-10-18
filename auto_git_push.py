import os
import subprocess
import time

# === Configuration ===
CHECK_INTERVAL = 10  # seconds between checks
COMMIT_MESSAGE = "Leaderboard Update"

def run_command(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def check_for_changes():
    """Check if there are any uncommitted changes."""
    stdout, _ = run_command("git status --porcelain")
    return bool(stdout)  # True if there are changes

def auto_commit_push():
    """Commit and push all changes if any."""
    print("🔍 Checking for changes...")
    if check_for_changes():
        print("🟡 Changes detected! Committing and pushing...")
        run_command("git add .")
        run_command(f'git commit -m "{COMMIT_MESSAGE}"')
        stdout, stderr = run_command("git push")
        print(stdout or stderr)
        print("✅ Changes pushed successfully.\n")
    else:
        print("✅ No changes detected.\n")

if __name__ == "__main__":
    print("🚀 Auto Git Push Script Started")
    print(f"Will check for changes every {CHECK_INTERVAL} seconds...\n")

    try:
        while True:
            auto_commit_push()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user.")
