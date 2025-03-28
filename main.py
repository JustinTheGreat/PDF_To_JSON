import os
import json
from Components.pdf_processor import create_document_json

# Prompt the user for the file path when the script is run
if __name__ == "__main__":
    # Prompt the user for the PDF file path
    pdf_path = input("Enter the path to the PDF file: ")
    
    # Remove any quotes that might have been included in the path
    pdf_path = pdf_path.strip('"\'')
    
    # Define extraction parameters for different sections (page_num starts at 0)
    extraction_params = [
        {
            "field_name": "Report",
            "start_keyword": "Test Result:",
            "end_keyword": "Mock Result",
            "page_num": 0,
            "horiz_margin": 300,
            "end_keyword_occurrence": 1,
            "forced_keywords": ["Mock Rasult"]
        },
        {
            "field_name": "Report(+1)",
            "start_keyword": "Parameters",
            "end_keyword": "meters",
            "page_num": 4,
            "horiz_margin": 160,
            "end_keyword_occurrence": 1
        },

    ]
    
    # Create the JSON file with additional extraction parameters
    json_path = create_document_json(pdf_path, extraction_params)
    
    if json_path:
        # Display the content of the created JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
            print("\nJSON Content:")
            print(json.dumps(content, indent=2))
    else:
        print("Failed to create JSON file.")