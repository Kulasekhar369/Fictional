import pandas as pd
import sys
import re

def load_mapping(file_path, sheet_name='Sheet1'):
    """Loads mappings from an Excel file into a dictionary."""
    try:
        mapping_df = pd.read_excel(file_path, sheet_name=sheet_name)
        mapping_dict = dict(zip(mapping_df['Pattern'], mapping_df.iloc[:, 1]))
        print(f"Loaded mappings from {file_path}:")
        print(mapping_dict)
        return mapping_dict
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        return {}

def extract_from_pattern(text, mapping_dict, default_value='Unknown'):
    """Extracts a value from text using a mapping dictionary."""
    for pattern, mapped_value in mapping_dict.items():
        if re.search(fr'\b{pattern}\b', str(text), re.IGNORECASE):
            return mapped_value
    return default_value

def process_sprint_data(file_path, circle_mapping_file, task_mapping_file, output_path):
    """Processes the Excel file to add 'Circle Name' and 'Task Category' columns."""
    try:
        # Load the main data file
        df = pd.read_excel(file_path)

        # Check required columns
        if not {'Sprint Name', 'Task Name'}.issubset(df.columns):
            print("Error: 'Sprint Name' and 'Task Name' columns are required in the Excel file.")
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

        # Save the transformed data to an output Excel file
        df.to_excel(output_path, index=False)
        print(f"Transformed Excel file saved as: {output_path}")

    except Exception as e:
        print(f"Error processing Jira data: {e}")

if __name__ == "__main__":
    input_file = sys.argv[1]          # Input Excel file path
    circle_mapping_file = sys.argv[2] # Circle mapping file path
    task_mapping_file = sys.argv[3]   # Task category mapping file path
    output_file = "sprint_data_transformed.xlsx" # Output file path

    process_sprint_data(input_file, circle_mapping_file, task_mapping_file, output_file)
