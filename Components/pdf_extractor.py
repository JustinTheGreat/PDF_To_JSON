import os
import json
import re
from Components.GeneralInfo import extract_serial_data, find_keyword_position, find_nth_occurrence_position
from Components.business_rules import apply_business_rules

def format_raw_text(field_name, raw_text, forced_keywords=None):
    """
    Apply basic formatting to raw text before parsing. Can add colons to specified keywords,
    effectively converting them to keys.
    
    Args:
        field_name (str): Name of the field for specific formatting rules
        raw_text (str): Raw text to format
        forced_keywords (list): List of keywords to add colons to if missing
        
    Returns:
        str: Formatted raw text
    """
    if not raw_text:
        return raw_text
    
    # Basic formatting to ensure proper line breaks and spacing
    formatted_text = raw_text.strip()
    
    # If we have keywords to force as keys
    if forced_keywords and isinstance(forced_keywords, list):
        # Process each line
        lines = formatted_text.split('\n')
        modified_lines = []
        
        for line in lines:
            modified_line = line
            
            # For each keyword, check if it's in the line (but doesn't already have a colon)
            for keyword in forced_keywords:
                # Escape special regex characters in the keyword
                escaped_keyword = re.escape(keyword)
                
                # Pattern matches the keyword followed by space but not followed by colon
                pattern = f"{escaped_keyword}(\\s+)(?!:)"
                
                # Replace with keyword + colon + space
                modified_line = re.sub(pattern, f"{keyword}:\\1", modified_line)
                
                # Also handle case where keyword is at the end of the line
                if modified_line.strip().endswith(keyword):
                    modified_line = modified_line.rstrip() + ": "
            
            modified_lines.append(modified_line)
            
        formatted_text = '\n'.join(modified_lines)
    
    return formatted_text

def parse_text_to_key_value(text):
    """
    Parse text into key-value pairs where keys are before colons and values are after colons.
    Handles cases where multiple key-value pairs exist on the same line.
    Special handling for values that contain colons (like MAC addresses).
    Always stores values as a list to handle duplicate keys consistently.
    Prevents creating any keys with empty values.
    
    Args:
        text (str): Text to parse
        
    Returns:
        dict: Dictionary of key-value pairs and list of unparsed lines
    """
    parsed_data = {}
    unparsed_lines = []
    
    # Split the text by lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        # Check if the line has colons
        if ':' in line:
            # Use regex to find keys and values with positive lookahead
            import re
            
            # Pattern captures:
            # 1. A key (one or more words without colons)
            # 2. Followed by a colon and space
            # 3. The value up until the next key or end of string
            pattern = r'([^:\s]+(?:\s+[^:\s]+)*):\s+(.*?)(?=\s+[^:\s]+:\s+|$)'
            
            matches = list(re.finditer(pattern, line))
            
            if matches:
                # Process each key-value pair
                for i, match in enumerate(matches):
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    
                    # Skip any keys with empty values
                    if not value:
                        continue
                    
                    # Special handling for the last key if it has a complex value with colons
                    if i == len(matches) - 1:
                        # Check if the match doesn't end at the end of the line
                        match_end = match.start() + len(match.group(0))
                        if match_end < len(line):
                            # Get the remaining part of the line as part of the value
                            # (only if it doesn't match a new key pattern)
                            remaining = line[match_end:].strip()
                            if not re.match(r'^[^:\s]+:\s+', remaining):
                                value = line[match.start() + len(key) + 2:].strip()
                    
                    # Skip if the value is empty after processing
                    if not value:
                        continue
                    
                    # Always store values in a list for consistent handling of duplicate keys
                    if key in parsed_data:
                        if isinstance(parsed_data[key], list):
                            parsed_data[key].append(value)
                        else:
                            # Convert existing single value to a list with both values
                            parsed_data[key] = [parsed_data[key], value]
                    else:
                        # Initialize with a list containing a single value
                        parsed_data[key] = [value]
            else:
                # If no matches found but line has a colon, use simple split
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                
                # Skip any keys with empty values
                if not value:
                    continue
                
                # Always store values in a list for consistent handling of duplicate keys
                if key in parsed_data:
                    if isinstance(parsed_data[key], list):
                        parsed_data[key].append(value)
                    else:
                        # Convert existing single value to a list with both values
                        parsed_data[key] = [parsed_data[key], value]
                else:
                    # Initialize with a list containing a single value
                    parsed_data[key] = [value]
        else:
            # No colons found, add to unparsed lines
            unparsed_lines.append(line)
    
    # Simplify lists with a single item to just the value itself
    for key in list(parsed_data.keys()):
        if isinstance(parsed_data[key], list) and len(parsed_data[key]) == 1:
            parsed_data[key] = parsed_data[key][0]
    
    return parsed_data, unparsed_lines

def apply_special_formatting(field_name, parsed_data, unparsed_lines):
    """
    Apply all special formatting using the business rules module.
    
    Args:
        field_name (str): Name of the field to apply special formatting to
        parsed_data (dict): Dictionary of parsed key-value pairs
        unparsed_lines (list): List of lines that couldn't be parsed with simple rules
        
    Returns:
        dict: Dictionary with formatted data
    """
    return apply_business_rules(field_name, parsed_data, unparsed_lines)