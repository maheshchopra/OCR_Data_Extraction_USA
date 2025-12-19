# Add this function after the validation functions, before find_pdf_files_in_inbox()
def create_detailed_billing_dataframe(result: dict, source_filename: str) -> Optional[str]:
    """
    Create a pandas DataFrame from detailed_billing_rows and save it to a CSV file.
    
    Args:
        result: The extracted bill data dictionary
        source_filename: The original PDF filename (without extension)
        
    Returns:
        Path to the saved CSV file, or None if pandas is not available or no data exists
    """
    
    detailed_billing_rows = result.get("detailed_billing_rows")
    if not detailed_billing_rows:
        return None
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(detailed_billing_rows)
        
        # Reorder columns to match the bill structure
        column_order = [
            "meter_number",
            "service_category",
            "service_from_date",
            "service_through_date",
            "previous_reading",
            "current_reading",
            "multiplier",
            "consumption_units",
            "power_factor",
            "rate_code",
            "unit_charge",
            "amount"
        ]
        
        # Only include columns that exist in the DataFrame
        available_columns = [col for col in column_order if col in df.columns]
        df = df[available_columns]
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        detailed_billing_dir = os.path.join(script_dir, "processed", "detailed_billing")
        
        # Create directory if it doesn't exist
        if not os.path.exists(detailed_billing_dir):
            os.makedirs(detailed_billing_dir)
        
        # Create filename
        csv_filename = f"{source_filename}_detailed_billing.csv"
        csv_path = os.path.join(detailed_billing_dir, csv_filename)
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        
        print(f"Saved detailed billing table to: {csv_path}", file=sys.stderr)
        
        return csv_path
        
    except Exception as e:
        print(f"Error creating detailed billing DataFrame: {e}", file=sys.stderr)
        return None