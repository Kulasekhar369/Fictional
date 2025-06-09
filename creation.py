import requests
import json
from base64 import b64encode

# ==== CONFIGURATION ====
JIRA_URL = "https://your-domain.atlassian.net"
USERNAME = "your-email@example.com"
API_TOKEN = "your-api-token"
TEMPLATE_ISSUE_KEY = "PROJ-123"  # Issue you want to clone
NEW_SUMMARY = "Cloned Story - Sprint 24"
PROJECT_KEY = "PROJ"
ISSUE_TYPE = "Story"
ASSIGNEE = "your.jira.username"  # not email, it's the accountId or username
PRIORITY_ID = "3"  # Optional: 1 = Highest, 3 = Medium, 5 = Lowest

# ==== AUTH ====
auth = (USERNAME, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# ==== 1. Get the template issue ====
def get_issue(key):
    url = f"{JIRA_URL}/rest/api/3/issue/{key}"
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch issue: {response.status_code}, {response.text}")
    return response.json()

# ==== 2. Modify the description ====
def modify_description(original_description, env="STAGING", circle="PAYMENTS"):
    # Convert the raw ADF JSON to a string and do simple replacements
    description_str = json.dumps(original_description)
    description_str = description_str.replace("{{ENV}}", env)
    description_str = description_str.replace("{{CIRCLE}}", circle)
    return json.loads(description_str)  # convert back to ADF JSON

# ==== 3. Create a new issue ====
def create_issue(summary, description):
    url = f"{JIRA_URL}/rest/api/3/issue"
    payload = {
        "fields": {
            "summary": summary,
            "project": {
                "key": PROJECT_KEY
            },
            "issuetype": {
                "name": ISSUE_TYPE
            },
            "description": description,
            "assignee": {
                "name": ASSIGNEE  # use "accountId" if using Atlassian Cloud
            },
            "priority": {
                "id": PRIORITY_ID
            }
            # Add other fields like parent, team, custom fields if needed
        }
    }
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    if response.status_code != 201:
        raise Exception(f"Failed to create issue: {response.status_code}, {response.text}")
    return response.json()

# ==== MAIN ====
if __name__ == "__main__":
    template_issue = get_issue(TEMPLATE_ISSUE_KEY)
    original_description = template_issue["fields"].get("description")

    if not original_description:
        raise Exception("Template issue has no description.")

    new_description = modify_description(original_description)
    result = create_issue(NEW_SUMMARY, new_description)
    print(f"Issue created: {result['key']}")
