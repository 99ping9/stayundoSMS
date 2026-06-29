import os
import sys
import asyncio
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    sys.exit(1)

supabase: Client = create_client(url, key)

async def main():
    print("Starting DB Reset and Seeding for 4 rooms...")
    rooms = ["B동", "C동", "D동", "E동"]
    all_acc = rooms + ["공통메세지", "전체공용"]

    print("1. Truncating accommodations (this will cascade delete reservations and templates)...")
    # Using delete with a condition that matches all (neq is a good way)
    try:
        supabase.table("v3_accommodations").delete().neq("name", "nothing_to_match").execute()
    except Exception as e:
        print("Delete error:", e)

    print("2. Inserting accommodations...")
    data = [{"name": acc} for acc in all_acc]
    supabase.table("v3_accommodations").insert(data).execute()

    print("3. Inserting Templates...")
    common_templates = [
        {"trigger_type": "checkin_food_0900", "send_time": "09:00:00", "subject": "맛집 안내", "content": "{name}님, 입실 전 주변 맛집을 소개해드립니다."},
        {"trigger_type": "checkin_1900", "send_time": "19:00:00", "subject": "저녁 안내", "content": "{name}님, 저녁 식사는 맛있게 하셨나요?"},
        {"trigger_type": "checkout_0900", "send_time": "09:00:00", "subject": "퇴실 안내", "content": "{name}님, 편안한 밤 되셨나요? 11시 퇴실입니다."},
        {"trigger_type": "multinight_0900", "send_time": "09:00:00", "subject": "연박 안내", "content": "{name}님, 연박 안내드립니다."}
    ]

    specific_template_types = [
        {"trigger_type": "checkin_guide_0900", "send_time": "09:00:00", "subject": "체크인 안내"},
        {"trigger_type": "checkin_1450", "send_time": "14:48:00", "subject": "입실 안내"},
        {"trigger_type": "checkout_1900", "send_time": "19:00:00", "subject": "후기 작성 요청"}
    ]

    # Insert common
    for t in common_templates:
        supabase.table("v3_message_templates").insert({
            "accommodation_name": "공통메세지",
            "trigger_type": t["trigger_type"],
            "send_time": t["send_time"],
            "subject": t["subject"],
            "content": t["content"]
        }).execute()

    # Insert specific
    for room in rooms:
        for t in specific_template_types:
            content = f"{{name}}님, {room} {t['subject']} 내용입니다.\n\n[{room} 기본안내]"
            if t['trigger_type'] == 'checkout_1900':
                content = f"{{name}}님, {room}에서의 하루는 어떠셨나요? 소중한 후기를 남겨주세요. \n\n[{room} 기본안내]"
            
            supabase.table("v3_message_templates").insert({
                "accommodation_name": room,
                "trigger_type": t["trigger_type"],
                "send_time": t["send_time"],
                "subject": t["subject"],
                "content": content
            }).execute()

    print("4. Inserting Dummy Reservations...")
    today = datetime.now().date()
    
    reservations = [
        {
            "guest_name": "김비동",
            "phone_number": "010-1111-2222",
            "accommodation_name": "B동",
            "checkin_date": str(today),
            "checkout_date": str(today + timedelta(days=1)),
            "memo": "B동 더미 예약"
        },
        {
            "guest_name": "이씨동",
            "phone_number": "010-3333-4444",
            "accommodation_name": "C동",
            "checkin_date": str(today + timedelta(days=1)),
            "checkout_date": str(today + timedelta(days=2)),
            "memo": "C동 더미 예약"
        },
        {
            "guest_name": "박디동",
            "phone_number": "010-5555-6666",
            "accommodation_name": "D동",
            "checkin_date": str(today - timedelta(days=1)),
            "checkout_date": str(today + timedelta(days=1)),
            "memo": "D동 더미 예약 (연박)"
        },
        {
            "guest_name": "최이동",
            "phone_number": "010-7777-8888",
            "accommodation_name": "E동",
            "checkin_date": str(today),
            "checkout_date": str(today + timedelta(days=1)),
            "memo": "E동 더미 예약"
        }
    ]
    
    supabase.table("v3_reservations").insert(reservations).execute()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
