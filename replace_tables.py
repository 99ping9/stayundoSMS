import os
import glob

tables = ['v3_accommodations', 'v3_reservations', 'v3_message_templates', 'v3_sms_logs']

files = glob.glob('**/*.py', recursive=True) + glob.glob('**/*.sql', recursive=True)

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    orig_content = content
    
    if file.endswith('.sql'):
        # For SQL, replace bare words
        for t in tables:
            content = content.replace(' ' + t, ' v2_' + t)
            content = content.replace('(' + t, '(v2_' + t)
    else:
        # For Python files, replace string literals
        for t in tables:
            content = content.replace('"' + t + '"', '"v2_' + t + '"')
            content = content.replace("'" + t + "'", "'v2_" + t + "'")

    if content != orig_content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {file}')
