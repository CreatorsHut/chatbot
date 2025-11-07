'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

// 카테고리 선택지
const CATEGORIES = [
  { value: 'educator', label: '🎓 교육자 (선생님, 튜터)' },
  { value: 'historical', label: '📜 역사인물' },
  { value: 'fictional', label: '🎭 가상인물 (판타지, 만화, SF)' },
  { value: 'mentor', label: '🤝 멘토 (상담, 진로)' },
  { value: 'friend', label: '👥 친구' },
  { value: 'other', label: '✨ 기타' },
];

// 카테고리별 세부항목 - 정확히 매핑됨
const CATEGORY_DETAILS: Record<string, Array<{ value: string; label: string }>> = {
  // 교육자 -> 학업 관련 과목
  educator: [
    { value: 'korean', label: '국어 선생님' },
    { value: 'math', label: '수학 선생님' },
    { value: 'english', label: '영어 선생님' },
    { value: 'science', label: '과학 선생님' },
    { value: 'history', label: '역사 선생님' },
    { value: 'social_studies', label: '사회 선생님' },
    { value: 'general', label: '일반 튜터' },
  ],

  // 역사인물 -> 역사 관련
  historical: [
    { value: 'history', label: '역사 인물 (동양)' },
    { value: 'social_studies', label: '역사 인물 (서양)' },
    { value: 'science', label: '과학자/발명가' },
    { value: 'korean', label: '문인/예술가' },
    { value: 'general', label: '기타 역사 인물' },
  ],

  // 가상인물 -> 다양한 장르
  fictional: [
    { value: 'general', label: '판타지 캐릭터' },
    { value: 'english', label: '만화/웹툰 캐릭터' },
    { value: 'science', label: 'SF/사이버펑크 캐릭터' },
    { value: 'korean', label: '동화/우화 캐릭터' },
    { value: 'history', label: '게임 캐릭터' },
  ],

  // 멘토 -> 상담, 진로 관련
  mentor: [
    { value: 'general', label: '일반 상담가' },
    { value: 'social_studies', label: '진로/직업 멘토' },
    { value: 'korean', label: '심리 상담가' },
    { value: 'english', label: '취업 코치' },
    { value: 'science', label: '학습 코치' },
  ],

  // 친구 -> 성격/MBTI 별
  friend: [
    { value: 'general', label: '친한 친구 (일반)' },
    { value: 'korean', label: '감정적인 친구 (F형)' },
    { value: 'english', label: '논리적인 친구 (T형)' },
    { value: 'math', label: '밝은 친구 (E형)' },
    { value: 'science', label: '조용한 친구 (I형)' },
    { value: 'history', label: '재미있는 친구 (놀이친구)' },
    { value: 'social_studies', label: '믿을 수 있는 친구' },
  ],

  // 기타 -> 다양한 캐릭터
  other: [
    { value: 'general', label: '동물/펫 캐릭터' },
    { value: 'korean', label: '음식/물체 의인화' },
    { value: 'english', label: '우주인/외계인' },
    { value: 'science', label: 'AI/로봇' },
    { value: 'history', label: '유명인/연예인' },
    { value: 'math', label: '신화 속 존재' },
    { value: 'social_studies', label: '직업 체험용' },
  ],
};

const SUBJECTS = [
  { value: 'korean', label: '국어' },
  { value: 'math', label: '수학' },
  { value: 'english', label: '영어' },
  { value: 'science', label: '과학' },
  { value: 'history', label: '역사' },
  { value: 'social_studies', label: '사회' },
  { value: 'general', label: '일반' },
];

const NARRATION_STYLES = [
  { value: 'none', label: '연출 없음' },
  { value: 'minimal', label: '최소 (*행동* 가끔)' },
  { value: 'novel', label: '소설형 (전체 서술) ⭐ 추천' },
  { value: 'screenplay', label: '시나리오형' },
];

interface FormData {
  name: string;
  short_description: string;
  category: string;
  subject: string;
  avatar_url?: string;
  personality_traits: {
    core_traits: string[];
    speech_style: string;
    catchphrase: string;
    tone: string;
  };
  greeting_message: string;
  background_story: string;
  world_setting: string;
  teaching_style: string;
  example_conversations: Array<{ user: string; char: string }>;
  narration_style: string;
  creativity: number;
  context_length: number;
  moderation_level: string;
  tags: string[];
}

export default function CreateCharacterPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(1); // 1: 기본, 2: 성격, 3: 배경, 4: 연출
  const [imageGenerating, setImageGenerating] = useState(false);
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);

  // 입력 중인 텍스트를 문자열로 관리
  const [traitsInput, setTraitsInput] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  
  const [formData, setFormData] = useState<FormData>({
    name: '',
    short_description: '',
    category: 'educator',
    subject: 'general',
    personality_traits: {
      core_traits: [],
      speech_style: '',
      catchphrase: '',
      tone: '',
    },
    greeting_message: '',
    background_story: '',
    world_setting: '',
    teaching_style: '',
    example_conversations: [{ user: '', char: '' }],
    narration_style: 'novel',
    creativity: 0.7,
    context_length: 50,
    moderation_level: 'high',
    tags: [],
  });

  useEffect(() => {
    const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (!loggedIn) {
      router.push('/login?redirect=/characters/create');
    }
    setIsLoggedIn(loggedIn);
  }, [router]);

  if (!isLoggedIn) {
    return null;
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;

    // 카테고리 변경 시 세부항목 자동 업데이트
    if (name === 'category') {
      const defaultSubject = CATEGORY_DETAILS[value]?.[0]?.value || 'general';
      setFormData(prev => ({
        ...prev,
        [name]: value,
        subject: defaultSubject,
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handlePersonalityChange = (key: string, value: string | string[]) => {
    setFormData(prev => ({
      ...prev,
      personality_traits: {
        ...prev.personality_traits,
        [key]: value,
      },
    }));
  };

  const handleTraitsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 입력값을 그대로 저장 (쉼표 포함)
    setTraitsInput(value);
    
    // 실시간으로 배열도 업데이트 (제출 시 사용)
    const traits = value.trim() ? value.split(',').map(t => t.trim()).filter(t => t) : [];
    handlePersonalityChange('core_traits', traits);
  };

  const handleExampleConversationChange = (index: number, key: 'user' | 'char', value: string) => {
    const newConversations = [...formData.example_conversations];
    newConversations[index][key] = value;
    setFormData(prev => ({
      ...prev,
      example_conversations: newConversations,
    }));
  };

  const addExampleConversation = () => {
    setFormData(prev => ({
      ...prev,
      example_conversations: [...prev.example_conversations, { user: '', char: '' }],
    }));
  };

  const removeExampleConversation = (index: number) => {
    setFormData(prev => ({
      ...prev,
      example_conversations: prev.example_conversations.filter((_, i) => i !== index),
    }));
  };

  const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 입력값을 그대로 저장 (쉼표 포함)
    setTagsInput(value);
    
    // 실시간으로 배열도 업데이트 (제출 시 사용)
    const tags = value.trim() ? value.split(',').map(t => t.trim()).filter(t => t) : [];
    setFormData(prev => ({
      ...prev,
      tags,
    }));
  };

  const generateImage = async () => {
    if (!formData.name.trim()) {
      setError('캐릭터 이름을 입력한 후 이미지를 생성해주세요.');
      return;
    }

    setImageGenerating(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      
      // 캐릭터 정보 기반 프롬프트 + 아바타 최적화
      const prompt = `${formData.name}, ${formData.short_description}, portrait, head and shoulders only, solid color background, no objects, no text, profile picture style`;

      console.log('🎨 이미지 생성 프롬프트:', prompt);

      const response = await fetch(`${process.env.NEXT_PUBLIC_FASTAPI_URL}/image/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_token: token,
          prompt: prompt,
          size: '1024x1024',
          quality: 'standard',
          save_to_db: false,
        }),
      });

      if (!response.ok) {
        throw new Error('이미지 생성에 실패했습니다.');
      }

      const result = await response.json();
      if (result.url) {
        setGeneratedImageUrl(result.url);
        setFormData(prev => ({
          ...prev,
          avatar_url: result.url,
        }));
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '이미지 생성 중 오류가 발생했습니다.');
    } finally {
      setImageGenerating(false);
    }
  };

  const validateStep = (step: number): boolean => {
    setError(null);

    switch (step) {
      case 1:
        if (!formData.name.trim()) {
          setError('📋 캐릭터 이름을 입력해주세요.');
          return false;
        }
        if (!formData.short_description.trim()) {
          setError('📋 한 줄 설명을 입력해주세요.');
          return false;
        }
        return true;

      case 2:
        if (formData.personality_traits.core_traits.length === 0) {
          setError('🎨 성격/특성을 최소 1개 이상 입력해주세요.');
          return false;
        }
        if (!formData.personality_traits.speech_style.trim()) {
          setError('🎨 말투/스타일을 입력해주세요.');
          return false;
        }
        if (!formData.greeting_message.trim()) {
          setError('🎨 첫 대사를 입력해주세요.');
          return false;
        }
        return true;

      case 3:
        if (!formData.background_story.trim()) {
          setError('📖 배경 스토리를 입력해주세요.');
          return false;
        }
        if (!formData.world_setting.trim()) {
          setError('📖 세계관/배경을 입력해주세요.');
          return false;
        }
        // teaching_style은 카테고리가 educator일 때만 필수
        if (formData.category === 'educator' && !formData.teaching_style.trim()) {
          setError('📖 교수법/학습 스타일을 입력해주세요.');
          return false;
        }
        return true;

      case 4:
        // 태그는 최소 1개 이상 필수
        if (formData.tags.length === 0) {
          setError('🎬 태그를 최소 1개 이상 입력해주세요.');
          return false;
        }
        return true;

      default:
        return true;
    }
  };

  const validateForm = () => {
    // 1단계: 기본 정보
    if (!formData.name.trim()) {
      setError('📋 캐릭터 이름을 입력해주세요.');
      setCurrentStep(1);
      return false;
    }
    if (!formData.short_description.trim()) {
      setError('📋 한 줄 설명을 입력해주세요.');
      setCurrentStep(1);
      return false;
    }
    
    // 2단계: 성격 설정
    if (formData.personality_traits.core_traits.length === 0) {
      setError('🎨 성격/특성을 최소 1개 이상 입력해주세요.');
      setCurrentStep(2);
      return false;
    }
    if (!formData.personality_traits.speech_style.trim()) {
      setError('🎨 말투/스타일을 입력해주세요.');
      setCurrentStep(2);
      return false;
    }
    if (!formData.greeting_message.trim()) {
      setError('🎨 첫 대사를 입력해주세요.');
      setCurrentStep(2);
      return false;
    }
    
    // 3단계: 배경 및 세계관
    if (!formData.background_story.trim()) {
      setError('📖 배경 스토리를 입력해주세요.');
      setCurrentStep(3);
      return false;
    }
    if (!formData.world_setting.trim()) {
      setError('📖 세계관/배경을 입력해주세요.');
      setCurrentStep(3);
      return false;
    }
    if (formData.category === 'educator' && !formData.teaching_style.trim()) {
      setError('📖 교수법/학습 스타일을 입력해주세요.');
      setCurrentStep(3);
      return false;
    }
    
    // 4단계: 연출 스타일 및 기타 설정
    if (formData.tags.length === 0) {
      setError('🎬 태그를 최소 1개 이상 입력해주세요.');
      setCurrentStep(4);
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      
      // avatar_url 값 확인 (빈 문자열은 null로 변환)
      console.log('🖼️ generatedImageUrl:', generatedImageUrl, typeof generatedImageUrl);
      console.log('🖼️ formData.avatar_url:', formData.avatar_url, typeof formData.avatar_url);
      
      let avatarUrl = generatedImageUrl || formData.avatar_url || null;
      // 빈 문자열은 null로 변환 (Django URLField는 빈 문자열을 허용하지 않음)
      if (avatarUrl === '') {
        avatarUrl = null;
      }
      console.log('🖼️ 최종 avatar_url:', avatarUrl, typeof avatarUrl);
      
      const requestData = {
        name: formData.name,
        short_description: formData.short_description,
        category: formData.category,
        subject: formData.subject,
        avatar_url: avatarUrl,
        personality_traits: formData.personality_traits,
        greeting_message: formData.greeting_message,
        background_story: formData.background_story,
        world_setting: formData.world_setting,
        teaching_style: formData.teaching_style,
        example_conversations: formData.example_conversations.filter(c => c.user && c.char),
        narration_style: formData.narration_style,
        creativity: formData.creativity,
        context_length: formData.context_length,
        moderation_level: formData.moderation_level,
        tags: formData.tags,
        visibility: 'private',
        auto_generate_prompt: true,
      };
      
      console.log('📤 전송 데이터:', requestData);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_DJANGO_API_URL}/characters/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ 캐릭터 생성 실패:', errorData);
        console.error('❌ 에러 상세:', JSON.stringify(errorData, null, 2));
        
        // Django REST Framework 에러 메시지 파싱
        let errorMessage = '캐릭터 생성에 실패했습니다.';
        if (errorData.avatar_url) {
          errorMessage = `아바타 URL 에러: ${errorData.avatar_url.join(', ')}`;
        } else if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (typeof errorData === 'object') {
          // 필드별 에러 메시지 결합
          const errors = Object.entries(errorData).map(([key, value]) => {
            return `${key}: ${Array.isArray(value) ? value.join(', ') : value}`;
          });
          errorMessage = errors.join('\n');
        }
        
        throw new Error(errorMessage);
      }

      setSuccess(true);
      setTimeout(() => {
        router.push('/characters');
      }, 2000);
    } catch (err) {
      console.error('❌ 캐릭터 생성 에러:', err);
      setError(err instanceof Error ? err.message : '캐릭터 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-[#111827]">
      <Header />

      <main className="mx-auto w-full max-w-screen-lg px-6 py-10">
        <h1 className="text-[36px] font-bold text-[#111827] mb-2">🎭 나만의 AI 캐릭터 만들기</h1>
        <p className="text-[16px] text-[#6b7380] mb-8">초보자도 쉽게 따라할 수 있는 단계별 가이드입니다.</p>

        {/* 진행 상황 표시 */}
        <div className="flex gap-2 mb-8">
          {[1, 2, 3, 4].map(step => (
            <button
              key={step}
              onClick={() => setCurrentStep(step)}
              className={`flex-1 h-2 rounded-full transition ${
                step <= currentStep ? 'bg-[#3b82f6]' : 'bg-[#e5e7eb]'
              }`}
            />
          ))}
        </div>

        {/* 에러 표시 */}
        {error && (
          <div className="mb-6 p-4 bg-[#fee2e2] border border-[#fecaca] rounded-lg text-[#991b1b]">
            {error}
          </div>
        )}

        {/* 성공 메시지 */}
        {success && (
          <div className="mb-6 p-4 bg-[#dcfce7] border border-[#86efac] rounded-lg text-[#166534]">
            ✅ 캐릭터가 성공적으로 생성되었습니다! 곧 이동합니다...
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* STEP 1: 기본 정보 */}
          {currentStep >= 1 && (
            <section className={`p-6 border rounded-lg ${currentStep === 1 ? 'border-[#3b82f6] bg-[#f0f7ff]' : 'border-[#e5e7eb]'}`}>
              <h2 className="text-[24px] font-bold mb-6 flex items-center gap-2">
                <span>📋</span>
                <span>기본 정보</span>
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    캐릭터 이름 *
                  </label>
                  <input
                    type="text"
                    name="name"
                    placeholder="예: 장영실, 수학 쌤 리사"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    한 줄 설명 *
                  </label>
                  <input
                    type="text"
                    name="short_description"
                    placeholder="예: 수학을 사랑하는 친절한 선생님"
                    value={formData.short_description}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                      카테고리
                    </label>
                    <select
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                    >
                      {CATEGORIES.map(cat => (
                        <option key={cat.value} value={cat.value}>{cat.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                      세부 항목
                    </label>
                    <select
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                    >
                      {CATEGORY_DETAILS[formData.category]?.map(item => (
                        <option key={item.value} value={item.value}>{item.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* STEP 2: 성격 설정 */}
          {currentStep >= 2 && (
            <section className={`p-6 border rounded-lg ${currentStep === 2 ? 'border-[#3b82f6] bg-[#f0f7ff]' : 'border-[#e5e7eb]'}`}>
              <h2 className="text-[24px] font-bold mb-6 flex items-center gap-2">
                <span>🎨</span>
                <span>성격 설정</span>
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    성격/특성 (쉼표로 구분) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="예: 친절함, 유머러스, 진지함"
                    value={traitsInput}
                    onChange={handleTraitsChange}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                  {traitsInput && (
                    <p className="text-[12px] text-[#6b7280] mt-1">
                      입력된 특성: {formData.personality_traits.core_traits.join(', ') || '없음'}
                    </p>
                  )}
                  <p className="text-[12px] text-[#ef4444] mt-1">
                    ⚠️ 최소 1개 이상의 성격/특성을 입력해주세요.
                  </p>
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    말투/스타일 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="예: ~요, ~네, 존댓말"
                    value={formData.personality_traits.speech_style}
                    onChange={(e) => handlePersonalityChange('speech_style', e.target.value)}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    톤/분위기
                  </label>
                  <input
                    type="text"
                    placeholder="예: 밝고 긍정적인"
                    value={formData.personality_traits.tone}
                    onChange={(e) => handlePersonalityChange('tone', e.target.value)}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    대표 멘트/캐치프레이즈
                  </label>
                  <input
                    type="text"
                    placeholder="예: 항상 응원할게!"
                    value={formData.personality_traits.catchphrase}
                    onChange={(e) => handlePersonalityChange('catchphrase', e.target.value)}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    첫 대사 *
                  </label>
                  <textarea
                    name="greeting_message"
                    placeholder="예: *방문을 열고 밝게 인사한다* 안녕! 오늘은 뭘 배우고 싶어?"
                    value={formData.greeting_message}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                  <p className="text-[12px] text-[#6b7380] mt-2">💡 팁: 행동은 *별표*, 배경은 [대괄호], 심리는 (소괄호)로 표현하세요!</p>
                </div>
              </div>
            </section>
          )}

          {/* STEP 3: 배경 및 세계관 */}
          {currentStep >= 3 && (
            <section className={`p-6 border rounded-lg ${currentStep === 3 ? 'border-[#3b82f6] bg-[#f0f7ff]' : 'border-[#e5e7eb]'}`}>
              <h2 className="text-[24px] font-bold mb-6 flex items-center gap-2">
                <span>📖</span>
                <span>배경 및 세계관</span>
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    배경 스토리 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    name="background_story"
                    placeholder="예: 저는 조선시대 과학자 장영실입니다. 천문과 시계 연구에..."
                    value={formData.background_story}
                    onChange={handleInputChange}
                    rows={4}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    세계관/배경 <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    name="world_setting"
                    placeholder="예: 현대 한국 서울, 고등학교 3학년 교실, 따뜻한 오후"
                    value={formData.world_setting}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    교수법/학습 스타일 {formData.category === 'educator' && <span className="text-red-500">*</span>}
                  </label>
                  <textarea
                    name="teaching_style"
                    placeholder="예: 소크라테스식 질문, 단계적 설명, 실생활 사례 중심"
                    value={formData.teaching_style}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                  {formData.category === 'educator' && (
                    <p className="text-[12px] text-[#6b7380] mt-1">
                      💡 교육자 카테고리는 교수법/학습 스타일이 필수입니다.
                    </p>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* STEP 4: 연출 및 기타 설정 */}
          {currentStep >= 4 && (
            <section className={`p-6 border rounded-lg ${currentStep === 4 ? 'border-[#3b82f6] bg-[#f0f7ff]' : 'border-[#e5e7eb]'}`}>
              <h2 className="text-[24px] font-bold mb-6 flex items-center gap-2">
                <span>🎭</span>
                <span>연출 스타일 및 기타 설정</span>
              </h2>

              {/* 이미지 생성 섹션 */}
              <div className="mb-8 p-4 bg-[#fef3c7] border border-[#fcd34d] rounded-lg">
                <h3 className="text-[16px] font-bold text-[#92400e] mb-3 flex items-center gap-2">
                  <span>🎨</span>
                  <span>캐릭터 아바타 생성 (선택사항)</span>
                </h3>
                <p className="text-[13px] text-[#78350f] mb-4">
                  AI가 <strong>캐릭터의 얼굴/상반신만</strong> 깔끔하게 생성해드립니다. 배경, 소품, 텍스트 등 불필요한 요소는 제외됩니다.
                </p>

                <div className="flex gap-4 items-start">
                  <div className="flex-1">
                    {generatedImageUrl ? (
                      <div className="space-y-3">
                        <div className="h-[200px] rounded-lg overflow-hidden border border-[#d1d5db]">
                          <img
                            src={generatedImageUrl}
                            alt="Generated Avatar"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={generateImage}
                          disabled={imageGenerating}
                          className="w-full px-4 py-2 bg-[#f59e0b] text-white text-[14px] font-bold rounded-lg hover:bg-[#d97706] disabled:opacity-50 transition"
                        >
                          {imageGenerating ? '생성 중...' : '다시 생성하기'}
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={generateImage}
                        disabled={imageGenerating}
                        className="w-full px-4 py-3 bg-[#f59e0b] text-white text-[14px] font-bold rounded-lg hover:bg-[#d97706] disabled:opacity-50 transition flex items-center justify-center gap-2"
                      >
                        <span>✨</span>
                        <span>{imageGenerating ? '이미지 생성 중...' : '아바타 이미지 생성하기'}</span>
                      </button>
                    )}
                  </div>
                  <div className="flex-1 text-[12px] text-[#6b7380] space-y-2">
                    <p>💡 <strong>팁:</strong></p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>캐릭터 이름과 설명을 먼저 입력하세요</li>
                      <li>프로필 사진 스타일로 얼굴/상반신만 생성됩니다</li>
                      <li>깔끔한 단색 배경으로 자동 생성됩니다</li>
                      <li>30초 정도 소요되며, 다시 생성할 수 있습니다</li>
                      <li>아바타 없이도 캐릭터를 생성할 수 있습니다</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    연출 스타일
                  </label>
                  <select
                    name="narration_style"
                    value={formData.narration_style}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  >
                    {NARRATION_STYLES.map(style => (
                      <option key={style.value} value={style.value}>{style.label}</option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                      창의성 (0.0 ~ 1.0)
                    </label>
                    <input
                      type="number"
                      name="creativity"
                      min="0"
                      max="1"
                      step="0.1"
                      value={formData.creativity}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                    />
                    <p className="text-[12px] text-[#6b7380] mt-1">낮을수록 안정적, 높을수록 창의적</p>
                  </div>

                  <div>
                    <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                      기억 범위 (턴)
                    </label>
                    <input
                      type="number"
                      name="context_length"
                      min="10"
                      max="100"
                      value={formData.context_length}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                    />
                  </div>

                  <div>
                    <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                      안전 수준
                    </label>
                    <select
                      name="moderation_level"
                      value={formData.moderation_level}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                    >
                      <option value="low">낮음</option>
                      <option value="medium">중간</option>
                      <option value="high">높음 (권장)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    태그 (쉼표로 구분) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    placeholder="예: 친절, 재미있는, 초등학생용"
                    value={tagsInput}
                    onChange={handleTagsChange}
                    className="w-full px-4 py-3 border border-[#d1d5db] rounded-lg focus:outline-none focus:border-[#3b82f6] focus:ring-2 focus:ring-[#3b82f6]/20"
                  />
                  {tagsInput && (
                    <p className="text-[12px] text-[#6b7280] mt-1">
                      입력된 태그: {formData.tags.join(', ') || '없음'}
                    </p>
                  )}
                  <p className="text-[12px] text-[#ef4444] mt-1">
                    ⚠️ 최소 1개 이상의 태그를 입력해주세요.
                  </p>
                </div>

                <div>
                  <label className="block text-[14px] font-semibold text-[#374151] mb-2">
                    예시 대화 (선택사항)
                  </label>
                  <p className="text-[12px] text-[#6b7380] mb-4">캐릭터의 말투를 더 잘 이해하도록 예시 대화를 추가하세요!</p>

                  <div className="space-y-3">
                    {formData.example_conversations.map((conv, idx) => (
                      <div key={idx} className="flex gap-2">
                        <input
                          type="text"
                          placeholder="사용자 메시지"
                          value={conv.user}
                          onChange={(e) => handleExampleConversationChange(idx, 'user', e.target.value)}
                          className="flex-1 px-3 py-2 border border-[#d1d5db] rounded-lg text-[13px] focus:outline-none focus:border-[#3b82f6]"
                        />
                        <input
                          type="text"
                          placeholder="캐릭터 응답"
                          value={conv.char}
                          onChange={(e) => handleExampleConversationChange(idx, 'char', e.target.value)}
                          className="flex-1 px-3 py-2 border border-[#d1d5db] rounded-lg text-[13px] focus:outline-none focus:border-[#3b82f6]"
                        />
                        {formData.example_conversations.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeExampleConversation(idx)}
                            className="px-3 py-2 text-[#ef4444] text-[13px] font-semibold hover:bg-[#fee2e2] rounded-lg transition"
                          >
                            삭제
                          </button>
                        )}
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={addExampleConversation}
                    className="mt-3 px-4 py-2 text-[#3b82f6] text-[14px] font-semibold hover:bg-[#f0f7ff] rounded-lg transition border border-[#3b82f6]"
                  >
                    + 예시 추가
                  </button>
                </div>
              </div>
            </section>
          )}

          {/* 네비게이션 버튼 */}
          <div className="flex gap-4 pt-6">
            {currentStep > 1 && (
              <button
                type="button"
                onClick={() => setCurrentStep(currentStep - 1)}
                className="flex-1 h-12 px-6 rounded-lg border border-[#d1d5db] text-[#374151] text-[16px] font-bold hover:bg-[#f9fafb] transition"
              >
                이전
              </button>
            )}
            {currentStep < 4 ? (
              <button
                type="button"
                onClick={() => {
                  if (validateStep(currentStep)) {
                    setCurrentStep(currentStep + 1);
                  }
                }}
                className="flex-1 h-12 px-6 rounded-lg bg-[#3b82f6] text-white text-[16px] font-bold hover:bg-[#2563eb] transition"
              >
                다음
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading}
                className="flex-1 h-12 px-6 rounded-lg bg-[#10b981] text-white text-[16px] font-bold hover:bg-[#059669] disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {loading ? '생성 중...' : '캐릭터 생성하기'}
              </button>
            )}
          </div>
        </form>
      </main>

      <Footer />
    </div>
  );
}
