import requests
import pandas as pd
import re
import sys
import os

# JIRA config
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_API_ENDPOINT = f"{JIRA_BASE_URL}/rest/api/3/search"
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Authentication
auth = (JIRA_USERNAME, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Utility: Load mapping CSVs
def load_mapping(file_path: str) -> dict:
    try:
        df = pd.read_csv(file_path)
        return dict(zip(df['Pattern'], df['MappedValue']))
    except Exception as e:
        print(f"Error loading mapping from {file_path}: {e}")
        return {}

# Utility: Extract pattern
def extract_from_pattern(text: str, mapping_dict: dict, default_value="Unknown") -> str:
    for pattern, value in mapping_dict.items():
        if re.search(fr'\b{pattern}\b', str(text), re.IGNORECASE):
            return value
    return default_value

# Fetch issues for a given JQL
def fetch_issues_for_sprint(jql_query: str) -> list:
    params = {
        "jql": jql_query,
        "maxResults": 1000,
        "fields": "*all"  # fetch all fields for now
    }
    response = requests.get(JIRA_API_ENDPOINT, headers=headers, params=params, auth=auth)
    response.raise_for_status()
    return response.json().get("issues", [])

# Main function
def process_sprints(sprint_names: list, circle_map_path: str, category_map_path: str, output_file: str) -> None:
    circle_map = load_mapping(circle_map_path)
    category_map = load_mapping(category_map_path)

    all_data = []

    for sprint_name in sprint_names:
        jql = f'"Sprint" = "{sprint_name}"'
        print(f"Fetching data for: {sprint_name}")
        try:
            issues = fetch_issues_for_sprint(jql)
            for issue in issues:
                fields = issue.get("fields", {})

                # === Paste your custom extraction logic below ===
                row = {
                    "Key": issue.get("key"),
                    "Status": fields.get("status", {}).get("name", ""),
                    "Assignee": fields.get("assignee", {}).get("displayName", ""),
                    "Summary": fields.get("summary", ""),
                    "Parent Summary": fields.get("parent", {}).get("fields", {}).get("summary", ""),
                }

                # Circle and Category assignment
                row["Circle"] = extract_from_pattern(row["Parent Summary"], circle_map)
                row["Category"] = extract_from_pattern(row["Summary"], category_map)

                all_data.append(row)
        except Exception as e:
            print(f"Error processing sprint {sprint_name}: {e}")

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_excel(output_file, index=False)
        print(f"Output saved to {output_file}")
    else:
        print("No data extracted.")

# Jenkins entrypoint
if __name__ == "__main__":
    # sprint_names passed as comma-separated argument
    sprint_names = sys.argv[1].split(",")
    circle_map = sys.argv[2]  # path to circle mapping CSV
    category_map = sys.argv[3]  # path to category mapping CSV
    output_file = "final_sprint_output.xlsx"
    process_sprints(sprint_names, circle_map, category_map, output_file)
