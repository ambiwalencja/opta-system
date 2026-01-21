import os

# --- 1. Setup: Configuration ---
INPUT_FILE = 'backup-on-2026-01-21-15-05-55.sql'   # The name of your original SQL file
OUTPUT_FILE = 'backup-on-2026-01-21-15-05-55-cleaned.sql' # The name of the modified file

# Define all the modifications you want to make here.
# Key: The text to find | Value: The text to replace it with
modifications = {
    "'0000-00-00'": "'1970-01-01'"   # Fix the invalid MySQL dates
    # "ENGINE=MyISAM": "ENGINE=InnoDB", # Example: Modernize the engine
    # "TYPE=InnoDB": "ENGINE=InnoDB",   # Example: Fix deprecated syntax
    # You can add hundreds of these pairs!
}

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