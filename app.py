import os
import logging
import json
from flask import Flask, request, Response, make_response
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from datetime import date
import time
import schedule
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
# slack verification token
slack_events_adapter = SlackEventAdapter(
    "ff67dfd0cd4e30d537d9946d3e1f9278", "/slack/events", app)
# slack bot user oauth access token
slack_web_client = WebClient(
    token="xoxb-1402753062691-1412556862820-75ByznqwuGoLZ5IYVBFfkZXQ")

# Dictionary to store daily reports
daily_reports = {}
users = {}
usernames = []
people_who_report = []
people_who_dont_report = []
participation_rate = int()
questions= ["How do you feel today?", "What did you do since your last report?", "What will you do today?", "Anything blocking your progress?"]

# We can reach all user informations in specific channel with using users_list
members  = slack_web_client.users_list(channel = "C01BMPYRD46")['members']
for member in members:
    if member['is_bot'] == False and member['name'] != "slackbot":
        user_id = member['id']
        usernames.append(member['profile']['real_name'])
        users[user_id] = member

#usernames = " ".join([str(i) for i in usernames])  


# Post scheduled message to every user
def scheduled_message():
    for user_id in users:
        slack_web_client.api_call(
                    "chat.postMessage",
                    params=dict(
                        as_user=True,
                        channel=user_id, 
                        text="*rapor yolla reis* >> 20 saniye timerlı test mesajı"
            )
    )
schedule = BackgroundScheduler(daemon=True)
schedule.add_job(
    scheduled_message, 
    #trigger='interval',
    'interval', 
    next_run_time='2020-10-19 10:00:00', 
    hours=1    
    )
schedule.start()

for user_id in users:
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
                        "name": "dashboard",
                        "text": "Dashboard",
                        "type": "button",
                        "value": "dashboard"
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
    # Create a new report for this user in the daily_reports dictionary
    daily_reports[user_id] = {
        "daily_channel": daily_report_dm["channel"],
        "message_ts": "",
        "report": {}
    }
# scheduled message to every user
""" 
def scheduled_message():
    slack_web_client.chat_scheduleMessage(
        channel=user_id, 
        post_at="1602864670",
        text="*rapor yolla reis*"
        
)
scheduled_message()
 """
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
            if not daily_reports[user_id]["report"]:
                daily_reports[user_id]["message_ts"] = form_json["message_ts"]
                #print(daily_reports[user_id]["message_ts"])
                # Show the reporting dialog to the user
                open_dialog = slack_web_client.api_call(
                "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Daily Report",
                            "submit_label": "Submit",
                            "callback_id": user_id + "daily_form",
                            "state": "report",                       
                            "elements": [
                                {
                                    "label": questions[0],
                                    "type": "text",
                                    "name": "feelings",
                                    "max_length": 30,
                                },
                                {
                                    "label": questions[1],
                                    "type": "textarea",
                                    "name": "completedtasks",
                                },
                                {
                                    "label": questions[2],
                                    "type": "textarea",
                                    "name": "todo",
                                },
                                {
                                    "label": questions[3],
                                    "type": "textarea",
                                    "name": "problems",
                                },
                            ]
                        }
                    )
                )  
            
                print("-----------------------")
                print(open_dialog["title"])
                print("-----------------------")
            else:
                slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text= "Zaten rapor yolladın müdür çok istiyosan editle."
                )
            )

        elif selection == "edit_report":            
            daily_report = daily_reports[user_id]
            if not daily_reports[user_id]["report"]:
                slack_web_client.api_call(
                    "chat.postMessage",
                    params=dict(
                        channel=user_id, 
                        text="You have not reported anything yet."
                    )
                )

            else:
                open_dialog = slack_web_client.api_call(
                    "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Edit",
                            "submit_label": "Save",
                            "callback_id": user_id + "edit_form",
                            "state": "edit",
                            "elements": [
                                {
                                    "label": "How do you feel today?",
                                    "type": "text",
                                    "value": daily_report["report"]["feelings"],
                                    "name": "feelings",
                                    "max_length": 30,
                                },
                                {
                                    "label": "What did you do since your last report?",
                                    "type": "textarea",
                                    "value": daily_report["report"]["completedtasks"],
                                    "name": "completedtasks",
                                },
                                {
                                    "label": "What will you do today?",
                                    "type": "textarea",
                                    "value": daily_report["report"]["todo"],
                                    "name": "todo",
                                },
                                {   
                                    "label": "Anything blocking your progress?",
                                    "type": "textarea",
                                    "value": daily_report["report"]["problems"],
                                    "name": "problems",
                                },
                            ]
                        }
                    )
                )
            print(open_dialog)

        elif selection == "dashboard":
            dash = slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text= "*Choose a Question to Change:*",
                    attachments= [
                        {
                            "text": "",
                            "color": "#3AA3E3",
                            "attachment_type": "default",
                            "callback_id": "question_selection",
                            "response_url": "https://hooks.slack.com/services/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",
                            "actions": [
                                {
                                    "name": "question_list",
                                    "text": "Questions",
                                    "type": "select",
                                    "options": [
                                        {
                                            "text": questions[0],
                                            "value": "q1"
                                        },
                                        {
                                            "text": questions[1],
                                            "value": "q2"
                                        },
                                        {
                                            "text": questions[2],
                                            "value": "q3"
                                        },
                                        {
                                            "text": questions[3],
                                            "value": "q4"
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                )
            )
            print("*********************************")
            question = dash["message"]["attachments"][0]["actions"][0]["options"]
            print(question)

            if question[0]["value"] == "q1":
                slack_web_client.api_call(
                    "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Change",
                            "submit_label": "OK",
                            "callback_id": user_id + "q1_form",
                            "state": "q1_form",
                            "elements": [
                                {
                                    "label": "Question 1",
                                    "type": "text",
                                    "value": questions[0],
                                    "name": "q1",
                                },
                            ]
                        }
                    )    
                )

            elif question[1]["value"] == "q2":
                slack_web_client.api_call(
                    "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Change",
                            "submit_label": "OK",
                            "callback_id": user_id + "q2_form",
                            "state": "q2_form",
                            "elements": [
                                {
                                    "label": "Question 2",
                                    "type": "text",
                                    "value": questions[1],
                                    "name": "q2",
                                },
                            ]
                        }
                    )    
                )
            elif question[2]["value"] == "q3":
                slack_web_client.api_call(
                    "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Change",
                            "submit_label": "OK",
                            "callback_id": user_id + "q3_form",
                            "state": "q3_form",
                            "elements": [
                                {
                                    "label": "Question 3",
                                    "type": "text",
                                    "value": questions[2],
                                    "name": "q3",
                                },
                            ]
                        }
                    )    
                )

            elif question[3]["value"] == "q4":
                slack_web_client.api_call(
                    "dialog.open",
                    params=dict(
                        trigger_id=form_json["trigger_id"],
                        dialog={
                            "title": "Change",
                            "submit_label": "OK",
                            "callback_id": user_id + "q4_form",
                            "state": "q4_form",
                            "elements": [
                                {
                                    "label": "Question 4",
                                    "type": "text",
                                    "value": questions[3],
                                    "name": "q4",
                                },
                            ]
                        }
                    )    
                )

        elif selection == "help":
            slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text=":bulb: You can edit your report as well",
                )
            )

    elif form_json["type"] == "dialog_submission":
        if form_json["state"] == "report":
            daily_report = daily_reports[user_id]
            daily_reports[user_id]["report"] = form_json["submission"]
            edited_report = slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel="C01BMPYRD46", #daily_reports[user_id]["daily_channel"],
                    ts=daily_report["message_ts"],
                    text= "",
                    attachments=[
                        {"text": "*" + form_json["user"]["name"] + "*" + " posted an update for *Pragma Daily*"},
                        {"text": "*How do you feel today?*" + "\n" + form_json["submission"]["feelings"], "color": "#ff3333"},
                        {"text": "*What did you do since your last report?*" + "\n" + form_json["submission"]["completedtasks"], "color": "#1a8cff"},
                        {"text": "*What will you do today?*" + "\n" + form_json["submission"]["todo"], "color": "#29a329"},
                        {"text": "*Anything blocking your progress?*" + "\n" + form_json["submission"]["problems"], "color": "#ff9900"},
                    ]
                )
            )
        
            #reported_user_names = [users[user_id]["profile"]["real_name"]people_who_report]
            user_name = users[user_id]["profile"]["real_name"]
            people_who_report.append(user_name)

            participation_rate = (len(people_who_report) / len(users) * 100)

            for name in usernames:
                if name not in people_who_report:
                    people_who_dont_report.append(name)
                
                if name in people_who_report and name in people_who_dont_report:
                    people_who_dont_report.remove(name)

            string = '@'
            tagged_people = [string + i for i in people_who_dont_report]


            slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text="Kolay gelsin müdür."
                )
            )
            if people_who_dont_report:
                print("*********")
                print("TESTTTTTTTTTTTTTssadsad")
                print("*********")
                slack_web_client.api_call(
                    "chat.postMessage",
                    params=dict(
                        channel="C01BMPYRD46", 
                        text="",
                        attachments=[
                            {"text": "Engagement summary for *pragma daily* on " + "*" + str(date.today().strftime("%d/%m/%Y")) + "*"},
                            {"text": "Posted their update: " + "*" + ", ".join(people_who_report) + "*", "color": "#ff3333"},
                            {"text": "Still have time to report: " + "*" + ", ".join(tagged_people) +"*", "color": "#29a329"},
                            {"text": "Participation: " + "*" + str(participation_rate) + "%" + "*"},
                            {"text": "Devamke! " + ":tada:"},
                        ]
                    )
                )
            else:
                slack_web_client.api_call(
                    "chat.postMessage",
                    params=dict(
                        channel="C01BMPYRD46", 
                        text="",
                        attachments=[
                            {"text": "Engagement summary for *pragma daily* on " + "*" + str(date.today().strftime("%d/%m/%Y")) + "*"},
                            {"text": "Posted their update: " + "*" + ", ".join(people_who_report) + "*", "color": "#ff3333"},
                            {"text": "Participation: " + "*" + str(participation_rate) + "%" + "*"},
                            {"text": "Devamke! " + ":tada:"},
                        ]
                    )
                )

            daily_report["message_ts"] = edited_report["ts"]

        elif form_json["state"] == "edit":
            daily_report = daily_reports[user_id]
            daily_reports[user_id]["report"] = form_json["submission"]
            print("dailyreport-----------------------")
            print("-----------------------")
            slack_web_client.api_call(
                "chat.update",
                params=dict(
                    channel="C01BMPYRD46", #daily_reports[user_id]["daily_channel"],
                    ts=daily_report["message_ts"],
                    text= "",
                    attachments=[
                        {"text": "*" + form_json["user"]["name"] + "*" + " posted an update for *Pragma Daily*"},
                        {"text": "*How do you feel today?*" + "\n" + form_json["submission"]["feelings"], "color": "#ff3333"},
                        {"text": "*What did you do since your last report?*" + "\n" + form_json["submission"]["completedtasks"], "color": "#1a8cff"},
                        {"text": "*What will you do today?*" + "\n" + form_json["submission"]["todo"], "color": "#29a329"},
                        {"text": "*Anything blocking your progress?*" + "\n" + form_json["submission"]["problems"], "color": "#ff9900"},
                    ]
                )
            )
            slack_web_client.api_call(
                "chat.postMessage",
                params=dict(
                    channel=user_id, 
                    text=":heavy_check_mark: Report has been edited."
                )
            )
    return make_response("", 200)  

#scheduled_message.job()

if __name__ == "__main__": 
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG) 

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())
    app.run(host='0.0.0.0', port=5003, debug=False)