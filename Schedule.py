import json
from datetime import datetime
import subprocess
import os

# Load configuration
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)

# Current date and time
now = datetime.now()

current_time = now.strftime("%H:%M")
current_day = now.isoweekday()

start_time = config["start_time"]
stop_time = config["stop_time"]
weekdays = config["weekdays"]
weekend_shutdown = config["weekend_shutdown"]

print(f"Current time: {current_time}")
print(f"Current day: {current_day}")


# Weekday schedule
if current_day in weekdays:

    if current_time == start_time:
        print("Start time reached. Starting EC2 instances...")

        subprocess.run([
            "/home/ubuntu/Cloud_Scheduler/venv/bin/python",
            "/home/ubuntu/Cloud_Scheduler/Scheduler.py",
            "start"
        ])

    elif current_time == stop_time:
        print("Stop time reached. Stopping EC2 instances...")

        subprocess.run([
            "/home/ubuntu/Cloud_Scheduler/venv/bin/python",
            "/home/ubuntu/Cloud_Scheduler/Scheduler.py",
            "stop"
        ])

    else:
        print("No scheduled action at this time.")


# Weekend schedule
elif weekend_shutdown:

    print("Weekend detected.")

    # Stop instances only once at the beginning of the weekend
    if current_day == 6 and current_time == "00:00":

        print("Weekend shutdown time reached. Stopping EC2 instances...")

        subprocess.run([
            "/home/ubuntu/Cloud_Scheduler/venv/bin/python",
            "/home/ubuntu/Cloud_Scheduler/Scheduler.py",
            "stop"
        ])

    else:
        print("Weekend shutdown already handled or not yet scheduled.")


else:
    print("No weekend shutdown configured.")
