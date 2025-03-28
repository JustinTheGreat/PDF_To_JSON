import pdfplumber
import re

def find_keyword_position(words, keyword):
    """
    Find the position of a keyword in the extracted words.
    
    Args:
        words (list): List of word dictionaries from pdfplumber
        keyword (str): Keyword to search for
        
    Returns:
        dict: Position information or None if not found
    """
    for word in words:
        if keyword in word['text']:
            return {
                'x0': word['x0'],
                'y0': word['top'],
                'x1': word['x1'],
                'y1': word['bottom']
            }
    return None

def find_nth_occurrence_position(words, keyword, n):
    """
    Find the position of the nth occurrence of a keyword.
    If fewer than n occurrences are found, returns the last occurrence.
    
    Args:
        words (list): List of word dictionaries from pdfplumber
        keyword (str): Keyword to search for
        n (int): Which occurrence to find (1-based indexing)
        
    Returns:
        dict: Position information or None if not found at all
    """
    occurrences = []
    for word in words:
        if keyword in word['text']:
            occurrences.append({
                'x0': word['x0'],
                'y0': word['top'],
                'x1': word['x1'],
                'y1': word['bottom']
            })
    
    if len(occurrences) > 0:
        # If we have fewer occurrences than requested, return the last one
        if len(occurrences) < n:
            return occurrences[-1]
        else:
            return occurrences[n - 1]
    return None

def extract_serial_data(pdf_path, start_keyword, end_keyword, 
                        page_num=0, horiz_margin=100, end_keyword_occurrence=3):
    """
    Extracts text data starting from a specified keyword within specified horizontal boundary
    and ending at the specified occurrence of an end keyword.
    If fewer than the specified occurrences are found, uses the last occurrence.
    
    Args:
        pdf_path (str): Path to the PDF file
        start_keyword (str): Keyword to start extraction from (default: "Serial no.:")
        end_keyword (str): Keyword to end extraction at (default: "[kW]")
        page_num (int): Page number to extract from (default: 0 - first page)
        horiz_margin (float): Horizontal distance in points to expand from start position
        end_keyword_occurrence (int): Which occurrence of end_keyword to stop at (default: 3)
        
    Returns:
        str: Extracted text data
    """
    try:
        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Get the specified page
            if page_num >= len(pdf.pages):
                return f"Error: Page number {page_num} out of range"
            
            page = pdf.pages[page_num]
            
            # Extract page text with bounding boxes for positioning
            words = page.extract_words(keep_blank_chars=True, x_tolerance=3, y_tolerance=3)
            
            # Find starting keyword position
            start_pos = find_keyword_position(words, start_keyword)
            if not start_pos:
                return f"{start_keyword} not found on page {page_num}"
            
            # Find the nth occurrence of ending keyword (or the last occurrence if fewer than n)
            end_pos = find_nth_occurrence_position(words, end_keyword, end_keyword_occurrence)
            if not end_pos:
                # Try a fallback approach for when the end keyword isn't found
                full_text = page.extract_text()
                if start_keyword in full_text:
                    # Extract from start keyword to the end of the page
                    start_idx = full_text.find(start_keyword)
                    return full_text[start_idx:]
                return f"Error: No occurrences of {end_keyword} found"
            
            # Define the initial bounding box
            left = start_pos['x0']
            right = left + horiz_margin
            top = start_pos['y0']
            bottom = end_pos['y1'] + 5  # Add small margin
            
            # Check for negative dimensions and fix if needed
            if bottom < top:
                # Swap top and bottom to ensure positive height
                top, bottom = bottom, top
                print(f"Fixed negative height: swapped top ({top}) and bottom ({bottom})")
            
            if right < left:
                # Swap left and right to ensure positive width
                left, right = right, left
                print(f"Fixed negative width: swapped left ({left}) and right ({right})")
            
            # Create the corrected bounding box
            bbox = (left, top, right, bottom)
            
            # Optional: Log the bounding box for debugging
            print(f"Using bounding box: {bbox}")
            
            # Crop the page to our bounding box
            cropped_page = page.crop(bbox)
            
            # Extract text from the cropped area
            extracted_text = cropped_page.extract_text()
            
            # If no text was extracted, try a different approach
            if not extracted_text:
                # Try extracting the whole page text and filtering
                full_text = page.extract_text()
                if start_keyword in full_text and end_keyword in full_text:
                    start_idx = full_text.find(start_keyword)
                    # Find the correct occurrence of end_keyword
                    curr_idx = start_idx
                    for _ in range(end_keyword_occurrence):
                        end_idx = full_text.find(end_keyword, curr_idx)
                        if end_idx == -1:
                            # If we can't find the next occurrence, use the last found one
                            break
                        curr_idx = end_idx + len(end_keyword)
                    
                    if end_idx > start_idx:
                        # Extract from start to end (including the end keyword)
                        return full_text[start_idx:end_idx + len(end_keyword)]
                    else:
                        # Just extract from start to the end of the page
                        return full_text[start_idx:]
                
            return extracted_text or "No text found in the specified area"
            
    except Exception as e:
        # If the error is specifically about negative width/height, try alternate extraction
        if "negative width or height" in str(e):
            try:
                # Try extracting the whole page text and filtering
                full_text = page.extract_text()
                lines = full_text.split('\n')
                
                # Find lines containing our keywords
                start_line_idx = -1
                end_line_idx = -1
                
                for i, line in enumerate(lines):
                    if start_keyword in line and start_line_idx == -1:
                        start_line_idx = i
                    
                    if end_keyword in line:
                        # Count occurrences to match our target occurrence
                        end_line_count = 0
                        for j in range(i+1):
                            if end_keyword in lines[j]:
                                end_line_count += 1
                        
                        if end_line_count == end_keyword_occurrence:
                            end_line_idx = i
                            break
                
                # If we found both lines, extract the text between them
                if start_line_idx != -1 and end_line_idx != -1 and end_line_idx >= start_line_idx:
                    result = '\n'.join(lines[start_line_idx:end_line_idx+1])
                    return result
                elif start_line_idx != -1:
                    # Just extract from start keyword to end of page
                    result = '\n'.join(lines[start_line_idx:])
                    return result
                
                return f"Fallback extraction failed: Keywords not found in text"
            except Exception as fallback_error:
                return f"Error in fallback extraction: {str(fallback_error)}"
        
        return f"Error extracting data: {str(e)}"  

if __name__ == "__main__":
    pdf_path = "report_v1.pdf"
    
    # # Basic usage with defaults
    # result = extract_serial_data(pdf_path, horiz_margin=200)
    # print(result)
    
    # Example with custom parameters
    result = extract_serial_data(
        pdf_path, 
        start_keyword="Serial no.:", 
        end_keyword="Version Data",
        horiz_margin=200, 
        end_keyword_occurrence=1
    )
    print(result)