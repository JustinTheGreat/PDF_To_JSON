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
        # Basic text extraction with simple start/end keywords
        {
            "field_name": "General Info",
            "start_keyword": "Customer Information:",
            "end_keyword": "Equipment Details",
            "page_num": 0,
            "horiz_margin": 300,
            "end_keyword_occurrence": 1
        },
        
        # Using vertical margin to limit extraction height
        {
            "field_name": "Equipment Specs",
            "start_keyword": "Equipment Details",
            "end_keyword": None,  # No end keyword
            "page_num": 0,
            "horiz_margin": 350,
            "vertical_margin": 200,  # Limit vertical extraction to 200 points
            "left_move": 20  # Shift extraction box 20 points to the left
        },
        
        # Using forced keywords to help with parsing
        {
            "field_name": "Technical Parameters",
            "start_keyword": "Parameters",
            "end_keyword": "Test Results",
            "page_num": 1,
            "horiz_margin": 400,
            "forced_keywords": ["Serial Number", "Model", "Voltage", "Current", "Power"]
        },
        
        # Using line break handling for better formatting
        {
            "field_name": "Test Results",
            "start_keyword": "Test Results",
            "end_keyword": "Certification",
            "page_num": 1,
            "horiz_margin": 450,
            "remove_breaks_before": ["passed", "failed", "warning"],
            "remove_breaks_after": ["Test:", "Result:"]
        },
        
        # Using limited line breaks instead of end keyword
        {
            "field_name": "Certification",
            "start_keyword": "Certification",
            "end_keyword": None,  # No end keyword
            "page_num": 1,
            "horiz_margin": 350,
            "end_break_line_count": 10  # Stop after 10 line breaks
        },
        
        # Field with continuation on another page
        {
            "field_name": "Maintenance Records",
            "start_keyword": "Maintenance History",
            "end_keyword": "End of Records",
            "page_num": 2,
            "horiz_margin": 500,
        },
        
        # Continuation field (will be merged with the base field)
        {
            "field_name": "Maintenance Records(+1)",
            "start_keyword": "Continued from previous page",
            "end_keyword": "Recommendations",
            "page_num": 3,
            "horiz_margin": 500,
        },
        
        # Chart field with specific chart parameters
        {
            "field_name": "Performance Data(Chart)",
            "start_keyword": "Performance Metrics",
            "end_keyword": "Graph Data End",
            "page_num": 4,
            "horiz_margin": 450,
            "top_title": True,  # Use top row as column titles
            "left_title": True,  # Use left column as row titles
            "priority_side": "left"  # Make left titles the primary grouping
        },
        
        # Table processing with customized structure
        {
            "field_name": "Components List",
            "start_keyword": "Component Inventory",
            "end_keyword": "Inventory End",
            "page_num": 5,
            "horiz_margin": 500,
            "table_top_labeling": True,
            "table_left_labeling": True,
            "table_structure": "top_main",
            "min_column_width": 5
        },
        
        # Using specific occurrence of keywords for targeted extraction
        {
            "field_name": "Additional Notes",
            "start_keyword": "Notes:",
            "start_keyword_occurrence": 2,  # Use the 2nd occurrence of "Notes:"
            "end_keyword": "End of Notes",
            "end_keyword_occurrence": 1,
            "page_num": 6,
            "horiz_margin": 300
        }
    ]
    
    # Create the JSON file with extraction parameters
    json_path = create_document_json(pdf_path, extraction_params)
    
    if json_path:
        # Display the content of the created JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
            print("\nJSON Content:")
            print(json.dumps(content, indent=2))
    else:
        print("Failed to create JSON file.")