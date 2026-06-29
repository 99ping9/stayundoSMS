import os
import glob
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Update Files
def update_files():
    files = glob.glob('**/*.py', recursive=True) + glob.glob('**/*.sql', recursive=True) + glob.glob('**/*.html', recursive=True)
    for file in files:
        if 'rename_rooms.py' in file or 'chowonsms2-main' in file:
            continue
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = content.replace('초원브릿지', '숙소1').replace('초원스페이스', '숙소2')
            if content != new_content:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file}")
        except Exception as e:
            pass

# 2. Update DB
def update_db():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("Missing Supabase credentials.")
        return

    supabase: Client = create_client(url, key)

    try:
        print("Inserting new accommodations...")
        supabase.table("v3_accommodations").upsert([{"name": "숙소1"}, {"name": "숙소2"}]).execute()
        
        print("Updating templates accommodation_name...")
        supabase.table("v3_message_templates").update({"accommodation_name": "숙소1"}).eq("accommodation_name", "초원브릿지").execute()
        supabase.table("v3_message_templates").update({"accommodation_name": "숙소2"}).eq("accommodation_name", "초원스페이스").execute()
        
        print("Updating reservations accommodation_name...")
        supabase.table("v3_reservations").update({"accommodation_name": "숙소1"}).eq("accommodation_name", "초원브릿지").execute()
        supabase.table("v3_reservations").update({"accommodation_name": "숙소2"}).eq("accommodation_name", "초원스페이스").execute()

        print("Updating template content and subjects...")
        res = supabase.table("v3_message_templates").select("*").execute()
        if res.data:
            for row in res.data:
                content_changed = '초원브릿지' in row['content'] or '초원스페이스' in row['content']
                subject_changed = row['subject'] and ('초원브릿지' in row['subject'] or '초원스페이스' in row['subject'])
                
                if content_changed or subject_changed:
                    new_content = row['content'].replace('초원브릿지', '숙소1').replace('초원스페이스', '숙소2')
                    new_subject = None
                    if row['subject']:
                        new_subject = row['subject'].replace('초원브릿지', '숙소1').replace('초원스페이스', '숙소2')
                    
                    update_data = {"content": new_content}
                    if row['subject']:
                        update_data["subject"] = new_subject
                        
                    supabase.table("v3_message_templates").update(update_data).eq("id", row['id']).execute()

        print("Deleting old accommodations...")
        supabase.table("v3_accommodations").delete().eq("name", "초원브릿지").execute()
        supabase.table("v3_accommodations").delete().eq("name", "초원스페이스").execute()
        
        print("DB updated successfully.")
    except Exception as e:
        print(f"DB Update Error: {e}")

if __name__ == '__main__':
    update_files()
    update_db()
