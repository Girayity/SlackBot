import random


class BotBot:

    text = {
        
        [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*giray.bdn* posted an update for *Daily Standup*"
			}
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "How do you feel today?",
				"emoji": "true"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "What did you do since your last report?",
				"emoji": "true"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "What will you do today?",
				"emoji": "true"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Anything blocking your progress?",
				"emoji": "true"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
			}
		}
	]
    }
    def __init__(self, text):
        self.text = text  

    def get_message_payload(self):
        return {
            "blocks": [
                self.text,
            ],
        }
 