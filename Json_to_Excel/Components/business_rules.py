import re
from typing import Dict, List, Any, Tuple, Union, Optional

class BusinessRules:
    """
    Class for implementing custom business rules that transform JSON data
    before it is written to Excel.
    
    This module allows for application-specific transformations that are 
    separate from the core Excel generation functionality.
    """
    
    @staticmethod
    def transform_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all business rules transformations to a single JSON data object.
        
        Args:
            json_data: A dictionary containing the JSON data to transform
            
        Returns:
            The transformed JSON data
        """
        result = json_data.copy()  # Create a copy to avoid modifying the original
        
        # Apply specific transformations - add or remove as needed
        result = BusinessRules.transform_sample_rule(result)
        # result = BusinessRules.transform_another_rule(result)
        # result = BusinessRules.transform_complex_rule(result)
        
        return result
    
    @staticmethod
    def transform_all_data(all_json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to all JSON data entries.
        
        Args:
            all_json_data: Dictionary mapping file paths to their JSON content
            
        Returns:
            Transformed data dictionary
        """
        transformed_data = {}
        
        for file_name, file_json_data in all_json_data.items():
            # Handle different data structures (list or dict)
            if isinstance(file_json_data, list):
                transformed_data[file_name] = [
                    BusinessRules.transform_data(item) 
                    for item in file_json_data
                ]
            else:
                transformed_data[file_name] = BusinessRules.transform_data(file_json_data)
                
        return transformed_data
    
    @staticmethod
    def transform_sample_rule(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example transformation rule - renames fields with a specific pattern.
        
        This function looks for keys that match a pattern and renames them
        to a new format.
        
        Example:
            "old_name_123": "value" becomes:
            "new_name_123": "value"
            
        Args:
            data: The data dictionary to transform
            
        Returns:
            Transformed data dictionary
        """
        result = data.copy()
        
        # Look for fields dictionary if it exists
        fields = result.get('fields', result)
        
        # Find keys matching a pattern
        pattern_keys = [
            key for key in fields.keys() 
            if key.lower().startswith('old_name')
        ]
        
        for key in pattern_keys:
            # Get the original value
            value = fields.get(key)
            
            # Create the new key name
            # Example: "old_name_123" -> "new_name_123"
            suffix = key[len('old_name'):]  # Extract the part after "old_name"
            new_key = f"new_name{suffix}"
            
            # Add the new key with the same value
            fields[new_key] = value
            
            # Optionally remove the old key
            # del fields[key]
        
        # If we were working with a nested 'fields' dictionary, update it
        if 'fields' in result and result['fields'] is not fields:
            result['fields'] = fields
            
        return result
    
    @staticmethod
    def transform_value_formatting(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example transformation rule - formats numeric values.
        
        This function formats numeric string values to ensure consistent
        precision and presentation.
        
        Example:
            "voltage": "3.500000" becomes:
            "voltage": "3.50"
            
        Args:
            data: The data dictionary to transform
            
        Returns:
            Transformed data dictionary
        """
        result = data.copy()
        
        # Look for fields dictionary if it exists
        fields = result.get('fields', result)
        
        # Number formatting pattern
        numeric_pattern = r'^-?\d+\.\d+$'
        
        # Process each field
        for key, value in fields.items():
            if isinstance(value, str) and re.match(numeric_pattern, value):
                try:
                    # Parse the number and format to 2 decimal places
                    numeric_value = float(value)
                    fields[key] = f"{numeric_value:.2f}"
                except ValueError:
                    # If conversion fails, keep the original value
                    continue
        
        # If we were working with a nested 'fields' dictionary, update it
        if 'fields' in result and result['fields'] is not fields:
            result['fields'] = fields
            
        return result
    
    @staticmethod
    def transform_array_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example transformation rule - converts space-separated values to arrays.
        
        This function converts space-separated string values into arrays
        for proper display in Excel with subtitles.
        
        Example:
            "measurements": "12.1 45.6 78.9" becomes:
            "measurements": ["12.1", "45.6", "78.9"]
            
        Args:
            data: The data dictionary to transform
            
        Returns:
            Transformed data dictionary
        """
        result = data.copy()
        
        # Look for fields dictionary if it exists
        fields = result.get('fields', result)
        
        # Find keys that might contain space-separated values
        array_candidate_keys = [
            key for key in fields.keys() 
            if isinstance(fields[key], str) and ' ' in fields[key]
        ]
        
        for key in array_candidate_keys:
            value = fields.get(key)
            
            # Skip if not a string or not containing a space
            if not isinstance(value, str) or ' ' not in value:
                continue
                
            # Parse the values
            try:
                # Split by space
                parts = value.split()
                
                # If we have multiple parts, convert to an array
                if len(parts) > 1:
                    fields[key] = parts
            except Exception as e:
                # If parsing fails, keep the original field
                continue
        
        # If we were working with a nested 'fields' dictionary, update it
        if 'fields' in result and result['fields'] is not fields:
            result['fields'] = fields
            
        return result