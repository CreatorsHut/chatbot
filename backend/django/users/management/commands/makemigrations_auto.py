"""
자동 마이그레이션 생성 커맨드

사용법:
    python manage.py makemigrations_auto

모든 앱의 변경사항을 감지하고 자동으로 마이그레이션 파일을 생성합니다.
"""

import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = '모든 앱의 마이그레이션 자동 생성 및 적용'

    def print_status(self, message, status='info'):
        """상태 메시지 출력"""
        symbols = {
            'info': '[INFO]',
            'success': '[OK]',
            'warning': '[WARN]',
            'error': '[ERROR]'
        }

        print(f"{symbols.get(status, '[*]')} {message}")

    def check_database_connection(self):
        """데이터베이스 연결 확인"""
        try:
            connection.ensure_connection()
            self.print_status("Database connection successful!", 'success')
            return True
        except OperationalError as e:
            self.print_status(f"Database connection failed: {e}", 'error')
            return False

    def make_migrations(self):
        """모든 앱의 마이그레이션 파일 생성"""
        try:
            self.print_status("Checking for model changes...", 'info')

            # makemigrations 실행 (대화형 입력 없이)
            call_command('makemigrations', interactive=False, verbosity=1)

            self.print_status("Migration files created/updated!", 'success')
            return True
        except Exception as e:
            self.print_status(f"Makemigrations error: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False

    def migrate(self):
        """마이그레이션 적용"""
        try:
            self.print_status("Applying migrations...", 'info')

            # migrate 실행
            call_command('migrate', interactive=False, verbosity=1)

            self.print_status("Migrations applied successfully!", 'success')
            return True
        except Exception as e:
            self.print_status(f"Migration error: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False

    def handle(self, *args, **options):
        print("\n" + "="*60)
        print("[Django Auto Migrations]")
        print("="*60 + "\n")

        # 1. 데이터베이스 연결 확인
        if not self.check_database_connection():
            self.print_status("Cannot proceed without database connection", 'error')
            return

        # 2. 마이그레이션 파일 생성
        print("")
        self.print_status("Creating migrations...", 'info')
        if not self.make_migrations():
            self.print_status("Makemigrations failed - Stopping", 'error')
            return

        # 3. 마이그레이션 적용
        print("")
        self.print_status("Applying migrations...", 'info')
        if not self.migrate():
            self.print_status("Migration failed", 'error')
            return

        print("\n" + "="*60)
        self.print_status("All done!", 'success')
        print("="*60 + "\n")
