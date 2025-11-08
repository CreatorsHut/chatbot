"""
Celery 애플리케이션 설정

Redis를 Broker로 사용하여 비동기 작업 처리
"""

import os
from celery import Celery

# Redis URL
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery 애플리케이션 생성
celery_app = Celery(
    "fastapi_app",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Celery 설정
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # 작업 결과 유지 시간 (24시간)
    result_expires=86400,
    # 작업 타임아웃 (15분)
    task_soft_time_limit=900,
    task_time_limit=1200,
)

print(f"[Celery] Broker: {REDIS_URL[:50]}...")
print(f"[Celery] Backend: {REDIS_URL[:50]}...")

# 작업 자동 로드
celery_app.autodiscover_tasks(['app'])
