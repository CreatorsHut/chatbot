"""
Supabase 스토리지 클라이언트
이미지 생성 후 Supabase에 저장
"""

import os
from datetime import datetime
from typing import Optional
from supabase import create_client, Client

# 환경변수
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "generated-images")

# Supabase 클라이언트 초기화
supabase_client: Optional[Client] = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print(f"[Supabase] Connected to Supabase: {SUPABASE_URL[:50]}...")
        print(f"[Supabase] Bucket: {SUPABASE_BUCKET}")
    except Exception as e:
        print(f"[Supabase] Connection failed: {e}")
        supabase_client = None
else:
    print("[Supabase] SUPABASE_URL or SUPABASE_SERVICE_KEY not configured")


def get_supabase_client() -> Optional[Client]:
    """Supabase 클라이언트 반환"""
    return supabase_client


def is_supabase_available() -> bool:
    """Supabase 사용 가능 여부"""
    return supabase_client is not None


def upload_image_to_supabase(
    image_url: str,
    user_id: int,
    filename: str = "image.png"
) -> Optional[str]:
    """
    이미지를 URL에서 다운로드한 후 Supabase에 업로드

    Args:
        image_url: DALL-E에서 생성된 이미지 URL
        user_id: 사용자 ID
        filename: 저장할 파일명

    Returns:
        Supabase 공개 URL 또는 None
    """
    if not supabase_client:
        print("[Supabase] ❌ Supabase client not available")
        return None

    try:
        import requests
        from io import BytesIO

        print(f"\n[Supabase] ========================================")
        print(f"[Supabase] Downloading image from DALL-E URL...")
        print(f"[Supabase] URL: {image_url[:80]}...")

        # DALL-E URL에서 이미지 다운로드
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            print(f"[Supabase] ❌ Failed to download image: {response.status_code}")
            return None

        image_data = BytesIO(response.content)

        # 파일 경로 구성: {user_id}/{YYYY-MM-DD}/{timestamp}_{filename}
        now = datetime.utcnow()
        date_folder = now.strftime("%Y-%m-%d")
        timestamp = int(now.timestamp())

        file_name = f"{timestamp}_{filename}"
        file_path = f"{user_id}/{date_folder}/{file_name}"

        print(f"[Supabase] Uploading to bucket: {SUPABASE_BUCKET}")
        print(f"[Supabase] File path: {file_path}")

        # Supabase에 업로드
        result = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
            path=file_path,
            file=image_data.getvalue(),
            file_options={"content-type": "image/png"}
        )

        # 공개 URL 생성
        public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)

        print(f"[Supabase] ✅ Image uploaded successfully!")
        print(f"[Supabase] Public URL: {public_url}")
        print(f"[Supabase] ========================================\n")

        return public_url

    except Exception as e:
        print(f"\n[Supabase] ❌ ========================================")
        print(f"[Supabase] Upload failed!")
        print(f"[Supabase] Error: {str(e)}")
        print(f"[Supabase] ========================================\n")
        import traceback
        traceback.print_exc()
        return None
