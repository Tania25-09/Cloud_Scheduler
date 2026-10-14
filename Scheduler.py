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
                    f"Stop request submitted for EC2 instance: {instance_id}"
                )

            except Exception as e:

                print(f"Failed to stop {instance_id}: {e}")

                logger.error(
                    f"Failed to stop {instance_id}: {e}"
                )

        else:
            print(f"Skipping {instance_id}: current state is {state}")
            logger.info(
                f"Skipping EC2 instance {instance_id}: current state is {state}"
            ) 
# --------------------------------------------------
# Send SNS notification
# --------------------------------------------------

def send_notification(message):

    """Send an email notification using AWS SNS."""

    try:
        sns = boto3.client(
            "sns",
            region_name=REGION
        )

        response = sns.publish(
            TopicArn="arn:aws:sns:ap-south-1:929677619941:EC2AutoSchedulerNotifications",
            Subject="Cloud Resource Auto-Scheduler Alert",
            Message=message
        )

        logger.info(
            f"SNS notification sent. Message ID: {response['MessageId']}"
        )

        print("Notification sent successfully.")

    except Exception as e:

        logger.exception(
            f"Failed to send SNS notification: {e}"
        )

        print(f"Failed to send notification: {e}")


# --------------------------------------------------
# Main program
# --------------------------------------------------

if __name__ == "__main__":

    try:

        if len(sys.argv) < 2:

            print("Usage:")
            print("  python Scheduler.py status")
            print("  python Scheduler.py start")
            print("  python Scheduler.py stop")

            sys.exit(1)

        command = sys.argv[1].lower()

        if command == "notify-test":
            send_notification(
                "EC2 Scheduled Shutdown Reminder\n\n"
                "Your scheduled EC2 instance will be stopped "
                "in 10 minutes. Please save your work."
            )
            sys.exit(0)

        if command == "status":

            show_status()

        elif command == "start":

            start_instances()

        elif command == "stop":

            stop_instances()

        else:

            print("Invalid command.")
            print("Use: status, start, or stop")

    except Exception as e:

        print(f"Unexpected error: {e}")

        logger.exception(
            f"Unexpected scheduler error: {e}"
        )
