"""
FastAPI 웹 서버와 Celery 워커를 동시에 실행하는 스크립트
"""

import os
import sys
import subprocess
import signal
import time
from typing import Optional

# 포트 설정
PORT = os.getenv('PORT', '8000')
LOG_PREFIX = "[StartupManager]"

# 프로세스 저장
web_process: Optional[subprocess.Popen] = None
worker_process: Optional[subprocess.Popen] = None


def signal_handler(signum, frame):
    """신호 수신 시 프로세스 종료"""
    global web_process, worker_process

    print(f"\n{LOG_PREFIX} 신호 수신: {signum}, 프로세스 종료 중...")

    if web_process:
        print(f"{LOG_PREFIX} 웹 서버 종료 (PID: {web_process.pid})...")
        web_process.terminate()
        try:
            web_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            web_process.kill()

    if worker_process:
        print(f"{LOG_PREFIX} 워커 종료 (PID: {worker_process.pid})...")
        worker_process.terminate()
        try:
            worker_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_process.kill()

    print(f"{LOG_PREFIX} 모든 프로세스 종료됨")
    sys.exit(0)


def run_web_server():
    """FastAPI 웹 서버 실행"""
    global web_process

    print(f"\n{LOG_PREFIX} FastAPI 웹 서버 시작...")
    print(f"{LOG_PREFIX} 포트: {PORT}")

    cmd = [
        sys.executable,
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', PORT
    ]

    web_process = subprocess.Popen(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )

    print(f"{LOG_PREFIX} 웹 서버 시작됨 (PID: {web_process.pid})")
    return web_process


def run_celery_worker():
    """Celery 워커 실행"""
    global worker_process

    print(f"\n{LOG_PREFIX} Celery 워커 시작...")

    cmd = [
        sys.executable,
        '-m', 'celery',
        '-A', 'app.celery_app',
        'worker',
        '--loglevel=info',
        '--concurrency=2'
    ]

    worker_process = subprocess.Popen(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )

    print(f"{LOG_PREFIX} 워커 시작됨 (PID: {worker_process.pid})")
    return worker_process


def main():
    """메인 함수"""
    print(f"\n{LOG_PREFIX} ========================================")
    print(f"{LOG_PREFIX} FastAPI 웹 서버 + Celery 워커 시작")
    print(f"{LOG_PREFIX} ========================================\n")

    # 신호 핸들러 등록
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # 웹 서버와 워커 동시 시작
    web_process = run_web_server()
    time.sleep(2)  # 웹 서버가 시작될 때까지 잠시 대기
    worker_process = run_celery_worker()

    try:
        print(f"\n{LOG_PREFIX} 모든 프로세스가 실행 중입니다...")
        print(f"{LOG_PREFIX} 웹 서버 PID: {web_process.pid}")
        print(f"{LOG_PREFIX} 워커 PID: {worker_process.pid}\n")

        # 프로세스들이 계속 실행되도록 유지
        while True:
            # 웹 서버 상태 체크
            if web_process.poll() is not None:
                print(f"\n{LOG_PREFIX} ❌ 웹 서버가 중단됨 (종료 코드: {web_process.returncode})")
                print(f"{LOG_PREFIX} 워커도 중단합니다...")
                if worker_process and worker_process.poll() is None:
                    worker_process.terminate()
                break

            # 워커 상태 체크
            if worker_process.poll() is not None:
                print(f"\n{LOG_PREFIX} ⚠️  워커가 중단됨 (종료 코드: {worker_process.returncode})")
                print(f"{LOG_PREFIX} 워커를 다시 시작합니다...")
                worker_process = run_celery_worker()

            time.sleep(5)  # 5초마다 상태 체크

    except KeyboardInterrupt:
        print(f"\n{LOG_PREFIX} 인터럽트 신호 수신")
        signal_handler(signal.SIGINT, None)


if __name__ == '__main__':
    main()
