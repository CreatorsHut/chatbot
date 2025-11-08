"""
Redis 클라이언트 및 작업 큐 설정

RQ (Redis Queue)를 사용한 비동기 작업 처리:
- 이미지 생성 작업
- 긴 시간이 걸리는 AI 작업
"""

import os
from typing import Optional
import redis
from rq import Queue

# Redis 연결 설정
REDIS_URL = os.getenv("REDIS_URL", "")

# Redis 클라이언트 초기화
redis_client: Optional[redis.Redis] = None
image_queue: Optional[Queue] = None

if REDIS_URL:
    try:
        redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        
        # 연결 테스트
        redis_client.ping()
        
        # 이미지 생성 전용 큐
        image_queue = Queue('image_generation', connection=redis_client)
        
        print(f"[Redis] Connected to Redis: {REDIS_URL[:30]}...")
        print(f"[Redis] Image queue initialized")
    except Exception as e:
        print(f"[Redis] Connection failed: {e}")
        print(f"[Redis] Running without Redis - synchronous mode")
        redis_client = None
        image_queue = None
else:
    print("[Redis] REDIS_URL not configured - running in synchronous mode")


def get_redis() -> Optional[redis.Redis]:
    """Redis 클라이언트 반환"""
    return redis_client


def get_image_queue() -> Optional[Queue]:
    """이미지 생성 큐 반환"""
    return image_queue


def is_redis_available() -> bool:
    """Redis 사용 가능 여부 확인"""
    return redis_client is not None

