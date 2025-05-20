import os

LOG_FILE_PATH = "karma_bot.log"

def display_logs():
    """Read and display the log data from the log file."""
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Log file '{LOG_FILE_PATH}' does not exist.")
        return

    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            logs = log_file.readlines()
            print("=== Bot Activity Logs ===")
            for line in logs:
                print(line.strip())
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    display_logs()
