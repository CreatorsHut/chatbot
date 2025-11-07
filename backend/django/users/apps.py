from django.apps import AppConfig
import os


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "사용자 관리"
    
    def ready(self):
        """서버 시작 시 자동 실행"""
        # AUTO_MIGRATE 환경변수가 false면 스킵
        if os.getenv('AUTO_MIGRATE', 'true').lower() == 'false':
            return
        
        # 중복 실행 방지
        if hasattr(self, '_auto_setup_done'):
            return
        self._auto_setup_done = True
            
        self.run_auto_setup()
    
    def run_auto_setup(self):
        """자동 설정 실행"""
        try:
            from django.core.management import call_command
            from django.db import connection
            from django.contrib.auth import get_user_model
            import sys
            
            print("\n" + "="*60)
            print("[Auto Setup] Starting database setup...")
            print("="*60)
            
            # 1. 데이터베이스 연결 확인
            try:
                connection.ensure_connection()
                print("[Auto Setup] Database connection OK")
            except Exception as e:
                print(f"[Auto Setup] Database connection failed: {e}")
                # PostgreSQL 데이터베이스 자동 생성 시도
                if 'postgresql' in str(connection.settings_dict.get('ENGINE', '')):
                    self.create_postgres_database()
            
            # 2. 마이그레이션 실행
            try:
                print("[Auto Setup] Running migrations...")
                call_command('migrate', '--no-input', verbosity=0)
                print("[Auto Setup] Migrations completed")
            except Exception as e:
                print(f"[Auto Setup] Migration failed: {e}")
            
            # 3. 슈퍼유저 자동 생성
            try:
                User = get_user_model()
                if not User.objects.filter(is_superuser=True).exists():
                    username = os.getenv('DJANGO_SUPERUSER_USERNAME', '')
                    email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
                    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')
                    
                    if all([username, email, password]):
                        User.objects.create_superuser(
                            username=username,
                            email=email,
                            password=password
                        )
                        print(f"[Auto Setup] Admin account '{username}' created")
                    else:
                        print("[Auto Setup] No admin credentials in .env - Skip")
                else:
                    print("[Auto Setup] Admin account already exists")
            except Exception as e:
                print(f"[Auto Setup] Admin creation failed: {e}")
            
            print("="*60)
            print("[Auto Setup] Setup completed!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"[Auto Setup] Error: {e}")
    
    def create_postgres_database(self):
        """PostgreSQL 데이터베이스 자동 생성 (psycopg3)"""
        try:
            import psycopg
            from django.conf import settings
            
            db = settings.DATABASES['default']
            
            print(f"[Auto Setup] Creating PostgreSQL database '{db['NAME']}'...")
            
            # psycopg3는 autocommit을 connect 시 설정
            conn = psycopg.connect(
                dbname='postgres',
                user=db['USER'],
                password=str(db['PASSWORD']),
                host=db['HOST'],
                port=db['PORT'],
                autocommit=True
            )
            cursor = conn.cursor()
            
            # 데이터베이스 존재 확인
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db['NAME'],))
            
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {db['NAME']}")
                print(f"[Auto Setup] Database '{db['NAME']}' created!")
            else:
                print(f"[Auto Setup] Database '{db['NAME']}' already exists")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"[Auto Setup] Could not create database: {e}")
