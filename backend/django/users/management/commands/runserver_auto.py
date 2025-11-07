"""
자동 데이터베이스 설정 및 서버 실행 커맨드

사용법:
    python manage.py runserver_auto
    python manage.py runserver_auto 8000
    python manage.py runserver_auto 0.0.0.0:8000
"""

import os
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command, execute_from_command_line
from django.db import connection
from django.db.utils import OperationalError
import psycopg


class Command(BaseCommand):
    help = '데이터베이스 자동 설정 후 서버 실행'

    def add_arguments(self, parser):
        parser.add_argument(
            'addrport',
            nargs='?',
            default='8000',
            help='서버 주소:포트 (기본: 8000)'
        )

    def print_status(self, message, status='info'):
        """상태 메시지 출력"""
        symbols = {
            'info': '[INFO]',
            'success': '[OK]',
            'warning': '[WARN]',
            'error': '[ERROR]'
        }
        
        print(f"{symbols.get(status, '[*]')} {message}")

    def check_postgres_settings(self):
        """Check PostgreSQL settings"""
        from django.conf import settings
        db_settings = settings.DATABASES['default']
        
        # SQLite 사용 중이면 바로 리턴
        if 'sqlite' in db_settings['ENGINE']:
            self.print_status("Using SQLite - Skip PostgreSQL setup", 'info')
            return False
        
        return {
            'ENGINE': db_settings.get('ENGINE'),
            'NAME': db_settings.get('NAME'),
            'USER': db_settings.get('USER'),
            'PASSWORD': db_settings.get('PASSWORD'),
            'HOST': db_settings.get('HOST', 'localhost'),
            'PORT': db_settings.get('PORT', '5432'),
        }

    def create_database_if_not_exists(self, db_config):
        """Create database if not exists (psycopg3)"""
        try:
            # Connect to postgres database to check/create target DB
            password = str(db_config['PASSWORD'])
            
            # psycopg3는 autocommit을 connect 시 설정
            conn = psycopg.connect(
                dbname='postgres',
                user=db_config['USER'],
                password=password,
                host=db_config['HOST'],
                port=db_config['PORT'],
                autocommit=True
            )
            cursor = conn.cursor()
            
            # 데이터베이스 존재 확인
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (db_config['NAME'],)
            )
            
            if not cursor.fetchone():
                self.print_status(f"Creating database '{db_config['NAME']}'...", 'info')
                cursor.execute(f"CREATE DATABASE {db_config['NAME']}")
                self.print_status(f"Database '{db_config['NAME']}' created!", 'success')
                
                # Grant privileges
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON DATABASE {db_config['NAME']} TO {db_config['USER']}"
                )
                self.print_status("Privileges granted", 'success')
            else:
                self.print_status(f"Database '{db_config['NAME']}' exists", 'success')
            
            cursor.close()
            conn.close()
            return True
            
        except psycopg.Error as e:
            self.print_status(f"PostgreSQL connection error: {e}", 'error')
            self.print_status("Please check:", 'warning')
            self.print_status("1. PostgreSQL service is running", 'info')
            self.print_status("2. Database settings in .env file", 'info')
            self.print_status("3. PostgreSQL password is correct", 'info')
            return False

    def run_migrations(self):
        """Run migrations"""
        try:
            self.print_status("Checking migrations...", 'info')
            
            # makemigrations
            call_command('makemigrations', interactive=False)
            
            # migrate
            call_command('migrate', interactive=False)
            
            self.print_status("Migrations completed!", 'success')
            return True
        except Exception as e:
            self.print_status(f"Migration error: {e}", 'error')
            return False

    def check_database_connection(self):
        """Check database connection"""
        try:
            connection.ensure_connection()
            self.print_status("Database connection successful!", 'success')
            return True
        except OperationalError as e:
            self.print_status(f"Database connection failed: {e}", 'error')
            return False

    def create_superuser_if_not_exists(self):
        """Create superuser if not exists"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if superuser already exists
            if User.objects.filter(is_superuser=True).exists():
                self.print_status("Admin account already exists", 'success')
                return True
            
            # Get superuser info from .env
            username = os.getenv('DJANGO_SUPERUSER_USERNAME', '')
            email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')
            
            if not all([username, email, password]):
                self.print_status("No superuser info in .env - Skip", 'warning')
                self.print_status("Create later with 'python manage.py createsuperuser'", 'info')
                return True
            
            # Create superuser
            self.print_status(f"Creating admin account '{username}'...", 'info')
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.print_status(f"Admin account '{username}' created!", 'success')
            self.print_status(f"Login: /admin (ID: {username})", 'info')
            return True
            
        except Exception as e:
            self.print_status(f"Superuser creation error: {e}", 'error')
            return False

    def handle(self, *args, **options):
        addrport = options['addrport']
        
        print("\n" + "="*60)
        print("[Django Auto Server Start]")
        print("="*60 + "\n")
        
        # 1. PostgreSQL 설정 확인
        db_config = self.check_postgres_settings()
        
        if db_config:
            # 2. Create database if not exists
            if not self.create_database_if_not_exists(db_config):
                self.print_status("Database setup failed - Stopping server", 'error')
                return
            
            # 3. Check database connection
            if not self.check_database_connection():
                return
        
        # 4. Run migrations
        self.print_status("\nRunning migrations...", 'info')
        if not self.run_migrations():
            self.print_status("Migration failed - Continue anyway", 'warning')
        
        # 5. 슈퍼유저 자동 생성
        print("")
        self.print_status("Checking admin account...", 'info')
        self.create_superuser_if_not_exists()
        
        # 6. 서버 시작
        print("\n" + "="*60)
        self.print_status("Starting Django server...", 'success')
        print("="*60 + "\n")
        
        # runserver 실행
        sys.argv = ['manage.py', 'runserver', addrport]
        execute_from_command_line(sys.argv)

