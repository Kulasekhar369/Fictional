import pandas as pd
import requests
import sys
import re
from io import BytesIO

# Jira credentials (Use environment variables or Jenkins credentials store)
JIRA_URL = "https://your-jira-instance.com/rest/api/2/"
JIRA_USERNAME = "your-username"
JIRA_API_TOKEN = "your-api-token"

# Function to fetch sprint report for a given board and sprint ID
def fetch_sprint_report(board_id: str, sprint_id: str) -> pd.DataFrame:
    """Fetches the sprint report Excel file from Jira API for a specific board and sprint."""
    api_url = f"{JIRA_URL}board/{board_id}/sprint/{sprint_id}/report"
    headers = {"Authorization": f"Basic {JIRA_API_TOKEN}"}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Read the Excel file from API response
        file_stream = BytesIO(response.content)
        df = pd.read_excel(file_stream)
        df['Board ID'] = board_id  # Add Board ID for reference
        print(f"Sprint report for Board {board_id}, Sprint {sprint_id} fetched successfully.")
        return df

    except Exception as e:
        print(f"Error fetching sprint report for Board {board_id}, Sprint {sprint_id}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

# Function to load mapping file (circle mapping or task mapping)
def load_mapping(file_path: str) -> dict:
    """Loads mappings from a CSV file into a dictionary."""
    try:
        mapping_df = pd.read_csv(file_path)
        return dict(zip(mapping_df['Pattern'], mapping_df['MappedValue']))
    except Exception as e:
        print(f"Error loading mapping file {file_path}: {e}")
        return {}

# Function to extract mapped value based on a pattern match
def extract_from_pattern(text: str, mapping_dict: dict, default_value="Unknown") -> str:
    """Extracts a value from text using a mapping dictionary."""
    for pattern, mapped_value in mapping_dict.items():
        if re.search(fr'\b{pattern}\b', str(text), re.IGNORECASE):
            return mapped_value
    return default_value

# Main processing function for multiple boards
def process_sprint_data_for_boards(board_sprint_mapping: dict, circle_mapping_file: str, task_mapping_file: str, output_path: str) -> None:
    """Fetches and processes the Jira sprint reports for multiple boards."""
    all_sprint_data = []

    # Step 1: Load mappings
    circle_mapping = load_mapping(circle_mapping_file)
    task_mapping = load_mapping(task_mapping_file)

    # Step 2: Loop through boards and sprints
    for board_id, sprint_id in board_sprint_mapping.items():
        df = fetch_sprint_report(board_id, sprint_id)
        
        if df.empty:
            print(f"Skipping Board {board_id}, Sprint {sprint_id} due to empty data.")
            continue

        # Step 3: Check required columns
        if not {'Sprint Name', 'Task Name'}.issubset(df.columns):
            print(f"Error: 'Sprint Name' and 'Task Name' columns are required for Board {board_id}, Sprint {sprint_id}.")
            continue

        # Step 4: Add 'Circle Name' column based on 'Sprint Name'
        df['Circle Name'] = df['Sprint Name'].apply(lambda x: extract_from_pattern(x, circle_mapping))

        # Step 5: Add 'Task Category' column based on 'Task Name'
        df['Task Category'] = df['Task Name'].apply(lambda x: extract_from_pattern(x, task_mapping))

        all_sprint_data.append(df)

    # Step 6: Merge all data into a single DataFrame
    if all_sprint_data:
        final_df = pd.concat(all_sprint_data, ignore_index=True)
        final_df.to_excel(output_path, index=False)
        print(f"Transformed sprint data for all boards saved as: {output_path}")
    else:
        print("No valid sprint data was found for any board.")

# Script execution in Jenkins
if __name__ == "__main__":
    board_sprint_mapping_str = sys.argv[1]  # Example: "Board1:Sprint10,Board2:Sprint15"
    circle_mapping_file = sys.argv[2]  # Path to circle mapping CSV
    task_mapping_file = sys.argv[3]  # Path to task category mapping CSV
    output_file = "processed_sprint_data.xlsx"  # Output file

    # Convert string input to dictionary {board_id: sprint_id}
    board_sprint_mapping = dict(item.split(":") for item in board_sprint_mapping_str.split(","))

    process_sprint_data_for_boards(board_sprint_mapping, circle_mapping_file, task_mapping_file, output_file)
