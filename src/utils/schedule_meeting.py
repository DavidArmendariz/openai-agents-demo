import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from azure.identity.aio import ClientSecretCredential
from dotenv import load_dotenv
from twilio.rest import Client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# Azure AD App Credentials
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
TENANT_ID = os.getenv("AZURE_TENANT_ID", "")

# Microsoft Graph API Base URL
GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
SCOPES = ["https://graph.microsoft.com/.default"]


async def get_access_token():
    """Get an access token for Microsoft Graph API"""
    credentials = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    token = await credentials.get_token(*SCOPES)
    await credentials.close()  # Close the credential client
    return token.token


def send_whatsapp_message(recipient, join_url):
    try:
        logger.info(
            f"Sending WhatsApp to recipient: {recipient} from {TWILIO_WHATSAPP_NUMBER}"
        )
        twilio_client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{recipient}",
            content_sid="HXbbc61c499a13f0ad5b3e0d7ec623efb9",
            messaging_service_sid="MG25fa851494b7c11ceef8704674d0ca7b",
            content_variables=json.dumps({"1": join_url}),
        )
    except Exception as e:
        logger.error("Error sending WhatsApp message: %s", e, exc_info=True)


async def schedule_meeting(event_data) -> dict[str, Any]:
    """Create a meeting using Microsoft Graph API with HTTP requests"""
    try:
        # Get access token
        access_token = await get_access_token()

        # Extract meeting details
        start_time_str = event_data.get("start_datetime", "2025-04-07T15:00:00Z")
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        end_time = start_time + timedelta(minutes=30)
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        subject = event_data.get("subject", "Cita con Australian Option")
        recipients = event_data.get("recipients", [])

        # User ID should be configured as env variable or passed in the request
        user_id = os.getenv("MICROSOFT_USER_ID", "79cb5e1e-583a-4cac-a015-320bd9ca0356")

        # Prepare headers for all requests
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Create a client session explicitly with connector
        connector = aiohttp.TCPConnector()
        session = aiohttp.ClientSession(connector=connector)

        try:
            # Get user's default calendar
            calendar_url = f"{GRAPH_API_BASE_URL}/users/{user_id}/calendar"
            async with session.get(calendar_url, headers=headers) as response:
                if response.status != 200:
                    return {"error": f"Failed to get calendar: {response.status}"}

                calendar_data = await response.json()
                calendar_id = calendar_data.get("id")

                if not calendar_id:
                    return {"error": "Calendar ID not found"}

                # Prepare event data
                event_payload = {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": "Esta es una cita automatizada creada con Microsoft Graph API",
                    },
                    "start": {
                        "dateTime": start_time_str,
                        "timeZone": "Pacific Standard Time",
                    },
                    "end": {
                        "dateTime": end_time_str,
                        "timeZone": "Pacific Standard Time",
                    },
                    "location": {"displayName": "Oficinas de Australian Option"},
                    "attendees": [],
                    "isOnlineMeeting": True,
                    "onlineMeetingProvider": "teamsForBusiness",
                    "transactionId": str(uuid.uuid4()),
                }

                # Create the event
                events_url = f"{GRAPH_API_BASE_URL}/users/{user_id}/calendars/{calendar_id}/events"
                async with session.post(
                    events_url, headers=headers, json=event_payload
                ) as response:
                    if response.status not in (200, 201):
                        return {"error": f"Failed to create meeting: {response.status}"}

                    result = await response.json()
                    online_meeting = result.get("onlineMeeting")

                    for recipient in recipients:
                        send_whatsapp_message(recipient, online_meeting["joinUrl"])

                    return {"online_meeting": online_meeting}
        finally:
            # Always close the session and connector, even if there's an error
            await session.close()
            await connector.close()

    except Exception as e:
        logger.error("Error scheduling meeting: %s", e, exc_info=True)
        raise e
