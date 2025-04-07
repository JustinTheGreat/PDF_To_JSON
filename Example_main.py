from simple_selection import process_single_file_terminal

# Main execution
if __name__ == "__main__":
    # Define extraction parameters for different sections (page_num starts at 0)
    extraction_params = [
        {
            "field_name": "Customer Sheet",
            "start_keyword": "BA:",
            "end_keyword": "FW package",
            "page_num": 0,
            "horiz_margin": 500,
            "end_keyword_occurrence": 1
        },
        {
            "field_name": "EOL Test",
            "start_keyword": "Parts",
            "end_keyword": "Test load",
            "page_num": 0,
            "horiz_margin": 100,
            "end_keyword_occurrence": 1,
            "left_move": 10
        },
        {
            "field_name": "EOL Test(+1)",
            "start_keyword": "Typ",
            "page_num": 0,
            "horiz_margin": 50,
            "left_move": 10,
            "end_break_line_count": 4,
        },
        {
            "field_name": "EOL Test(+1)",
            "start_keyword": "Comment",
            "page_num": 0,
            "horiz_margin": 100,
            "end_break_line_count": 4,
            "left_move": 30
        },
        {
            "field_name": "EOL Test(Chart)",
            "Top Title": "True",
            "Left Title": "True",
            "Priority Side": "Left",
        },
        {
            "field_name": "Used Measurement Device(s)",
            "start_keyword": "vHysense:",
            "end_keyword": "(Ripple)",
            "page_num": 0,
            "horiz_margin": 150,
            "end_keyword_occurrence": 1,
        },
        {
            "field_name": "Used Measurement Device(s)(+1)",
            "start_keyword": "HAI-Board:",
            "end_keyword": "LEM",
            "page_num": 0,
            "horiz_margin": 150,
            "end_keyword_occurrence": 1,
        },
        # Page 2 Functions
        {
            "field_name": "Voltage Calibration UDC",
            "start_keyword": "Demand Value",
            "page_num": 1,
            "horiz_margin": 80,
            "remove_breaks_before": ["[V]"],
            "end_break_line_count": 17,
        },
        {
            "field_name": "Voltage Calibration UDC(+1)",
            "start_keyword": "Actual Value",
            "page_num": 1,
            "horiz_margin": 80,
            "end_break_line_count": 16,
        },
        {
            "field_name": "Voltage Calibration UDC(+1)",
            "start_keyword": "Reference",
            "page_num": 1,
            "horiz_margin": 60,
            "remove_breaks_before": ["Value"],
            "end_break_line_count": 17,
        },
        {
            "field_name": "Voltage Calibration UDC(+1)",
            "start_keyword": "Deviation [V]",
            "page_num": 1,
            "horiz_margin": 90,
            "end_break_line_count": 16,
        },
        {
            "field_name": "Voltage Calibration UDC(+1)",
            "start_keyword": "Deviation",
            "start_keyword_occurrence": 1,
            "page_num": 1,
            "horiz_margin": 90,
            "remove_breaks_before": ["[%"],
            "end_break_line_count": 17,
        },
        {
            "field_name": "Voltage Calibration UDC(Chart)",
            "Top Title": "True",
        },
        # Page 3 Functions
        # Positive Current Calibration Chart (Chart 1)
        {
            "field_name": "Positive Current Calibration",
            "start_keyword": "Demand Value",
            "page_num": 2,
            "horiz_margin": 80,
            "remove_breaks_before": ["[A]"],
            "end_break_line_count": 15,
        },
        {
            "field_name": "Positive Current Calibration(+1)",
            "start_keyword": "Actual Value",
            "page_num": 2,
            "horiz_margin": 80,
            "end_break_line_count": 14,
        },
        {
            "field_name": "Positive Current Calibration(+1)",
            "start_keyword": "Reference",
            "page_num": 2,
            "horiz_margin": 60,
            "remove_breaks_before": ["Value"],
            "end_break_line_count": 15,
        },
        {
            "field_name": "Positive Current Calibration(+1)",
            "start_keyword": "Deviation [A]",
            "page_num": 2,
            "horiz_margin": 90,
            "end_break_line_count": 14,
        },
        {
            "field_name": "Positive Current Calibration(+1)",
            "start_keyword": "Deviation",
            "start_keyword_occurrence": 1,
            "page_num": 2,
            "horiz_margin": 90,
            "remove_breaks_before": ["[%"],
            "end_break_line_count": 15,
        },
        {
            "field_name": "Positive Current Calibration(Chart)",
            "Top Title": "True",
        },
        # Negative Current Calibration (Chart 2)
                {
            "field_name": "Negative Current Calibration",
            "start_keyword": "Demand Value",
            "start_keyword_occurrence": 2,
            "page_num": 2,
            "horiz_margin": 80,
            "remove_breaks_before": ["[A]"],
            "end_break_line_count": 14,
        },
        {
            "field_name": "Negative Current Calibration(+1)",
            "start_keyword": "Actual Value",
            "start_keyword_occurrence": 2,
            "page_num": 2,
            "horiz_margin": 80,
            "end_break_line_count": 13,
        },
        {
            "field_name": "Negative Current Calibration(+1)",
            "start_keyword": "Reference",
            "start_keyword_occurrence": 2,
            "page_num": 2,
            "horiz_margin": 60,
            "remove_breaks_before": ["Value"],
            "end_break_line_count": 15,
        },
        {
            "field_name": "Negative Current Calibration(+1)",
            "start_keyword": "Deviation [A]",
            "start_keyword_occurrence": 2,
            "page_num": 2,
            "horiz_margin": 90,
            "end_break_line_count": 13,
        },
        {
            "field_name": "Negative Current Calibration(+1)",
            "start_keyword": "Deviation",
            "start_keyword_occurrence": 3,
            "page_num": 2,
            "horiz_margin": 90,
            "remove_breaks_before": ["[%"],
            "end_break_line_count": 14,
        },
        {
            "field_name": "Negative Current Calibration(Chart)",
            "Top Title": "True",
        },
    ]

    process_single_file_terminal(extraction_params)
    
    # Use the multiple GUI function from the GUI module
    #launch_mode_selection_dialog(extraction_params, process_multiple_files)
    
    # Alternatively, you could use the custom options dialog:
    # launch_custom_options_dialog(extraction_params, process_multiple_files)