"""
백그라운드 작업 정의

RQ(Redis Queue)를 통해 실행되는 비동기 작업들
"""

import os
from typing import Dict, Any, Optional


def generate_image_task(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    job_id: Optional[int] = None,
    user_token: str = "",
) -> Dict[str, Any]:
    """
    이미지 생성 백그라운드 작업
    
    Args:
        prompt: 이미지 생성 프롬프트
        size: 이미지 크기
        quality: 품질 (standard/hd)
        job_id: Django DB의 GenerationJob ID
        user_token: 사용자 JWT 토큰
    
    Returns:
        결과 딕셔너리 (url, revised_prompt 등)
    """
    from .django_client import django_client
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DALLE_MODEL = os.getenv("DALLE_MODEL", "dall-e-3")
    
    print(f"[Task] Starting image generation: {prompt[:50]}...")
    
    try:
        # DALL-E API 호출
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": DALLE_MODEL,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": quality,
        }
        
        # 동기 HTTP 요청 (백그라운드 워커에서는 동기 방식 사용)
        import requests
        response = requests.post(
            f"{OPENAI_BASE_URL}/images/generations",
            json=payload,
            headers=headers,
            timeout=60.0
        )
        
        if response.status_code != 200:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"DALL-E API error: {error_message}")
        
        result = response.json()
        image_url = result["data"][0]["url"]
        revised_prompt = result["data"][0].get("revised_prompt", prompt)
        
        print(f"[Task] Image generated successfully: {image_url[:50]}...")
        
        # Django DB 업데이트 (비동기 함수를 동기로 실행)
        if job_id and user_token:
            import asyncio
            asyncio.run(django_client.update_generation_job(
                job_id=job_id,
                status="completed",
                result_data={
                    "url": image_url,
                    "revised_prompt": revised_prompt,
                    "model": DALLE_MODEL,
                    "size": size,
                    "quality": quality,
                },
                user_token=user_token
            ))
        
        return {
            "success": True,
            "url": image_url,
            "revised_prompt": revised_prompt,
            "model": DALLE_MODEL,
        }
        
    except Exception as e:
        print(f"[Task] Image generation failed: {e}")
        
        # Django DB 업데이트 (실패)
        if job_id and user_token:
            import asyncio
            asyncio.run(django_client.update_generation_job(
                job_id=job_id,
                status="failed",
                error_message=str(e),
                user_token=user_token
            ))
        
        return {
            "success": False,
            "error": str(e)
        }

