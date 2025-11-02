import os, requests, time

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
REFRESH_TOKEN = os.getenv("LINKEDIN_REFRESH_TOKEN", "")
TOKEN_EXPIRES_AT = 0

def exchange_code_for_tokens(code: str):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()

def refresh_access_token():
    global ACCESS_TOKEN, TOKEN_EXPIRES_AT

    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    data = r.json()

    ACCESS_TOKEN = data["access_token"]
    TOKEN_EXPIRES_AT = time.time() + int(data.get("expires_in", 3600))
    return ACCESS_TOKEN

def get_token():
    if time.time() > TOKEN_EXPIRES_AT:
        return refresh_access_token()
    return ACCESS_TOKEN
