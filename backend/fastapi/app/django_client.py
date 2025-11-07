"""
Django API Client for FastAPI
FastAPI에서 Django API를 호출하여 데이터를 저장/조회
"""
import httpx
import os
from typing import Optional, Dict, Any


DJANGO_BASE_URL = os.getenv("DJANGO_BASE_URL", "http://localhost:8000")
DJANGO_API_KEY = os.getenv("DJANGO_API_KEY", "")  # 선택적: API Key 인증


class DjangoClient:
    """Django API 클라이언트"""
    
    def __init__(self):
        self.base_url = DJANGO_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
        }
        if DJANGO_API_KEY:
            self.headers["Authorization"] = f"Bearer {DJANGO_API_KEY}"
    
    async def get_character(self, character_id: int) -> Optional[Dict[str, Any]]:
        """캐릭터 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/characters/{character_id}/",
                    headers=self.headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            print(f"[Django Client] Failed to get character: {e}")
            return None
    
    async def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        user_token: str = None,
        token_usage: int = 0,
        model_version: str = "",
        metadata: Dict = None
    ) -> Optional[Dict[str, Any]]:
        """메시지 저장"""
        try:
            # 사용자 토큰이 있으면 사용, 없으면 기본 헤더 사용
            headers = self.headers.copy()
            if user_token:
                headers["Authorization"] = f"Bearer {user_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/conversations/{conversation_id}/add_message/",
                    json={
                        "role": role,
                        "content": content,
                        "token_usage": token_usage,
                        "model_version": model_version,
                        "metadata": metadata or {},
                    },
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    print(f"[Django Client] Failed to save message: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            print(f"[Django Client] Failed to save message: {e}")
            return None
    
    async def create_generation_job(
        self,
        user_token: str,
        job_type: str,
        input_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """이미지 생성 작업 생성"""
        try:
            headers = self.headers.copy()
            if user_token:
                headers["Authorization"] = f"Bearer {user_token}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/generation-jobs/",
                    json={
                        "job_type": job_type,
                        "input_data": input_data,
                    },
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code in [200, 201]:
                    job_data = response.json()
                    job_id = job_data.get("id")
                    print(f"[Django Client] ✅ Job created successfully: ID={job_id}, Status={job_data.get('status')}")
                    print(f"[Django Client] Full response: {job_data}")
                    return job_data
                else:
                    print(f"[Django Client] ❌ Failed to create job: {response.status_code}")
                    print(f"[Django Client] Response: {response.text}")
                    return None
        except Exception as e:
            print(f"[Django Client] ❌ Failed to create job: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def update_generation_job(
        self,
        job_id: int,
        status: str,
        result_data: Dict[str, Any] = None,
        error_message: str = None,
        user_token: str = None
    ) -> Optional[Dict[str, Any]]:
        """이미지 생성 작업 상태 업데이트"""
        if job_id is None:
            print(f"[Django Client] ❌ Cannot update job: job_id is None")
            return None

        try:
            payload = {"status": status}
            if result_data:
                payload["result_data"] = result_data
            if error_message:
                payload["error_message"] = error_message

            headers = self.headers.copy()
            if user_token:
                headers["Authorization"] = f"Bearer {user_token}"

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v1/generation-jobs/{job_id}/",
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    print(f"[Django Client] ✅ Job {job_id} updated: {status}")
                    return response.json()
                else:
                    print(f"[Django Client] ❌ Failed to update job {job_id}: {response.status_code}")
                    print(f"[Django Client] Response: {response.text}")
                    return None
        except Exception as e:
            print(f"[Django Client] ❌ Failed to update job {job_id}: {e}")
            import traceback
            traceback.print_exc()
            return None


# 싱글톤 인스턴스
django_client = DjangoClient()

