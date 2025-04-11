import requests
import pandas as pd
import sys
import re

# Jira credentials (you should pass these securely from Jenkins)
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"

# JQL API endpoint
JIRA_SEARCH_API = f"{JIRA_URL}/rest/api/2/search"

# Load mapping file into a dictionary
def load_mapping(file_path: str) -> dict:
    try:
        mapping_df = pd.read_csv(file_path)
        return dict(zip(mapping_df['Pattern'], mapping_df['MappedValue']))
    except Exception as e:
        print(f"Error loading mapping file {file_path}: {e}")
        return {}

# Extract mapped value using pattern matching
def extract_from_pattern(text: str, mapping_dict: dict, default="Unknown") -> str:
    for pattern, mapped_value in mapping_dict.items():
        if re.search(fr'\b{pattern}\b', str(text), re.IGNORECASE):
            return mapped_value
    return default

# Fetch Jira issues using JQL for a given sprint name
def fetch_issues_by_sprint(sprint_name: str) -> pd.DataFrame:
    jql = f'sprint = "{sprint_name}"'
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_API_TOKEN)}",
        "Content-Type": "application/json"
    }
    params = {
        "jql": jql,
        "fields": "key,status,summary,parent"
    }

    response = requests.get(JIRA_SEARCH_API, headers=headers, params=params)
    response.raise_for_status()
    issues = response.json()["issues"]

    # Extract required fields
    data = []
    for issue in issues:
        key = issue["key"]
        status = issue["fields"]["status"]["name"]
        summary = issue["fields"]["summary"]
        parent_summary = issue["fields"]["parent"]["fields"]["summary"] if issue["fields"].get("parent") else ""
        data.append({
            "Key": key,
            "Status": status,
            "Summary": summary,
            "Parent Summary": parent_summary,
            "Sprint Name": sprint_name
        })

    return pd.DataFrame(data)

# Process multiple sprints and apply pattern matching
def process_sprints(sprint_names, circle_mapping_file, category_mapping_file, output_file):
    circle_mapping = load_mapping(circle_mapping_file)
    category_mapping = load_mapping(category_mapping_file)

    all_data = []

    for sprint in sprint_names:
        print(f"Processing sprint: {sprint}")
        df = fetch_issues_by_sprint(sprint)
        df["Circle"] = df["Parent Summary"].apply(lambda x: extract_from_pattern(x, circle_mapping))
        df["Category"] = df["Summary"].apply(lambda x: extract_from_pattern(x, category_mapping))
        all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_excel(output_file, index=False)
        print(f"Data saved to: {output_file}")
    else:
        print("No data found for any sprint.")

# Entry point
if __name__ == "__main__":
    sprint_names_arg = sys.argv[1]  # Comma-separated sprint names
    circle_mapping_file = sys.argv[2]
    category_mapping_file = sys.argv[3]
    output_file = "final_sprint_report.xlsx"

    sprint_names = sprint_names_arg.split(",")
    process_sprints(sprint_names, circle_mapping_file, category_mapping_file, output_file)
