import os, requests
from twilio.rest import Client

def load_template(filename):
    path = os.path.join(os.path.dirname(__file__), "templates", filename)
    with open(path, "r") as f:
        return f.read()

def notify(template_name, vars, etype="general"):
    msg = load_template(template_name).format(**vars)

    # WhatsApp send via Twilio
    TWILIO_SID     = os.getenv("TWILIO_SID")
    TWILIO_TOKEN   = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM_WA = os.getenv("TWILIO_FROM_WA")
    USER_WA        = os.getenv("USER_WA")
    

    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM_WA and USER_WA:
        try:
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            message = client.messages.create(
                from_=TWILIO_FROM_WA,
                body=msg,
                to=USER_WA
            )
            print(f"Twilio message sent with SID: {message.sid}")
        except Exception as e:
            print(f"Error sending Twilio message: {e}")

    print(f"[notify][{etype}] {msg}")

        
#def send_whatsapp(text: str):
#    if not (WA_TOKEN and WA_PHONE_ID and WA_TO): 
#        return
#    url = f"https://graph.facebook.com/v19.0/{WA_PHONE_ID}/messages"
#    data = {"messaging_product":"whatsapp","to": WA_TO.replace("whatsapp:",""),
#            "type":"text","text":{"body": text}}
#    headers = {"Authorization": f"Bearer {WA_TOKEN}"}
#    try:
#        r = requests.post(url, json=data, headers=headers, timeout=30)
#        r.raise_for_status()
#    except Exception as e:
#        log_event("error", f"whatsapp_failed: {e}")

#def send_email(subject: str, text: str):
#    if not (SENDGRID_KEY and MAIL_TO):
#        return
#    api = "https://api.sendgrid.com/v3/mail/send"
#    body = {
#      "personalizations":[{"to":[{"email": MAIL_TO}]}],
#      "from":{"email": MAIL_FROM},
#      "subject": subject,
#      "content":[{"type":"text/plain","value": text}]
#    }
#    try:
#        r = requests.post(api, json=body, headers={"Authorization": f"Bearer {SENDGRID_KEY}"}, timeout=30)
#        r.raise_for_status()
#    except Exception as e:
#        log_event("error", f"email_failed: {e}")

#def notify(title: str, text: str, payload=None, etype="info"):
#    log_event(etype, title, payload)
#    send_whatsapp(f"{title}\n{text}")
#    send_email(title, text)
