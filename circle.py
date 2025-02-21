import pandas as pd
import sys
import re

def extract_circle_name(sprint_name):
    """Extracts the circle name from a jumbled sprint name using pattern matching."""
    # Define known circle names or patterns (this can be extended or made dynamic)
    known_circles = ['CircleA', 'CircleB', 'CircleC', 'CircleD']
    
    # Use regex to match known circle names within the sprint name
    for circle in known_circles:
        if re.search(fr'\b{circle}\b', sprint_name, re.IGNORECASE):
            return circle
    return 'Unknown'

def process_circle_extraction(file_path, output_path):
    """Processes the Excel file to add a 'Circle Name' column."""
    try:
        # Load the Excel file containing Jira sprint data
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Check if 'Sprint Name' column exists
        if 'Sprint Name' not in df.columns:
            print("Error: 'Sprint Name' column not found in the Excel sheet.")
            return
        
        # Add 'Circle Name' column by extracting from 'Sprint Name'
        df['Circle Name'] = df['Sprint Name'].apply(extract_circle_name)
        
        # Save the updated data to an output Excel file
        df.to_excel(output_path, index=False)
        print(f"Transformed Excel file saved as: {output_path}")
    
    except Exception as e:
        print(f"Error processing Jira data: {e}")

if __name__ == "__main__":
    input_file = sys.argv[1]  # Input Excel file path
    output_file = "circle_extracted_output.xlsx"  # Output file path
    
    process_circle_extraction(input_file, output_file)
