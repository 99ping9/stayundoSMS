import os
import glob

files = glob.glob('**/*.py', recursive=True) + glob.glob('**/*.sql', recursive=True)

for file in files:
    if file == 'rename_to_v3.py' or 'chowonsms2-main' in file: 
        continue
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content.replace('v2_accommodations', 'v3_accommodations')\
                             .replace('v2_reservations', 'v3_reservations')\
                             .replace('v2_message_templates', 'v3_message_templates')\
                             .replace('v2_sms_logs', 'v3_sms_logs')
                             
        if content != new_content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated {file}')
    except Exception as e:
        print(f"Error on {file}: {e}")
