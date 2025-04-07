# PDF Extraction System: Usage Guide

This guide focuses on using the product to extract structured data from PDF documents and explains how the extraction process works.

## Overview of main.py

The `main.py` script serves as the entry point for the PDF extraction system. It:

1. Takes a PDF file path as input
2. Defines extraction parameters for different sections
3. Processes the PDF according to these parameters
4. Creates a structured JSON output with the extracted data

## Getting Started
### Installation and Setup
Ensure you have Python installed on your system (Python 3.6 or later recommended).

Install the required dependencies:
```
pip install pdfplumber
```

## Basic Usage Example

Here's a simple example of using `main.py`:

```python
import os
import json
from Components.pdf_processor import create_document_json

if __name__ == "__main__":
    # Get PDF file path from user
    pdf_path = input("Enter the path to the PDF file: ")
    pdf_path = pdf_path.strip('"\'')
    
    # Define extraction parameters
    extraction_params = [
        {
            "field_name": "General Info",
            "start_keyword": "Customer Information:",
            "end_keyword": "Equipment Details",
            "page_num": 0,
            "horiz_margin": 300
        }
    ]
    
    # Process the PDF
    json_path = create_document_json(pdf_path, extraction_params)
    
    # Display the results
    if json_path:
        with open(json_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
            print("\nJSON Content:")
            print(json.dumps(content, indent=2))
    else:
        print("Failed to create JSON file.")
```

## Default Auto-Formatting

The system automatically performs these actions without additional parameters:

1. **Key-Value Detection**: Identifies "Key: Value" patterns and structures them
2. **List Conversion**: Single values are kept as strings, multiple values become arrays
3. **Empty Value Removal**: Keys with empty values are automatically removed
4. **Line Break Normalization**: Ensures consistent line breaks in the formatted text
5. **Duplicate Key Handling**: Merges duplicate keys into arrays
6. **Whitespace Trimming**: Removes extra whitespace from keys and values

## Available Extraction Parameters

All available parameters that can be used in your extraction definition:

| Parameter | Type | Description |
|-----------|------|-------------|
| `field_name` | string | **Required**. Name for the extracted field (use (+1) suffix for continuation fields and (Chart) suffix for chart conversion) |
| `start_keyword` | string | **Required**. Keyword to start extraction from |
| `end_keyword` | string or null | Keyword to end extraction at (can be null if using line breaks) |
| `page_num` | integer | Page number to extract from (0-based, default: 0) |
| `horiz_margin` | float | Horizontal distance to expand from start position (default: 200) |
| `start_keyword_occurrence` | integer | Which occurrence of start_keyword to use (default: 1) |
| `end_keyword_occurrence` | integer | Which occurrence of end_keyword to stop at (default: 1) |
| `vertical_margin` | float or null | Vertical distance to expand from keyword position |
| `left_move` | float | Distance to move the left coordinate leftward (default: 0) |
| `end_break_line_count` | integer or null | Stop extraction after this many newlines |
| `forced_keywords` | array or null | List of keywords to add colons to if missing |
| `remove_breaks_before` | array or null | List of words to remove line breaks before them |
| `remove_breaks_after` | array or null | List of words to remove line breaks after them |

### Chart-Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `top_title` | boolean | Use top row as column titles for chart processing |
| `left_title` | boolean | Use left column as row titles for chart processing |
| `priority_side` | string | Primary grouping for chart ('top' or 'left') |

### Table-Specific Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `table_top_labeling` | boolean | Use top row as keys for table processing |
| `table_left_labeling` | boolean | Use left column as keys for table processing |
| `table_structure` | string | Structure type for table ('top_only', 'left_only', 'top_main', 'left_main') |
| `min_column_width` | integer | Minimum width for columns when using space delimiter |

## How the Extraction Process Works

The PDF extraction system follows this pipeline:

### 1. Initial Extraction
- Locates the `start_keyword` on the specified page
- Creates a bounding box extending horizontally by `horiz_margin`
- Extracts text within this area until the `end_keyword` or other limits

   ```
    <--Horizontal Margin Manually Set-->
   ┌─────────────────────────────────┐
   │ Start Keyword                   │
   │ Content to extract...           │
   │ ...                             │
   │ ...                             │
   │ End Keyword                     │
   └─────────────────────────────────┘
   ```

### 2. Text Formatting
- Adds colons to `forced_keywords` if they're missing
- Removes line breaks before/after specified words
- Prepares the text for structured parsing

### 3. Key-Value Parsing
- Identifies key-value pairs based on colons (e.g., "Name: John")
- Creates a dictionary with these pairs
- Collects unparsed lines for further processing

### 4. Field Merging
- Combines fields marked with (+1) suffix (e.g., "Report" and "Report(+1)")
- Maintains proper structure for duplicate keys

### 5. Chart Processing
- Converts fields marked with (Chart) suffix to structured format
- Organizes data based on chart parameters (top_title, left_title, etc.)

### 6. JSON Structure Creation
- Creates the final JSON structure with:
  - Field title
  - Raw extracted text
  - Formatted text
  - Structured field data


## Extraction Parameter Examples

### Basic Text Extraction

```python
{
    "field_name": "General Info",
    "start_keyword": "Customer Information:",
    "end_keyword": "Equipment Details",
    "page_num": 0,
    "horiz_margin": 300
}
```

### Using Vertical Margin

```python
{
    "field_name": "Equipment Specs",
    "start_keyword": "Equipment Details",
    "end_keyword": None,  # No end keyword
    "page_num": 0,
    "horiz_margin": 350,
    "vertical_margin": 200  # Limit vertical extraction to 200 points
}
```

### Using Forced Keywords

```python
{
    "field_name": "Technical Parameters",
    "start_keyword": "Parameters",
    "end_keyword": "Test Results",
    "page_num": 1,
    "horiz_margin": 400,
    "forced_keywords": ["Serial Number", "Model", "Voltage", "Current", "Power"]
}
```

### Line Break Handling

```python
{
    "field_name": "Test Results",
    "start_keyword": "Test Results",
    "end_keyword": "Certification",
    "page_num": 1,
    "horiz_margin": 450,
    "remove_breaks_before": ["passed", "failed", "warning"],
    "remove_breaks_after": ["Test:", "Result:"]
}
```

### Limited Line Breaks

```python
{
    "field_name": "Certification",
    "start_keyword": "Certification",
    "end_keyword": None,  # No end keyword
    "page_num": 1,
    "horiz_margin": 350,
    "end_break_line_count": 10  # Stop after 10 line breaks
}
```

### Multi-Page Content with Continuation

```python
# First page
{
    "field_name": "Maintenance Records",
    "start_keyword": "Maintenance History",
    "end_keyword": "End of Records",
    "page_num": 2,
    "horiz_margin": 500
},
# Continuation on next page
{
    "field_name": "Maintenance Records(+1)",
    "start_keyword": "Continued from previous page",
    "end_keyword": "Recommendations",
    "page_num": 3,
    "horiz_margin": 500
}
```

### Chart Data Processing

```python
{
    "field_name": "Performance Data(Chart)",
    "start_keyword": "Performance Metrics",
    "end_keyword": "Graph Data End",
    "page_num": 4,
    "horiz_margin": 450,
    "top_title": True,  # Use top row as column titles
    "left_title": True,  # Use left column as row titles
    "priority_side": "left"  # Make left titles the primary grouping
}
```

### Table Processing

```python
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
}
```

## Understanding the Extraction Logic

### Bounding Box Creation

The system creates a bounding box for extraction:
- Starts at the `start_keyword` position
- Extends horizontally by `horiz_margin` points
- Extends vertically to `end_keyword` or by `vertical_margin` if specified
- Can be shifted left by `left_move` points

### Keyword Occurrence Selection

- `start_keyword_occurrence` selects which occurrence of the start keyword to use
- `end_keyword_occurrence` selects which occurrence of the end keyword to stop at
- This allows targeting specific sections when keywords appear multiple times

### Alternative Extraction Methods

When the default bounding box method fails, the system tries:
1. **Text-based extraction**: Finds the start and end keywords in the full page text
2. **Line-based extraction**: Extracts by line numbers instead of coordinates

### Field Continuation Logic

When using the (+1) suffix in field names:
1. Extracts the base field and continuation field separately
2. Merges their text with a separator
3. Combines their structured data, properly handling duplicates
4. Preserves the base field name in the final output

## Tips for Effective Extraction

1. **Start broad, then narrow down**: Begin with wider margins and refine based on results
2. **Use visual inspection**: Check PDF layouts to identify start/end keywords
3. **Try multiple approaches**: If one set of parameters doesn't work, try different keywords or boundaries
4. **Handle multi-page content**: Use the (+1) suffix for content that spans pages
5. **Forced keywords**: Use when a PDF has inconsistent formatting
6. **Line break handling**: Use when text layout affects parsing

## Debugging Extraction Issues

If extraction isn't working as expected:

1. Check that the `start_keyword` exists exactly as specified in the PDF
2. Verify the page number (remember page numbering starts at 0)
3. Try increasing the `horiz_margin` to capture more content
4. Use `start_keyword_occurrence` if the keyword appears multiple times
5. For content spanning pages, ensure the continuation field uses the (+1) suffix
6. Check for invisible characters or formatting that might affect keyword matching

*Side Note: I'd recommend feeding all the files into AI (Claude.ai recommended) to help give you more specific use-case guide with this program*