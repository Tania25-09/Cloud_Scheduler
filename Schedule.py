import json
from datetime import datetime, timedelta
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python")
SCHEDULER = os.path.join(BASE_DIR, "Scheduler.py")

# Load configuration
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)

# Current date and time
now = datetime.now()
current_time = now.strftime("%H:%M")
current_day = now.isoweekday()

# Use a separate notification marker for each date
NOTIFICATION_MARKER = os.path.join(
    BASE_DIR,
    f".notification_sent_{now.strftime('%Y-%m-%d')}"
)

start_time = config["start_time"]
stop_time = config["stop_time"]

stop_datetime = datetime.strptime(stop_time, "%H:%M")
notification_time = (
    stop_datetime - timedelta(minutes=10)
).strftime("%H:%M")

weekdays = config["weekdays"]
weekend_shutdown = config["weekend_shutdown"]

print(f"Current time: {current_time}")
print(f"Current day: {current_day}")

# Weekday schedule
if current_day in weekdays:

    if current_time == start_time:
        print("Start time reached. Starting EC2 instances...")
        subprocess.run([PYTHON, SCHEDULER, "start"], check=False)

    elif current_time == notification_time:
        if not os.path.exists(NOTIFICATION_MARKER):
            print("Sending pre-stop notification...")

            result = subprocess.run(
                [PYTHON, SCHEDULER, "notify-test"],
                check=False
            )

            if result.returncode == 0:
                with open(NOTIFICATION_MARKER, "w") as marker:
                    marker.write(now.strftime("%Y-%m-%d"))

                print("Pre-stop notification command completed.")
            else:
                print("Notification command failed; it can be retried.")
        else:
            print("Notification already attempted successfully today.")

    elif current_time == stop_time:
        print("Stop time reached. Stopping EC2 instances...")
        subprocess.run([PYTHON, SCHEDULER, "stop"], check=False)

    else:
        print("No scheduled action at this time.")

# Weekend schedule
elif weekend_shutdown:
    print("Weekend detected.")

    # Check every 15 minutes on Saturday and Sunday
    if current_day in (6, 7) and now.minute % 15 == 0:
        print("Weekend shutdown check: stopping running tagged instances...")
        result = subprocess.run(
            [PYTHON, SCHEDULER, "stop"],
            check=False
        )

        if result.returncode != 0:
            print("Weekend shutdown command failed.")
    else:
        print("No weekend shutdown check due at this minute.")

else:
    print("No weekend shutdown configured.")
