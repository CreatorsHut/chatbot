from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
import uvicorn
import httpx
import json
from typing import AsyncGenerator, Optional
from .django_client import django_client

# Load environment variables
load_dotenv()

app = FastAPI(
    title="EduChat FastAPI",
    description="OpenAI streaming & image generation service for EduChat",
    version="1.0.0"
)

# CORS (configure from env, default to *)
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allow_origins.split(",") if o.strip()] if allow_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DJANGO_BASE_URL = os.getenv("DJANGO_BASE_URL", "http://localhost:8000")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
DALLE_MODEL = os.getenv("DALLE_MODEL", "dall-e-3")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다! .env 파일을 확인하세요.")


@app.get("/")
def root():
    return {
        "service": "fastapi",
        "status": "ok",
        "endpoints": [
            "/health",
            "/readiness",
            "/chat/stream",
            "/image/generate"
        ]
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/readiness")
def readiness():
    # Placeholder: add DB/Redis ping checks if needed
    return {"ready": True}


# ==================== Chat Streaming (OpenAI) ====================

import random
import re

# 이모지 풀 - 상황별로 분류
EMOJI_POOLS = {
    "happy": ["😊", "😃", "😄", "😁", "🙂", "😌", "🤗", "🥰", "✨", "💫", "🌟"],
    "thinking": ["🤔", "🧐", "💭", "🤨", "😯", "😮"],
    "excited": ["🤩", "😍", "🎉", "🎊", "⭐", "💫", "✨", "🌟"],
    "love": ["😍", "🥰", "😘", "💕", "💖", "💗", "💝"],
    "surprised": ["😮", "😯", "😲", "🤯", "😳"],
    "sad": ["😔", "😕", "🙁", "☹️", "😢", "😥"],
    "neutral": ["😐", "😑", "😶", "🙂"],
    "playful": ["😏", "😜", "😝", "😛", "🤪", "😋"],
}

# 반복되는 이모지 추적 (최근 5개)
recent_emojis = []

def diversify_emoji(text: str) -> str:
    """
    반복되는 이모지를 다양한 이모지로 교체
    """
    global recent_emojis
    
    # 이모지 패턴 찾기 (유니코드 이모지)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 표정
        "\U0001F300-\U0001F5FF"  # 기호 & 픽토그램
        "\U0001F680-\U0001F6FF"  # 교통 & 지도
        "\U0001F1E0-\U0001F1FF"  # 국기
        "\U00002600-\U000027BF"  # 기타 기호
        "\U0001F900-\U0001F9FF"  # 추가 이모지
        "\U0001FA70-\U0001FAFF"  # 확장 이모지
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    
    def replace_emoji(match):
        global recent_emojis
        emoji = match.group(0)
        
        # 이미 최근에 사용된 이모지면 교체
        if emoji in recent_emojis[-5:]:
            # 주변 텍스트로 감정 판단
            context = text[max(0, match.start()-20):match.end()+20].lower()
            
            # 컨텍스트 기반 풀 선택
            if any(word in context for word in ["생각", "고민", "음", "어떻"]):
                pool = EMOJI_POOLS["thinking"]
            elif any(word in context for word in ["기쁘", "좋", "환", "신나", "짱", "최고"]):
                pool = EMOJI_POOLS["happy"]
            elif any(word in context for word in ["와", "대단", "멋지", "놀라", "정말"]):
                pool = EMOJI_POOLS["excited"]
            elif any(word in context for word in ["사랑", "좋아", "귀여", "예쁘"]):
                pool = EMOJI_POOLS["love"]
            elif any(word in context for word in ["슬프", "아쉽", "안타", "걱정"]):
                pool = EMOJI_POOLS["sad"]
            elif any(word in context for word in ["재미", "장난", "웃", "하하"]):
                pool = EMOJI_POOLS["playful"]
            else:
                # 기본적으로 happy 풀 사용
                pool = EMOJI_POOLS["happy"]
            
            # 최근 사용하지 않은 이모지 선택
            available = [e for e in pool if e not in recent_emojis[-5:]]
            if not available:
                available = pool
            
            new_emoji = random.choice(available)
            recent_emojis.append(new_emoji)
            if len(recent_emojis) > 10:
                recent_emojis.pop(0)
            
            return new_emoji
        else:
            # 새로운 이모지는 그대로 유지
            recent_emojis.append(emoji)
            if len(recent_emojis) > 10:
                recent_emojis.pop(0)
            return emoji
    
    return emoji_pattern.sub(replace_emoji, text)


async def stream_chat_response(
    messages: list,
    system_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> AsyncGenerator[str, None]:
    """
    Stream chat response from OpenAI API
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{OPENAI_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_message = error_text.decode('utf-8') if error_text else 'Unknown error'
                    yield f"data: {json.dumps({'error': f'OpenAI API error: {response.status_code} - {error_message}'})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str == "[DONE]":
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break

                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    # 이모지 다양화 적용
                                    content = diversify_emoji(delta['content'])
                                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                        except json.JSONDecodeError:
                            continue

    except httpx.RequestError as e:
        yield f"data: {json.dumps({'error': f'Request error: {str(e)}'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"


from pydantic import BaseModel, Field


class ChatStreamRequest(BaseModel):
    """Chat streaming request"""
    conversation_id: int = Field(..., description="Conversation ID from Django")
    character_id: int = Field(..., description="Character ID from Django")
    user_message: str = Field(..., description="User's message")
    user_token: str = Field(default="", description="User's JWT token for Django API")
    messages: list = Field(default=[], description="Previous message history [{'role': 'user|assistant', 'content': '...'}]")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=4000)
    save_to_db: bool = Field(default=True, description="Save messages to Django DB")


class ImageGenerationRequest(BaseModel):
    """Image generation request"""
    user_token: str = Field(default="", description="User JWT token from frontend")
    prompt: str = Field(..., description="Image prompt")
    size: str = Field(default="1024x1024", description="Image size (1024x1024, 1024x1792, 1792x1024)")
    quality: str = Field(default="standard", description="Quality (standard or hd)")
    save_to_db: bool = Field(default=True, description="Save to Django DB")


@app.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):
    """
    Stream chat response from OpenAI

    1. Fetch character system prompt from Django API
    2. Save user message to Django DB
    3. Stream response from OpenAI
    4. Save assistant response to Django DB
    5. Return SSE stream
    """
    try:
        # 1. Fetch character system prompt from Django
        character_data = await django_client.get_character(request.character_id)
        if not character_data:
            raise HTTPException(
                status_code=404,
                detail=f"Character not found: {request.character_id}"
            )
        
        system_prompt = character_data.get("system_prompt", "You are a helpful assistant.")
        temperature = character_data.get("creativity", request.temperature)
        
        # 2. Save user message to DB (optional)
        if request.save_to_db:
            await django_client.save_message(
                conversation_id=request.conversation_id,
                role="user",
                content=request.user_message,
                user_token=request.user_token,
                model_version=OPENAI_MODEL,
            )
        
        # 3. Prepare messages for OpenAI
        all_messages = request.messages + [{"role": "user", "content": request.user_message}]
        
        # 4. Stream response and collect for saving
        collected_response = []
        
        async def stream_and_collect():
            """Stream from OpenAI and collect response"""
            async for chunk in stream_chat_response(
                messages=all_messages,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=request.max_tokens,
            ):
                # Parse SSE chunk
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:])
                        if data.get("content"):
                            collected_response.append(data["content"])
                    except:
                        pass
                
                yield chunk
            
            # 5. Save assistant response to DB after streaming completes
            if request.save_to_db and collected_response:
                full_response = "".join(collected_response)
                await django_client.save_message(
                    conversation_id=request.conversation_id,
                    role="assistant",
                    content=full_response,
                    user_token=request.user_token,
                    token_usage=len(full_response.split()),  # 간단한 토큰 추정
                    model_version=OPENAI_MODEL,
                )
        
        # Return SSE stream
        return StreamingResponse(
            stream_and_collect(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Image Generation (DALL-E) ====================

@app.post("/image/generate")
async def generate_image(request: ImageGenerationRequest):
    """
    Generate image using DALL-E 3

    1. Create generation job in Django DB
    2. Call DALL-E API
    3. Save result to Django DB
    4. Return image URL

    Returns: {
        "job_id": int,
        "url": "image_url",
        "revised_prompt": "actual_prompt_used"
    }
    """
    job_id = None
    
    try:
        # 1. Create generation job in Django (status: pending)
        if request.save_to_db and request.user_token:
            job_data = await django_client.create_generation_job(
                user_token=request.user_token,
                job_type="image",
                input_data={
                    "prompt": request.prompt,
                    "size": request.size,
                    "quality": request.quality,
                    "model": DALLE_MODEL,
                }
            )
            if job_data:
                job_id = job_data.get("id")
                
                # 즉시 processing 상태로 변경 (started_at 설정됨)
                await django_client.update_generation_job(
                    job_id=job_id,
                    status="processing",
                    user_token=request.user_token
                )
        elif request.save_to_db:
            print("[FastAPI] Warning: save_to_db=True but no user_token provided")
        
        # 2. Call DALL-E API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": DALLE_MODEL,
            "prompt": request.prompt,
            "n": 1,
            "size": request.size,
            "quality": request.quality,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENAI_BASE_URL}/images/generations",
                json=payload,
                headers=headers,
                timeout=60.0
            )

            if response.status_code != 200:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                # Update job status to failed
                if job_id and request.save_to_db and request.user_token:
                    await django_client.update_generation_job(
                        job_id=job_id,
                        status="failed",
                        error_message=error_message,
                        user_token=request.user_token
                    )
                
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"DALL-E API error: {error_message}"
                )

            result = response.json()
            image_url = result["data"][0]["url"]
            revised_prompt = result["data"][0].get("revised_prompt", request.prompt)
            
            # 3. Update job status to completed
            if job_id and request.save_to_db and request.user_token:
                await django_client.update_generation_job(
                    job_id=job_id,
                    status="completed",
                    result_data={
                        "url": image_url,
                        "revised_prompt": revised_prompt,
                        "model": DALLE_MODEL,
                        "size": request.size,
                        "quality": request.quality,
                    },
                    user_token=request.user_token
                )
            
            # 4. Return result
            return {
                "job_id": job_id,
                "url": image_url,
                "revised_prompt": revised_prompt,
                "model": DALLE_MODEL,
                "success": True
            }

    except HTTPException:
        raise
    except Exception as e:
        # Update job status to failed
        if job_id and request.save_to_db and request.user_token:
            await django_client.update_generation_job(
                job_id=job_id,
                status="failed",
                error_message=str(e),
                user_token=request.user_token
            )
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import socket
    
    host = os.getenv("FASTAPI_HOST", "127.0.0.1")
    port_str = os.getenv("FASTAPI_PORT", "8080")
    port = int(port_str) if port_str.isdigit() else 8080
    
    # 포트 사용 가능 여부 확인 및 자동 대체
    def find_available_port(start_port, max_attempts=10):
        for attempt in range(max_attempts):
            test_port = start_port + attempt
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, test_port))
                    return test_port
            except OSError:
                continue
        raise RuntimeError(f"Could not find available port in range {start_port}-{start_port+max_attempts-1}")
    
    try:
        available_port = find_available_port(port)
        if available_port != port:
            print(f"⚠️  Port {port} is in use. Using port {available_port} instead.")
        print(f"🚀 Starting FastAPI on http://{host}:{available_port}")
        uvicorn.run("app.main:app", host=host, port=available_port, reload=True)
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        print("💡 Try specifying a different port: FASTAPI_PORT=8001 python -m app.main")