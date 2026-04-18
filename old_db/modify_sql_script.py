import os
import re

# --- 1. Setup: Configuration ---
INPUT_FILE = 'backup-on-2026-04-17-19-03-55.sql'   # The name of your original SQL file
OUTPUT_FILE = 'backup-on-2026-04-17-19-03-55-cleaned_2.sql' # The name of the modified file

# Define all the modifications you want to make here.
# Key: The text to find | Value: The text to replace it with
modifications = {
    "'0000-00-00'": "'1970-01-01'"   # Fix the invalid MySQL dates
    # "ENGINE=MyISAM": "ENGINE=InnoDB", # Example: Modernize the engine
    # "TYPE=InnoDB": "ENGINE=InnoDB",   # Example: Fix deprecated syntax
    # You can add hundreds of these pairs!
}

def fix_data_wizyty_rok_mismatch(content):
    """Fix mismatches between data_wizyty year and rok column in wizyty table.
    
    The rok column contains the correct year. If the year in data_wizyty doesn't
    match, it will be corrected to match rok.
    """
    # Pattern: 'YYYY-MM-DD', YYYY, (matches data_wizyty date and rok value)
    pattern = r"'(\d{4})-(\d{2})-(\d{2})',\s*(\d{4}),"
    
    def replacer(match):
        data_year = match.group(1)   # Year from data_wizyty
        month = match.group(2)
        day = match.group(3)
        rok_year = match.group(4)    # Year from rok column
        
        # If they don't match, use the rok year
        if data_year != rok_year:
            return f"'{rok_year}-{month}-{day}', {rok_year},"
        else:
            return match.group(0)    # Return unchanged
    
    fixed_content = re.sub(pattern, replacer, content)
    return fixed_content

def modify_sql_script(input_path, output_path, changes_dict):
    try:
        # Check if file exists
        if not os.path.exists(input_path):
            print(f"Error: The file '{input_path}' was not found.")
            return

        # 2. Read the original content
        with open(input_path, 'r', encoding='utf-8') as file:
            content = file.read()

        print(f"Applying {len(changes_dict)} modifications...")

        # 3. Apply the changes
        modified_content = content
        for find_text, replace_text in changes_dict.items():
            # count=... is optional, but it's nice to see how many changes happened
            count = modified_content.count(find_text)
            modified_content = modified_content.replace(find_text, replace_text)
            print(f" - Replaced '{find_text}' with '{replace_text}' ({count} times)")

        # Fix data_wizyty and rok mismatches
        print("\nFixing data_wizyty/rok year mismatches in wizyty table...")
        modified_content = fix_data_wizyty_rok_mismatch(modified_content)
        print(" - Corrected dates where year in data_wizyty didn't match rok column")

        # 4. Save the results
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        print("-" * 30)
        print(f"Success! Modified script saved as: {output_path}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Execute the function ---
if __name__ == "__main__": # czyli wykonuje się tylko jeśli uruchomię to za pomocą python3 modify_sql_script.py, a jeśli zaimportuję to jako moduł, to się nie wykona
    modify_sql_script(INPUT_FILE, OUTPUT_FILE, modifications)