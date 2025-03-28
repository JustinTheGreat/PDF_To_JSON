import os
import json
import re
import pdfplumber
from Components.pdf_extractor import (
    parse_text_to_key_value, 
    format_raw_text, 
    apply_special_formatting
)
from Components.GeneralInfo import extract_serial_data, find_keyword_position, find_nth_occurrence_position

def clean_empty_keys(data_dict):
    """
    Clean a dictionary by removing any keys with empty values.
    
    Args:
        data_dict (dict): Dictionary to clean
        
    Returns:
        dict: Cleaned dictionary with no empty values
    """
    # Create a copy to avoid modifying during iteration
    cleaned_dict = {}
    
    for key, value in data_dict.items():
        # Skip empty values and empty lists
        if value == "" or value == [] or value is None:
            continue
        
        # For lists, filter out any empty values
        if isinstance(value, list):
            filtered_values = [v for v in value if v != "" and v is not None]
            if filtered_values:  # Only add if there are non-empty values
                cleaned_dict[key] = filtered_values if len(filtered_values) > 1 else filtered_values[0]
        else:
            cleaned_dict[key] = value
    
    return cleaned_dict

def extract_pdf_data(pdf_path, extraction_params):
    """
    Extract various data from PDF based on a list of extraction parameters.
    Parse the extracted text into key-value pairs.
    
    Args:
        pdf_path (str): Path to the PDF file
        extraction_params (list): List of parameter dictionaries for extraction
        
    Returns:
        dict: Dictionary with all extracted data
    """
    extracted_data = {}
    
    for param_set in extraction_params:
        # Extract the parameters from the dictionary
        field_name = param_set.get('field_name', 'N/A')
        start_keyword = param_set.get('start_keyword', 'N/A')
        end_keyword = param_set.get('end_keyword', 'N/A')
        page_num = param_set.get('page_num', 0)
        horiz_margin = param_set.get('horiz_margin', 200)
        end_keyword_occurrence = param_set.get('end_keyword_occurrence', 1)
        
        # Get the list of forced keywords (if any)
        forced_keywords = param_set.get('forced_keywords', None)
        
        # Extract the data using the specified parameters
        original_raw_text = extract_serial_data(
            pdf_path,
            start_keyword=start_keyword,
            end_keyword=end_keyword,
            page_num=page_num,
            horiz_margin=horiz_margin,
            end_keyword_occurrence=end_keyword_occurrence
        )
        
        # Format the raw text based on field name (but keep original for the raw_text field)
        formatted_raw_text = format_raw_text(field_name, original_raw_text, forced_keywords)
        
        # Parse the formatted text into key-value pairs and get unparsed lines
        parsed_result, unparsed_lines = parse_text_to_key_value(formatted_raw_text)
        
        # Apply special formatting to handle unparsed lines and business-specific rules
        formatted_result = apply_special_formatting(field_name, parsed_result, unparsed_lines)
        
        # Process the results based on keyword configuration
        processed_result = process_parsed_result(
            formatted_result,
            start_keyword, 
            end_keyword,
            original_raw_text,
            end_keyword_occurrence,
            forced_keywords
        )
        
        # Check if this field already exists (duplicate extraction parameters)
        if field_name in extracted_data:
            # Append to raw text
            existing_raw_text = extracted_data[field_name]["raw_text"]
            new_raw_text = existing_raw_text + "\n\n--- Additional Data ---\n\n" + original_raw_text
            
            # Append to formatted text
            existing_formatted_text = extracted_data[field_name]["formatted_text"]
            new_formatted_text = existing_formatted_text + "\n\n--- Additional Data ---\n\n" + formatted_raw_text
            
            # Merge parsed data dictionaries
            existing_parsed_data = extracted_data[field_name]["parsed_data"]
            new_parsed_data = {}
            
            # First copy all existing data
            for key, value in existing_parsed_data.items():
                new_parsed_data[key] = value
            
            # Then merge in new data, handling duplicates
            for key, value in processed_result.items():
                if key in new_parsed_data:
                    existing_value = new_parsed_data[key]
                    if isinstance(existing_value, list):
                        if isinstance(value, list):
                            new_parsed_data[key].extend(value)
                        else:
                            new_parsed_data[key].append(value)
                    else:
                        if isinstance(value, list):
                            new_parsed_data[key] = [existing_value] + value
                        elif existing_value != value:
                            new_parsed_data[key] = [existing_value, value]
                else:
                    new_parsed_data[key] = value
            
            # Update the extracted data with merged content
            extracted_data[field_name] = {
                "raw_text": new_raw_text,
                "formatted_text": new_formatted_text,
                "parsed_data": new_parsed_data
            }
        else:
            # Store both the original raw text and the formatted result in the dictionary
            extracted_data[field_name] = {
                "raw_text": original_raw_text,
                "formatted_text": formatted_raw_text,
                "parsed_data": processed_result
            }
    
    return extracted_data

def process_parsed_result(parsed_result, start_keyword, end_keyword, original_raw_text, end_keyword_occurrence, forced_keywords=None):
    """
    Process the parsed result based on keyword configuration.
    
    Args:
        parsed_result (dict): Dictionary of parsed key-value pairs
        start_keyword (str): Start keyword for extraction
        end_keyword (str): End keyword for extraction
        original_raw_text (str): Original raw text
        end_keyword_occurrence (int): Occurrence number of end keyword to use
        forced_keywords (list): List of keywords that should be treated as keys
        
    Returns:
        dict: Processed parsed result
    """
    # Create a copy to avoid modifying the original
    processed_result = parsed_result.copy()
    
    # Handle forced keywords to ensure they weren't included in previous values
    if forced_keywords and isinstance(forced_keywords, list):
        # For each forced keyword, check if it's contained in any value
        for keyword in forced_keywords:
            for key, value in list(processed_result.items()):
                # Handle both single values and lists of values
                if isinstance(value, str) and keyword in value:
                    # Split the value at the keyword
                    parts = value.split(keyword, 1)
                    
                    # Update the original value to stop at the keyword
                    processed_result[key] = parts[0].strip()
                    
                    # If there's content after the keyword, create a new key-value pair
                    if len(parts) > 1 and parts[1].strip():
                        # Set the keyword as a new key, and the remaining part as its value
                        # Make sure to handle the case where there's a colon already
                        if ':' in parts[1][:5]:  # Check first few characters for a colon
                            rest_parts = parts[1].split(':', 1)
                            new_value = rest_parts[1].strip() if len(rest_parts) > 1 else ""
                            # Only add if the new value is not empty
                            if new_value:
                                if keyword in processed_result:
                                    if isinstance(processed_result[keyword], list):
                                        processed_result[keyword].append(new_value)
                                    else:
                                        processed_result[keyword] = [processed_result[keyword], new_value]
                                else:
                                    processed_result[keyword] = new_value
                        else:
                            new_value = parts[1].strip()
                            # Only add if the new value is not empty
                            if new_value:
                                if keyword in processed_result:
                                    if isinstance(processed_result[keyword], list):
                                        processed_result[keyword].append(new_value)
                                    else:
                                        processed_result[keyword] = [processed_result[keyword], new_value]
                                else:
                                    processed_result[keyword] = new_value
                elif isinstance(value, list):
                    # Process each item in the list
                    new_values = []
                    for item in value:
                        if keyword in item:
                            # Split the value at the keyword
                            parts = item.split(keyword, 1)
                            
                            # Add the part before the keyword to the new values list
                            new_values.append(parts[0].strip())
                            
                            # If there's content after the keyword, create a new key-value pair
                            if len(parts) > 1 and parts[1].strip():
                                # Handle the case where there's a colon already
                                if ':' in parts[1][:5]:
                                    rest_parts = parts[1].split(':', 1)
                                    new_value = rest_parts[1].strip() if len(rest_parts) > 1 else ""
                                    # Only add if the new value is not empty
                                    if new_value:
                                        if keyword in processed_result:
                                            # Add to existing list or convert to list
                                            if isinstance(processed_result[keyword], list):
                                                processed_result[keyword].append(new_value)
                                            else:
                                                processed_result[keyword] = [processed_result[keyword], new_value]
                                        else:
                                            processed_result[keyword] = new_value
                                else:
                                    new_value = parts[1].strip()
                                    # Only add if the new value is not empty
                                    if new_value:
                                        if keyword in processed_result:
                                            # Add to existing list or convert to list
                                            if isinstance(processed_result[keyword], list):
                                                processed_result[keyword].append(new_value)
                                            else:
                                                processed_result[keyword] = [processed_result[keyword], new_value]
                                        else:
                                            processed_result[keyword] = new_value
                        else:
                            # Keep unchanged values
                            new_values.append(item)
                    
                    # Update with the filtered values
                    if new_values:
                        processed_result[key] = new_values
                    else:
                        # If all values were processed, remove the original key
                        del processed_result[key]
    
    # Special handling for Software Version section or when start_keyword == end_keyword
    if start_keyword == end_keyword:
        result = handle_same_start_end_keyword(processed_result, start_keyword)
    else:
        result = handle_different_start_end_keyword(
            processed_result, 
            end_keyword, 
            original_raw_text, 
            end_keyword_occurrence
        )
    
    # Clean out any empty values
    return clean_empty_keys(result)

def handle_same_start_end_keyword(parsed_result, keyword):
    """
    Handle case where start and end keywords are the same.
    
    Args:
        parsed_result (dict): Dictionary of parsed key-value pairs
        keyword (str): The keyword
        
    Returns:
        dict: Processed parsed result
    """
    # When start and end keywords are the same, we'll keep all entries
    # Just ensure we have at least one key with the keyword
    has_keyword = False
    for key in parsed_result.keys():
        if keyword in key:
            has_keyword = True
            break
    
    # If no keys contain the keyword, add one
    if not has_keyword and parsed_result:
        # Try to find a key that might contain part of the keyword
        matching_key = None
        for key in parsed_result.keys():
            if any(word in key.lower() for word in keyword.lower().split()):
                matching_key = key
                break
        
        # If found a partial match, rename it
        if matching_key:
            parsed_result[keyword] = parsed_result[matching_key]
            del parsed_result[matching_key]
        else:
            # Otherwise, add a new key
            parsed_result[keyword] = ""
    
    return parsed_result

def handle_different_start_end_keyword(parsed_result, end_keyword, original_raw_text, end_keyword_occurrence):
    """
    Handle case where start and end keywords are different.
    Prevents adding any empty keys or duplicates.
    
    Args:
        parsed_result (dict): Dictionary of parsed key-value pairs
        end_keyword (str): End keyword for extraction
        original_raw_text (str): Original raw text
        end_keyword_occurrence (int): Occurrence number of end keyword to use
        
    Returns:
        dict: Processed parsed result
    """
    # Remove the colon from the end_keyword if it exists
    clean_end_keyword = end_keyword.rstrip(':')
    
    # Find all occurrences of the end_keyword in the text
    end_keyword_lines = []
    lines = original_raw_text.split('\n')
    
    for i, line in enumerate(lines):
        if end_keyword in line:
            end_keyword_lines.append((i, line))
    
    # If we have the expected occurrence of end_keyword
    if end_keyword_lines and end_keyword_occurrence <= len(end_keyword_lines):
        # Use the specified occurrence
        end_line_index, end_line = end_keyword_lines[end_keyword_occurrence - 1]
        
        # Find all keys that appear after this end_keyword line
        keys_to_remove = []
        for i, line in enumerate(lines):
            if i > end_line_index and ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip()
                if key in parsed_result:
                    keys_to_remove.append(key)
        
        # Remove the identified keys
        for key in keys_to_remove:
            if key in parsed_result:
                del parsed_result[key]
        
        # Check if the end_keyword is part of an existing key
        is_part_of_existing_key = False
        for key in parsed_result.keys():
            if clean_end_keyword in key:
                is_part_of_existing_key = True
                break
        
        # Only add the end_keyword as a key if it's not already present in any form
        # and it has actual content in the end line
        if not is_part_of_existing_key and ':' in end_line:
            parts = end_line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            # Only add if the value is not empty
            if value:
                parsed_result[key] = value
    
    return parsed_result

def get_bbox_coordinates(pdf_path, extraction_params=None):
    """
    Get bounding box coordinates for specified fields in a PDF based on extraction parameters.
    
    Args:
        pdf_path (str): Path to the PDF file
        extraction_params (list): List of parameter dictionaries for extraction,
                                 following the same format as in main.py.
        
    Returns:
        dict: Dictionary containing bounding box information for each field or key
    """
    bbox_data = {}
    
    # Validate input
    if not extraction_params:
        raise ValueError("extraction_params must be provided")
    
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Iterate through each page in the PDF
            for page_num, page in enumerate(pdf.pages):
                # Extract words with their bounding boxes
                words = page.extract_words(keep_blank_chars=True, x_tolerance=3, y_tolerance=3)
                
                # Extract keywords from extraction parameters
                keywords = []
                for param in extraction_params:
                    # Add start and end keywords from each parameter set
                    if 'start_keyword' in param:
                        keywords.append(param['start_keyword'])
                    if 'end_keyword' in param and param['end_keyword'] != param.get('start_keyword'):
                        keywords.append(param['end_keyword'])
                
                # Find positions of all specified keywords
                for keyword in keywords:
                    # Find all occurrences of the keyword
                    keyword_positions = []
                    
                    for i, word in enumerate(words):
                        if keyword.lower() in word["text"].lower():
                            # Get the position of the keyword
                            position = {
                                "page": page_num,
                                "x0": word["x0"],
                                "top": word["top"],
                                "x1": word["x1"],
                                "bottom": word["bottom"],
                                "text": word["text"]
                            }
                            
                            # Try to get the value if it's on the same line or next to the keyword
                            value = ""
                            value_bbox = None
                            
                            # Check if there are words to the right on the same line
                            same_line_words = [w for w in words if abs(w["top"] - word["top"]) < 5 and w["x0"] > word["x1"]]
                            if same_line_words:
                                # Take the first word to the right
                                value = same_line_words[0]["text"]
                                value_bbox = {
                                    "x0": same_line_words[0]["x0"],
                                    "top": same_line_words[0]["top"],
                                    "x1": same_line_words[0]["x1"],
                                    "bottom": same_line_words[0]["bottom"]
                                }
                            
                            # Add the value and its position if found
                            position["value"] = value
                            position["value_bbox"] = value_bbox
                            
                            # Add to the list of positions for this keyword
                            keyword_positions.append(position)
                    
                    # Add all positions found for this keyword
                    if keyword_positions:
                        # Use a compound key with keyword and page to avoid overwriting
                        key = f"{keyword}_{page_num}"
                        bbox_data[key] = keyword_positions
    
    except Exception as e:
        print(f"Error extracting bounding box coordinates: {str(e)}")
    
    return bbox_data

def create_document_json(pdf_path, extraction_params):
    """
    Process a PDF file, extract document details and additional data,
    and create a JSON file with the extracted data. Supports merging
    fields marked with (+1) suffix.
    
    Args:
        pdf_path (str): Path to the PDF file
        extraction_params (list): List of parameter dictionaries for extraction
        
    Returns:
        str: Path to the created JSON file
    """
    # Check if file exists
    if not os.path.isfile(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return None
        
    # Extract data based on parameters
    extracted_data = extract_pdf_data(pdf_path, extraction_params)
    
    # Process field merging for fields with (+1) suffix
    merged_data = process_field_merging(extracted_data)
    
    # Prepare the JSON structure
    json_data = []
    
    # Add all extracted data to JSON
    for field_name, content_dict in merged_data.items():
        # Post-process to ensure no duplicate keys in the final output and no empty values
        final_fields = {}
        for key, value in content_dict["parsed_data"].items():
            # Skip any empty values
            if value == "" or value is None:
                continue
                
            if isinstance(value, list) and all(v == "" or v is None for v in value):
                continue
                
            # Handle duplicates by merging into lists
            if key in final_fields:
                if isinstance(final_fields[key], list):
                    if isinstance(value, list):
                        final_fields[key].extend([v for v in value if v != "" and v is not None])
                    elif value != "" and value is not None:
                        final_fields[key].append(value)
                else:
                    if isinstance(value, list):
                        non_empty_values = [v for v in value if v != "" and v is not None]
                        if non_empty_values:
                            final_fields[key] = [final_fields[key]] + non_empty_values
                    elif value != "" and value is not None and final_fields[key] != value:
                        final_fields[key] = [final_fields[key], value]
            else:
                # Filter out empty values from lists
                if isinstance(value, list):
                    non_empty_values = [v for v in value if v != "" and v is not None]
                    if non_empty_values:
                        final_fields[key] = non_empty_values if len(non_empty_values) > 1 else non_empty_values[0]
                else:
                    final_fields[key] = value
        
        data_entry = {
            "title": field_name,
            "raw_text": content_dict["raw_text"],
            "formatted_text": content_dict["formatted_text"],
            "fields": final_fields
        }
        json_data.append(data_entry)
    
    # Create JSON file name based on the PDF name
    pdf_filename = os.path.basename(pdf_path)
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    json_filename = f"{pdf_name_without_ext}.json"
    json_path = os.path.join(os.path.dirname(pdf_path), json_filename)
    
    # Save JSON data to file
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, indent=2)
    
    print(f"JSON file created: {json_path}")
    return json_path

def process_field_merging(extracted_data):
    """
    Process and merge fields that have a (+1) suffix in their names.
    Ensures proper handling of duplicate keys during merging.
    
    Args:
        extracted_data (dict): Dictionary containing extracted field data
        
    Returns:
        dict: Processed data with merged fields
    """
    merged_data = {}
    merge_candidates = {}
    
    # First pass: identify fields that need merging
    for field_name in extracted_data.keys():
        if "(+1)" in field_name:
            # Extract the base field name (without the +1)
            base_field_name = field_name.replace("(+1)", "").strip()
            
            # Check if we have the base field
            if base_field_name in extracted_data:
                # Add to merge candidates
                if base_field_name not in merge_candidates:
                    merge_candidates[base_field_name] = []
                merge_candidates[base_field_name].append(field_name)
            else:
                # If base field doesn't exist, keep as is
                merged_data[field_name] = extracted_data[field_name]
        else:
            # Regular field, add to merged data
            merged_data[field_name] = extracted_data[field_name]
    
    # Second pass: perform the merging
    for base_field, extension_fields in merge_candidates.items():
        # Start with the base field data
        base_data = extracted_data[base_field]
        merged_raw_text = base_data["raw_text"]
        merged_formatted_text = base_data["formatted_text"]
        merged_parsed_data = base_data["parsed_data"].copy()
        
        # Merge each extension field
        for ext_field in extension_fields:
            ext_data = extracted_data[ext_field]
            
            # Concatenate raw and formatted text with a separator
            merged_raw_text += "\n\n--- Additional Data ---\n\n" + ext_data["raw_text"]
            merged_formatted_text += "\n\n--- Additional Data ---\n\n" + ext_data["formatted_text"]
            
            # Merge the parsed data dictionaries
            for key, value in ext_data["parsed_data"].items():
                # Skip empty values
                if value == "" or value is None:
                    continue
                    
                if isinstance(value, list) and all(v == "" or v is None for v in value):
                    continue
                
                # If key exists in merged data
                if key in merged_parsed_data:
                    base_value = merged_parsed_data[key]
                    
                    # Both values are lists
                    if isinstance(base_value, list) and isinstance(value, list):
                        merged_parsed_data[key].extend([v for v in value if v != "" and v is not None])
                    # Base value is a list, new value is not
                    elif isinstance(base_value, list):
                        if value != "" and value is not None:
                            merged_parsed_data[key].append(value)
                    # New value is a list, base value is not
                    elif isinstance(value, list):
                        non_empty_values = [v for v in value if v != "" and v is not None]
                        if non_empty_values:
                            merged_parsed_data[key] = [base_value] + non_empty_values
                    # Neither value is a list, but they're different
                    elif base_value != value and value != "" and value is not None:
                        merged_parsed_data[key] = [base_value, value]
                    # Values are identical or new value is empty, keep as is
                else:
                    # Key doesn't exist in base, simply add it if it's not empty
                    if isinstance(value, list):
                        non_empty_values = [v for v in value if v != "" and v is not None]
                        if non_empty_values:
                            merged_parsed_data[key] = non_empty_values if len(non_empty_values) > 1 else non_empty_values[0]
                    else:
                        merged_parsed_data[key] = value
        
        # Clean out any empty values from the merged data
        merged_parsed_data = clean_empty_keys(merged_parsed_data)
        
        # Update the base field with merged data
        merged_data[base_field] = {
            "raw_text": merged_raw_text,
            "formatted_text": merged_formatted_text,
            "parsed_data": merged_parsed_data
        }
    
    return merged_data