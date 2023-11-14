from mailjet_rest import Client
import os

async def send_email( 
    recipient_email: str, 
    recipient_name:str, 
    validation_code: str|None = None,
    reset_password: str|None = None):
    api_key = os.environ['MAILJET_API_KEY']
    api_secret = os.environ['MAILJET_SECRET_KEY']
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    if validation_code:
        data = {
            'Messages': [
                {
                    "To": [
                        {
                            "Email": recipient_email,
                            "Name": recipient_name
                        }
                    ],
                    "TemplateID": 5302951,
                    "TemplateLanguage": True,
                    "Variables": {
                        "name": recipient_name,
                        "validation_code": validation_code
                    }
                }
            ]
        }
        response = mailjet.send.create(data=data)
    if reset_password:
        data = {
            'Messages': [
                {
                    "To": [
                        {
                            "Email": recipient_email,
                            "Name": recipient_name
                        }
                    ],
                    "TemplateID": 5307823,
                    "TemplateLanguage": True,
                    "Variables": {
                        "name": recipient_name,
                        "reset_password": reset_password
                    }
                }
            ]
        }
        response = mailjet.send.create(data=data)
    return response
