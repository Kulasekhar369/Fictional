import pandas as pd
import sys
import re

def load_mapping(file_path: str) -> dict:
    """Loads mappings from a CSV file into a dictionary."""
    try:
        mapping_df = pd.read_csv(file_path)
        mapping_dict = dict(zip(mapping_df['Pattern'], mapping_df['MappedValue']))
        print(f"Loaded mappings from {file_path}:")
        print(mapping_dict)
        return mapping_dict
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        return {}

def extract_from_pattern(text: str, mapping_dict: dict, default_value='Unknown') -> str:
    """Extracts a value from text using a mapping dictionary."""
    for pattern, mapped_value in mapping_dict.items():
        if re.search(fr'\b{pattern}\b', str(text), re.IGNORECASE):
            return mapped_value
    return default_value

def process_sprint_data(file_path: str, circle_mapping_file: str, task_mapping_file: str, output_path: str) -> None:
    """Processes the CSV file to add 'Circle Name' and 'Task Category' columns."""
    try:
        # Load the main data file
        df = pd.read_csv(file_path)

        # Check required columns
        if not {'Sprint Name', 'Task Name'}.issubset(df.columns):
            print("Error: 'Sprint Name' and 'Task Name' columns are required in the CSV file.")
            return

        # Load mappings
        circle_mapping = load_mapping(circle_mapping_file)
        task_mapping = load_mapping(task_mapping_file)

        # Add 'Circle Name' column using 'Sprint Name' and circle mapping
        df['Circle Name'] = df['Sprint Name'].apply(lambda x: extract_from_pattern(x, circle_mapping))

        # Add 'Task Category' column using 'Task Name' and task mapping
        df['Task Category'] = df['Task Name'].apply(lambda x: extract_from_pattern(x, task_mapping))

        # Display the first few rows for testing
        print(df.head())

        # Save the transformed data to an output CSV file
        df.to_csv(output_path, index=False)
        print(f"Transformed CSV file saved as: {output_path}")

    except Exception as e:
        print(f"Error processing Jira data: {e}")

if __name__ == "__main__":
    input_file = sys.argv[1]          # Input CSV file path
    circle_mapping_file = sys.argv[2] # Circle mapping CSV file path
    task_mapping_file = sys.argv[3]   # Task category mapping CSV file path
    output_file = "sprint_data_transformed.csv" # Output file path

    process_sprint_data(input_file, circle_mapping_file, task_mapping_file, output_file)
