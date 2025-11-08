"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

# Django 설정 로드
django.setup()

# 애플리케이션 초기화
application = get_wsgi_application()

# 배포 환경에서 자동으로 마이그레이션 실행 (한 번만)
if os.environ.get("ENVIRONMENT", "").lower() == "production":
    try:
        print("\n[WSGI] Running database migrations...")
        call_command("migrate", "--noinput", verbosity=0)
        print("[WSGI] Migrations completed!")
    except Exception as e:
        print(f"[WSGI] Migration warning: {e}")
