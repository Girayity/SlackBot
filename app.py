import os
import logging
import json
from flask import Flask, request, Response, make_response
from slack import WebClient
from slackeventsapi import SlackEventAdapter
#from botbot import BotBot

app = Flask(__name__)
# slack verification token
slack_events_adapter = SlackEventAdapter(
    "***", "/slack/events", app)
# slack bot user oauth access token
slack_web_client = WebClient(
    token="***")

# Dictionary to store daily reports
daily_reports = {}

# Send a message to the user asking what does user want?
user_id = "U01BDPPNFGF"
# Post a message to user
daily_report_dm = slack_web_client.api_call(
    "chat.postMessage",
    params=dict(
        as_user=True,
        channel=user_id,
        text="Hi! I'm BotBot. You can inform your teammates with using me about your mood, what you are doing now, what will you do and problems if there any. :v:\n\n",
        attachments=[
            {
                "text": "",
                "callback_id": user_id + "daily_form",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                    "name": "daily_report",
                    "text": "Daily Report",
                    "type": "button",
                    "value": "daily_report"
                    },
                    {
                    "name": "edit_report",
                    "text": "Edit Report",
                    "type": "button",
                    "value": "edit_report"
                    },
                    {
                    "name": "hi",
                    "text": "Say Hi!",
                    "type": "button",
                    "value": "say_hi"
                    },
                    {
                    "name": "help",
                    "text": "Help",
                    "type": "button",
                    "value": "help"
                    },
                ]
            }
        ]
    )
)

#print(daily_report_dm["message"]["attachments"][0]["actions"])
# Create a new report for this user in the daily_reports dictionary
daily_reports[user_id] = {
    "daily_channel": daily_report_dm["channel"],
    "message_ts": "",
    "report": {}
}

# Listen user's selection and show a dialog-submit/edit- according to that
@app.route("/slack/message_actions", methods=["POST"])
def message_actions():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])
    user_id = form_json["user"]["id"]
    #print(form_json)
    # Check to see what the user's selection was and update the message

    if form_json["type"] == "interactive_message":
        selection = form_json["actions"][0]["value"]

        if selection == "daily_report":
            daily_reports[user_id]["message_ts"] = form_json["message_ts"]
            print(daily_reports[user_id]["message_ts"])
            # Show the reporting dialog to the user
            open_dialog = slack_web_client.api_call(
            "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Daily Report",
                            "submit_label": "Submit",
                            "callback_id": user_id + "daily_form",
                            "elements": [
                                {
                                    "label": "How do you feel today?",
                                    "type": "text",
                                    "name": "feelings",
                                    "max_length": 30,
                                },
                                {
                                    "label": "What did you do since your last report?",
                                    "type": "textarea",
                                    "name": "completedtasks",
                                },
                                {
                                    "label": "What will you do today?",
                                    "type": "textarea",
                                    "name": "todo",
                                },
                                {
                                    "label": "Anything blocking your progress?",
                                    "type": "text",
                                    "name": "problems",
                                },
                            ]
                        }
                    )
                )  
            print(open_dialog)
        elif selection == "edit_report":
            daily_report = daily_reports[user_id]

            open_dialog = slack_web_client.api_call(
                "dialog.open",
                params=dict(
                    trigger_id=form_json["trigger_id"],
                    dialog={
                        "title": "Edit",
                        "submit_label": "Submit",
                        "callback_id": user_id + "daily_report_form",
                        "elements": [
                            {
                                "label": "How do you feel today?",
                                "type": "text",
                                "initial_value": "dsad",
                                "name": "feelings",
                                "max_length": 30,
                            },
                            {
                                "label": "What did you do since your last report?",
                                "type": "textarea",
                                "name": "completedtasks",
                            },
                            {
                                "label": "What will you do today?",
                                "type": "textarea",
                                "name": "todo",
                            },
                            {   
                                "label": "Anything blocking your progress?",
                                "type": "text",
                                "name": "problems",
                            },

                        ]
                    }
                )
            )
        elif selection == "say_hi":
            slack_web_client.api_call(
                    "chat.postMessage",
                    params=dict(
                        channel=user_id, 
                        text="Hi! I'm BotBot."
                    )
                )
        elif selection == "help":
            slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text=":bulb: You can edit your report as well"
                )
            )                  
    elif form_json["type"] == "dialog_submission":
        daily_report = daily_reports[user_id]
        daily_reports[user_id]["report"] = form_json["submission"]
        print(form_json)
        slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel="C01BMPYRD46", #daily_reports[user_id]["daily_channel"],
                    ts=daily_report["message_ts"],
                    text= "",
                    attachments=[
                        {"text":"*" + form_json["user"]["name"] + "*" + " posted an update for *Pragma Daily*"},
                        {"text": "*How do you feel today?*" + "\n" + form_json["submission"]["feelings"], "color": "#ff3333"},
                        {"text": "*What did you do since your last report?*" + "\n" + form_json["submission"]["completedtasks"], "color": "#1a8cff"},
                        {"text": "*What will you do today?*" + "\n" + form_json["submission"]["todo"], "color": "#29a329"},
                        {"text": "*Anything blocking your progress?*" + "\n" + form_json["submission"]["problems"], "color": "#ff9900"},
                    ]
                )
            )
    print(daily_reports[user_id]["report"])
    return make_response("", 200)

if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())
    app.run(host='0.0.0.0', port=5003, debug=True)
