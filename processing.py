import pandas as pd
import sys
import re

def load_category_mapping(mapping_file):
    """Load category mapping from an Excel file."""
    try:
        mapping_df = pd.read_excel(mapping_file, engine="openpyxl")
        return dict(zip(mapping_df['Keyword'].str.lower(), mapping_df['Category']))
    except Exception as e:
        print(f"Error loading category mapping: {e}")
        return {}

def extract_circle_name(sprint_name):
    """Extract circle name from a jumbled sprint name using pattern matching."""
    # Define known circle names or patterns (these can be extended)
    known_circles = ['CircleA', 'CircleB', 'CircleC']
    
    # Use regex to match known circle names
    for circle in known_circles:
        if re.search(fr'\b{circle}\b', sprint_name, re.IGNORECASE):
            return circle
    return 'Unknown'

def categorize_task(task_name, category_mapping):
    """Categorize tasks based on keywords in the task name."""
    for keyword, category in category_mapping.items():
        if re.search(fr'\b{keyword}\b', task_name, re.IGNORECASE):
            return category
    return 'Uncategorized'

def process_jira_data(file_path, mapping_file, output_path):
    """Main function to process Jira sprint data."""
    try:
        # Load the Excel file containing Jira data
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Load the category mapping from an external file
        category_mapping = load_category_mapping(mapping_file)
        
        # Add 'Circle Name' column by extracting from 'Sprint Name'
        df['Circle Name'] = df['Sprint Name'].apply(extract_circle_name)
        
        # Add 'Category' column by categorizing 'Task Name'
        df['Category'] = df['Task Name'].apply(lambda x: categorize_task(x, category_mapping))
        
        # Save the transformed data to an output Excel file
        df.to_excel(output_path, index=False)
        print(f"Transformed Excel file saved as: {output_path}")
    
    except Exception as e:
        print(f"Error processing Jira data: {e}")

if __name__ == "__main__":
    input_file = 
    mapping_file = "category_mapping.xlsx"  # Mapping file path
    output_file = "transformed_output.xlsx"  # Output file path
    
    process_jira_data(input_file, mapping_file, output_file)
