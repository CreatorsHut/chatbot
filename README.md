# AI 교육 캐릭터 채팅 플랫폼

> 학생들을 위한 AI 기반 개인 튜터 시스템

## 📋 프로젝트 개요

AI 교육 캐릭터 채팅 플랫폼은 학생들이 다양한 AI 캐릭터 튜터와 1:1로 대화하며 맞춤형 학습을 받을 수 있는 웹 애플리케이션입니다. School Mode를 통해 안전한 학습 환경을 보장합니다.

### 주요 기능

- 🤖 **AI 캐릭터 튜터**: 과목별 전문 튜터 캐릭터와 실시간 대화
- 🎓 **맞춤 학습**: 학생의 수준과 속도에 맞춘 개인화 학습
- ⚡ **실시간 스트리밍**: SSE/WebSocket을 통한 즉시 응답
- 🎨 **AI 이미지 생성**: DALL-E를 활용한 캐릭터 아바타 자동 생성
- 📊 **학습 관리**: 포인트, 캐릭터, 이미지 생성 기록 관리
- 🔒 **안전 환경**: School Mode 정책으로 학생 친화적 응답 보장

## 🏗️ 기술 스택

### Frontend
- **Framework**: Next.js 16 (App Router)
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **상태관리**: React Hooks (useState, useContext)
- **API 통신**: Fetch API, REST

### Backend
- **Django**: REST API 서버 (Python)
  - 사용자 인증 (JWT)
  - 캐릭터 관리
  - 대화 이력 저장
  - 생성 작업 관리

- **FastAPI**: AI 처리 서버 (Python)
  - 실시간 채팅 스트리밍 (SSE)
  - 이미지 생성 (DALL-E 3)
  - AI 응답 생성

### 데이터베이스
- **SQLite**: 개발용
- **PostgreSQL**: 프로덕션 (권장)

## 📁 프로젝트 구조

```
project11_4/
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/             # 페이지 및 레이아웃
│   │   │   ├── page.tsx     # 홈페이지
│   │   │   ├── profile/     # 프로필 페이지
│   │   │   ├── characters/  # 캐릭터 관련 페이지
│   │   │   ├── chat/        # 채팅 페이지
│   │   │   └── ...
│   │   ├── components/      # React 컴포넌트
│   │   └── lib/
│   │       └── api.ts       # API 클라이언트
│   └── package.json
│
├── backend/                  # Python 백엔드
│   ├── django/              # Django REST API
│   │   ├── characters/      # 캐릭터 앱
│   │   ├── conversations/   # 대화 앱
│   │   ├── users/           # 사용자 인증
│   │   ├── media/           # 이미지/생성 작업 관리
│   │   ├── config/          # Django 설정
│   │   └── manage.py
│   │
│   └── fastapi/             # FastAPI AI 서버
│       ├── app/
│       │   ├── main.py      # 메인 앱
│       │   └── django_client.py  # Django 통신
│       └── requirements.txt
│
├── .gitignore               # Git 제외 파일
├── README.md                # 이 파일
└── docs/                    # 문서 (선택사항)
```

## 🚀 빠른 시작

### 필수 요구사항
- Node.js 18+
- Python 3.10+
- Git

### 1. 저장소 클론
```bash
git clone https://github.com/CreatorsHut/chatbot.git
cd chatbot
```

### 2. 프론트엔드 설정
```bash
cd frontend
npm install
```

### 3. 백엔드 설정

#### Django 서버
```bash
cd backend/django
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### FastAPI 서버 (다른 터미널)
```bash
cd backend/fastapi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### 4. 프론트엔드 실행 (다른 터미널)
```bash
cd frontend
npm run dev
```

## 📖 환경 변수 설정

### Frontend (.env.local)
```
NEXT_PUBLIC_DJANGO_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8080
```

### Backend Django (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
OPENAI_API_KEY=your-openai-key
```

### Backend FastAPI (.env)
```
DJANGO_API_URL=http://localhost:8000
OPENAI_API_KEY=your-openai-key
```

## 🎯 주요 페이지

| 페이지 | 설명 | URL |
|--------|------|-----|
| 홈 | 추천 캐릭터 및 소개 | `/` |
| 캐릭터 목록 | 전체 캐릭터 조회 | `/characters` |
| 캐릭터 생성 | 새 캐릭터 생성 | `/characters/create` |
| 채팅 | AI 캐릭터와 대화 | `/chat` |
| 프로필 | 사용자 정보 및 통계 | `/profile` |
| 로그인 | 사용자 인증 | `/login` |
| 회원가입 | 새 계정 생성 | `/signup` |

## 🔐 API 엔드포인트 (주요)

### 인증
- `POST /api/v1/auth/register/` - 회원가입
- `POST /api/v1/auth/login/` - 로그인
- `POST /api/v1/auth/logout/` - 로그아웃

### 캐릭터
- `GET /api/v1/characters/` - 캐릭터 목록
- `GET /api/v1/characters/{id}/` - 캐릭터 상세정보
- `POST /api/v1/characters/` - 캐릭터 생성
- `GET /api/v1/characters/public_characters/` - 공개 캐릭터

### 대화
- `GET /api/v1/conversations/my_conversations/` - 내 대화 목록
- `POST /api/v1/conversations/` - 대화 시작
- `GET /api/v1/conversations/{id}/messages/` - 대화 메시지

### FastAPI AI
- `POST /chat/stream` - 실시간 채팅 스트리밍
- `POST /image/generate` - 이미지 생성

## 📦 배포

### Vercel (Frontend)
```bash
cd frontend
vercel deploy
```

### Heroku (Backend)
```bash
cd backend/django
heroku create your-app-name
git push heroku main
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 👥 팀

- **CreatorsHut** - 개발팀

## 📞 연락처

- GitHub Issues: [Report a bug](https://github.com/CreatorsHut/chatbot/issues)
- Email: contact@creatorshut.com

## 🙏 감사의 말

- OpenAI (DALL-E, GPT)
- Django & FastAPI 커뮤니티
- Next.js 팀

---

**마지막 업데이트**: 2025년 11월
