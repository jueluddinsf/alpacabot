#!/usr/bin/env python3
import os
import re

def fix_imports(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Replace "from dice_ai.app" with "from app"
                    modified_content = re.sub(r'from dice_ai\.app', 'from app', content)
                    # Replace "import dice_ai.app" with "import app"
                    modified_content = re.sub(r'import dice_ai\.app', 'import app', modified_content)
                    
                    if content != modified_content:
                        with open(file_path, 'w') as f:
                            f.write(modified_content)
                        print(f"Fixed imports in {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    fix_imports("app")
    print("Import fixes completed!") 