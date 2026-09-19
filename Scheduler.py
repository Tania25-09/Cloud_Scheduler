import boto3
import sys
import json
import os
import logging


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(
    BASE_DIR,
    "scheduler_actions.log"
)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Load configuration
# --------------------------------------------------

CONFIG_PATH = os.path.join(
    BASE_DIR,
    "config.json"
)

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)


# --------------------------------------------------
# AWS configuration
# --------------------------------------------------

REGION = "ap-south-1"

ec2 = boto3.client(
    "ec2",
    region_name=REGION
)


# --------------------------------------------------
# Get scheduled EC2 instances
# --------------------------------------------------

def get_scheduled_instances():

    """Get all EC2 instances with AutoSchedule=true."""

    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:AutoSchedule",
                "Values": ["true"]
            }
        ]
    )

    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append(instance)

    return instances


# --------------------------------------------------
# Show instance status
# --------------------------------------------------

def show_status():

    """Show current status of scheduled instances."""

    instances = get_scheduled_instances()

    if not instances:
        print("No AutoSchedule instances found.")
        return

    print("Cloud Resource Auto-Scheduler")
    print("-" * 50)

    for instance in instances:

        instance_id = instance["InstanceId"]
        state = instance["State"]["Name"]

        name = "Unnamed"

        for tag in instance.get("Tags", []):

            if tag["Key"] == "Name":
                name = tag["Value"]

        print(f"Name: {name}")
        print(f"Instance ID: {instance_id}")
        print(f"State: {state}")
        print("-" * 50)


# --------------------------------------------------
# Start EC2 instances
# --------------------------------------------------

def start_instances():

    """Start stopped scheduled instances."""

    instances = get_scheduled_instances()

    for instance in instances:

        instance_id = instance["InstanceId"]
        state = instance["State"]["Name"]

        if state == "stopped":

            print(f"Starting instance: {instance_id}")

            try:

                ec2.start_instances(
                    InstanceIds=[instance_id]
                )

                logger.info(
                    f"Started EC2 instance: {instance_id}"
                )

            except Exception as e:

                print(f"Failed to start {instance_id}: {e}")

                logger.error(
                    f"Failed to start {instance_id}: {e}"
                )

        else:

            print(
                f"{instance_id} is already {state}"
            )


# --------------------------------------------------
# Stop EC2 instances
# --------------------------------------------------

def stop_instances():

    """Stop running scheduled instances."""

    instances = get_scheduled_instances()

    for instance in instances:

        instance_id = instance["InstanceId"]
        state = instance["State"]["Name"]

        if state == "running":

            print(f"Stopping instance: {instance_id}")

            try:

                ec2.stop_instances(
                    InstanceIds=[instance_id]
                )

                logger.info(
                    f"Stopped EC2 instance: {instance_id}"
                )

            except Exception as e:

                print(f"Failed to stop {instance_id}: {e}")

                logger.error(
                    f"Failed to stop {instance_id}: {e}"
                )

        else:

            print(
                f"{instance_id} is already {state}"
            )


# --------------------------------------------------
# Main program
# --------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Usage:")
        print("  python Scheduler.py status")
        print("  python Scheduler.py start")
        print("  python Scheduler.py stop")

        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "status":

        show_status()

    elif command == "start":

        start_instances()

    elif command == "stop":

        stop_instances()

    else:

        print("Invalid command.")
        print("Use: status, start, or stop")
