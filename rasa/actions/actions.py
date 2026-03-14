from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import os
import httpx

# IMPORTANT: use Docker service name, NOT localhost
APPT_URL = os.getenv(
    "APPOINTMENT_SERVICE_URL",
    "http://appointment_service:8000"
)

class ActionBookAppointment(Action):
    def name(self) -> Text:
        return "action_book_appointment"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        person_name = tracker.get_slot("person_name")
        appointment_date = tracker.get_slot("appointment_date")

        payload = {
            "name": person_name,
            "date": appointment_date
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{APPT_URL}/appointments",
                    json=payload,
                    timeout=5.0
                )

            if resp.status_code == 201:
                appointment_id = resp.json().get("appointment_id")

                dispatcher.utter_message(
                    text=f"Your appointment is booked. ID: {appointment_id}"
                )

                return [{
                    "event": "slot",
                    "name": "appointment_id",
                    "value": appointment_id
                }]

            dispatcher.utter_message(
                text="Sorry, couldn't book the appointment right now."
            )

        except Exception:
            dispatcher.utter_message(
                text="Error contacting appointment service."
            )

        return []
