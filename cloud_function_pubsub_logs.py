import sys
import os
sys.path.insert(1, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "packages"
))
from google.cloud import pubsub
import base64
import json
from google.cloud import logging

def process_pubsub_message(event, context):
    # Initialize the Cloud Logging client
    client = logging.Client()
    # Define the logname for the custom logs. This will be custom log table name in BQ dataset.
    logger = client.logger("ML_Platform_Custom_Logs")

    try:
        if "data" in event:
            # Decode and parse the Pub/Sub message data
            pubsub_message = base64.b64decode(event["data"]).decode('utf-8')
            pubsub_data = json.loads(pubsub_message)
            
            # Create a dictionary to hold the log data
            log_entry = {}
            
            # Load the log data into the desired fields
            log_entry["severity"] = pubsub_data["level"]
            log_entry["jsonPayload.message"] = pubsub_data["message"]
            log_entry["jsonPayload.created_at"] = pubsub_data["created_at"]
            log_entry["jsonPayload.principal_email"] = pubsub_data.get("principal_email")
            log_entry["sourceLocation.line"] = pubsub_data.get("line_number")
            log_entry["sourceLocation.function"] = pubsub_data.get("function_name")
            log_entry["sourceLocation.file"] = pubsub_data.get("file_name")
            log_entry["sourceLocation.module_path"] = pubsub_data.get("module_path")
            
            # Load the remaining payload data into jsonPayload.payload
            payload = {key: value for key, value in pubsub_data.items() if key not in [
                "level", "message", "created_at", "principal_email", 
                "line_number", "function_name", "file_name", "module_path"
            ]}
            log_entry["jsonPayload.payload"] = payload
            
            # Log the processed data
            logger.log_struct(log_entry)
    except Exception as e:
        # Log the exception and return an error message
        logger.log_text(f"Error processing Pub/Sub message: {str(e)}")
        return f"Error: {str(e)}"

    try:
        if "ackId" in event and "subscription" in event:
            # Acknowledge the Pub/Sub message
            ack_id = event['ackId']
            subscription_path = event['subscription']
            subscriber = pubsub.SubscriberClient()
            subscriber.acknowledge(subscription=subscription_path, ack_ids=[ack_id])
        else:
            raise ValueError("Missing ackId or subscription path")
    except Exception as e:
        # Log the exception and return an error message
        logger.log_text(f"Error acknowledging Pub/Sub message: {str(e)}")
        return f"Error: {str(e)}"

    # If we reached this point, the message was processed successfully
    return "Message Processed Successfully"
