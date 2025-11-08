/**
 * API 클라이언트
 * Django REST API 및 FastAPI와 통신
 */

// 프로덕션 환경 감지 (Vercel에서 자동 제공)
const isProduction = process.env.NODE_ENV === 'production' || process.env.VERCEL === '1';

// Railway 백엔드 URL (프로덕션)
const PRODUCTION_DJANGO_URL = 'https://chatbot-production-848e.up.railway.app/api/v1';
const PRODUCTION_FASTAPI_URL = 'https://fastapi-production-xxxx.up.railway.app'; // FastAPI 배포 후 교체 필요

// API URL 설정 (프로덕션 우선)
const DJANGO_API_URL = process.env.NEXT_PUBLIC_DJANGO_API_URL || 
  (isProduction ? PRODUCTION_DJANGO_URL : 'http://localhost:8000/api/v1');
const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 
  (isProduction ? PRODUCTION_FASTAPI_URL : 'http://localhost:8080');

// 디버깅용 (브라우저 콘솔에 출력)
if (typeof window !== 'undefined') {
  console.log('[API Config]', {
    environment: isProduction ? 'production' : 'development',
    DJANGO_API_URL,
    FASTAPI_URL,
    VERCEL: process.env.VERCEL,
    NODE_ENV: process.env.NODE_ENV
  });
}

// ==================== Types ====================

export interface Character {
  id: number;
  name: string;
  short_description: string;
  category: string;
  category_display: string;
  subject: string;
  subject_display: string;
  avatar_url: string | null;
  owner_name: string;
  status: string;
  visibility: string;
  tags: string[];
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface CharacterDetail extends Character {
  personality_traits: Record<string, any>;
  background_story: string;
  world_setting: string;
  teaching_style: string;
  example_conversations: Array<{ user: string; char: string }>;
  greeting_message: string;
  narration_style: string;
  narration_style_display: string;
  narration_template: string;
  system_prompt: string;
  creativity: number;
  context_length: number;
  moderation_level: string;
  moderation_level_display: string;
}

export interface Conversation {
  id: number;
  character: number;
  character_name: string;
  user_name: string;
  title: string | null;
  subject: string | null;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  conversation: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  token_usage: number;
  created_at: string;
}

// ==================== Auth API ====================

export interface LoginResponse {
  message: string;
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role: string;
  };
}

export interface RegisterResponse {
  message: string;
  access: string;
  refresh: string;
  user: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    role: string;
  };
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || errorData.error || '로그인에 실패했습니다.');
    }

    return await response.json();
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function register(
  email: string,
  username: string,
  first_name: string,
  password: string,
  password_confirm: string
): Promise<RegisterResponse> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        username,
        first_name,
        password,
        password_confirm,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || errorData.error || '회원가입에 실패했습니다.');
    }

    return await response.json();
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
}

export async function logout(refreshToken: string): Promise<void> {
  try {
    const token = localStorage.getItem('token');
    await fetch(`${DJANGO_API_URL}/auth/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });
  } catch (error) {
    console.error('Logout error:', error);
  }
}

// ==================== Character API ====================

export async function fetchCharacters(token?: string): Promise<Character[]> {
  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${DJANGO_API_URL}/characters/`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      // If 401, try public characters endpoint
      if (response.status === 401) {
        const publicData = await fetchPublicCharacters();
        // Flatten the Record<string, Character[]> to Character[]
        return Object.values(publicData).flat();
      }
      throw new Error(`Failed to fetch characters: ${response.status}`);
    }

    const data = await response.json();
    // Django REST Framework pagination: { count, next, previous, results }
    return data.results || data;
  } catch (error) {
    console.error('Error fetching characters:', error);
    throw error;
  }
}

export async function fetchCharacter(id: number): Promise<CharacterDetail> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/characters/${id}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch character: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching character:', error);
    throw error;
  }
}

export async function fetchPublicCharacters(): Promise<Record<string, Character[]>> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/characters/public_characters/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch public characters: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching public characters:', error);
    throw error;
  }
}

// ==================== Conversation API ====================

export async function fetchConversations(token: string): Promise<Conversation[]> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/conversations/my_conversations/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch conversations: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
}

export async function createConversation(
  token: string,
  characterId: number,
  title?: string,
  subject?: string
): Promise<Conversation> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/conversations/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        character: characterId,
        title,
        subject,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to create conversation: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
}

export async function fetchConversationMessages(
  token: string,
  conversationId: number
): Promise<Message[]> {
  try {
    const response = await fetch(
      `${DJANGO_API_URL}/conversations/${conversationId}/messages/`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch messages: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching messages:', error);
    throw error;
  }
}

// ==================== FastAPI Chat & Image ====================

export async function streamChat(
  conversationId: number,
  characterId: number,
  userMessage: string,
  messages: Array<{ role: string; content: string }>,
  userToken: string = '',
  temperature?: number,
  maxTokens?: number
): Promise<ReadableStream<Uint8Array>> {
  const response = await fetch(`${FASTAPI_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      character_id: characterId,
      user_message: userMessage,
      user_token: userToken,
      messages,
      temperature: temperature || 0.7,
      max_tokens: maxTokens || 2000,
      save_to_db: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to stream chat: ${response.status}`);
  }

  return response.body!;
}

export interface ImageGenerationResult {
  url: string;
  revised_prompt: string;
  model: string;
}

export async function generateImage(
  prompt: string,
  size: string = '1024x1024',
  quality: string = 'standard',
  userToken: string = ''
): Promise<ImageGenerationResult> {
  try {
    const response = await fetch(`${FASTAPI_URL}/image/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        size,
        quality,
        user_token: userToken,
        save_to_db: true,  // Django에 저장
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to generate image: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating image:', error);
    throw error;
  }
}

// ==================== Message API ====================

export async function addMessage(
  token: string,
  conversationId: number,
  role: 'user' | 'assistant',
  content: string
): Promise<Message> {
  try {
    const response = await fetch(`${DJANGO_API_URL}/conversations/${conversationId}/add_message/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        role,
        content,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to add message: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error adding message:', error);
    throw error;
  }
}
