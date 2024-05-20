import requests
import os


OK_CODES = 200, 201, 202, 203, 204, 205, 206


def get_release_notes_description(file_path):
    with open(file_path, "r", encoding="utf8", errors="ignore") as html_file:
        release_notes_description = html_file.read()
    return release_notes_description


def send_notes_zendesk(content):
    url = "https://takeoffhelp.zendesk.com/api/v2/help_center/articles/4417757892753/translations/en-us.json"
    token = os.environ["API_KEY"]
    res = requests.put(
        url,
        headers={"Authorization": "basic " + token},
        json={"translation": {"body": content}},
    )
    if res.status_code in OK_CODES:
        print("Release Notes sent successfully")
        return True
    else:
        print(f"Request Failed with Status Code: {res.status_code}")
        return False


# if __name__ == "__main__":
content = get_release_notes_description("./data/release_notes_zendesk.html")
send_notes_zendesk(content)
