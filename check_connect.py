import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 로드
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Checking connection to: {url}")

if not url or not key:
    print("❌ 실패: .env 파일에 SUPABASE_URL 또는 SUPABASE_KEY가 없습니다.")
    sys.exit(1)

try:
    supabase: Client = create_client(url, key)
    
    # 연결 테스트 시도
    # 존재하지 않는 테이블이라도 쿼리를 보내보면 연결 여부를 알 수 있음
    print("Connecting...")
    
    try:
        response = supabase.table("v3_accommodations").select("*", count="exact").limit(1).execute()
        print("✅ 연결 성공! (테이블도 정상적으로 존재함)")
        print(f"데이터 개수: {response.count}")
        
    except Exception as e:
        # Pydantic 모델이나 API 에러 분석
        error_str = str(e)
        if "PGRST205" in error_str or "relation" in error_str and "does not exist" in error_str:
            print("✅ 연결 성공! (단, DB에 테이블이 없습니다)")
            print("👉 Supabase SQL Editor에서 schema.sql을 실행해주세요.")
        elif "PGRST301" in error_str:
             print("✅ 연결 성공! (JWT/권한 문제일 수 있음)")
        else:
            print("❌ 연결 실패 또는 알 수 없는 오류")
            print(f"에러 내용: {e}")

except Exception as e:
    print("❌ 치명적 오류 (URL 형식이 잘못되었거나 라이브러리 문제)")
    print(e)
