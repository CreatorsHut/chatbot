'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import {
  fetchConversations,
  Conversation,
  fetchUserStats,
  fetchUserCharacters,
  fetchImageGenerations,
  fetchPointsHistory,
  UserCharacter,
  ImageGeneration,
  PointsTransaction
} from '@/lib/api';

interface UserProfile {
  id?: number;
  email: string;
  name: string;
  username?: string;
  first_name?: string;
  createdAt?: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // 포인트
  const [points, setPoints] = useState(0);
  const [pointsHistory, setPointsHistory] = useState<PointsTransaction[]>([]);

  // 캐릭터
  const [characters, setCharacters] = useState<UserCharacter[]>([]);

  // 이미지 생성
  const [imageGeneration, setImageGeneration] = useState<ImageGeneration[]>([]);

  // 대화 기록
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    // 로그인 확인
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (!isLoggedIn) {
      router.push('/login');
      return;
    }

    // 사용자 정보 로드
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      const userData = JSON.parse(storedUser);
      setUser(userData);
      setFormData({
        name: userData.first_name || userData.username || userData.name || '',
        email: userData.email,
      });
    }

    // 모든 데이터 로드
    const loadAllData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          router.push('/login');
          return;
        }

        // 병렬 로드
        const [convData, statsData, charData, imgData, pointsData] = await Promise.allSettled([
          fetchConversations(token),
          fetchUserStats(token),
          fetchUserCharacters(token),
          fetchImageGenerations(token),
          fetchPointsHistory(token),
        ]);

        // 대화 기록
        if (convData.status === 'fulfilled') {
          setConversations(convData.value);
        }

        // 통계
        if (statsData.status === 'fulfilled') {
          setPoints(statsData.value.points || 0);
        }

        // 캐릭터
        if (charData.status === 'fulfilled') {
          setCharacters(charData.value);
        }

        // 이미지
        if (imgData.status === 'fulfilled') {
          setImageGeneration(imgData.value);
        }

        // 포인트 히스토리
        if (pointsData.status === 'fulfilled') {
          setPointsHistory(pointsData.value);
        }
      } catch (err) {
        console.error('데이터 로드 오류:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAllData();
  }, [router]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');

    try {
      localStorage.setItem(
        'user',
        JSON.stringify({
          ...user,
          first_name: formData.name,
        })
      );

      setUser({
        ...user!,
        name: formData.name,
      });
      setIsEditing(false);
      setMessage('프로필이 수정되었습니다.');
    } catch (err) {
      setMessage('네트워크 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('user');
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <p className="text-[#6b7380]">로딩 중...</p>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fafbfd] flex flex-col">
      <Header />

      <main className="flex-1 mx-auto w-full max-w-screen-xl px-6 py-12">
        {/* 프로필 헤더 */}
        <div className="mb-12">
          <div className="flex items-start justify-between mb-8">
            <div>
              <h1 className="text-[44px] font-bold text-[#111827]">프로필</h1>
              <p className="mt-2 text-[16px] text-[#6b7380]">
                학습 활동과 통계를 확인하세요
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="h-10 px-6 rounded-full bg-[#fee2e2] text-[#dc2626] text-[14px] font-semibold hover:bg-[#fecaca] transition-colors"
            >
              로그아웃
            </button>
          </div>

          {/* 사용자 정보 카드 */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#eef2f7]">
            {message && (
              <div
                className={`p-3 rounded-lg text-[13px] mb-4 ${
                  message.includes('실패') || message.includes('오류')
                    ? 'bg-[#fee2e2] text-[#dc2626] border border-[#fca5a5]'
                    : 'bg-[#dcfce7] text-[#166534] border border-[#86efac]'
                }`}
              >
                {message}
              </div>
            )}

            {!isEditing ? (
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="mb-6">
                    <label className="block text-[12px] font-semibold text-[#6b7380] mb-1">
                      이름
                    </label>
                    <p className="text-[24px] font-bold text-[#111827]">{user?.name}</p>
                  </div>

                  <div className="mb-6">
                    <label className="block text-[12px] font-semibold text-[#6b7380] mb-1">
                      이메일
                    </label>
                    <p className="text-[16px] text-[#111827]">{user?.email}</p>
                  </div>

                  {user?.createdAt && (
                    <div>
                      <label className="block text-[12px] font-semibold text-[#6b7380] mb-1">
                        가입일
                      </label>
                      <p className="text-[14px] text-[#6b7380]">
                        {new Date(user.createdAt).toLocaleDateString('ko-KR')}
                      </p>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setIsEditing(true)}
                  className="h-10 px-6 rounded-lg bg-[#3b82f6] text-white text-[14px] font-semibold hover:bg-[#2563eb] transition-colors"
                >
                  프로필 수정
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {/* 이름 입력 */}
                <div>
                  <label htmlFor="name" className="block text-[14px] font-semibold text-[#111827] mb-2">
                    이름
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full h-10 px-3 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
                  />
                </div>

                {/* 이메일 입력 (읽기 전용) */}
                <div>
                  <label htmlFor="email" className="block text-[14px] font-semibold text-[#111827] mb-2">
                    이메일
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    disabled
                    className="w-full h-10 px-3 border border-[#e5ebf5] rounded-lg text-[14px] bg-[#f2f5f9] text-[#6b7380] cursor-not-allowed"
                  />
                  <p className="mt-1 text-[12px] text-[#6b7380]">이메일은 변경할 수 없습니다.</p>
                </div>

                {/* 버튼 */}
                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex-1 h-10 bg-[#3b82f6] text-white text-[14px] font-semibold rounded-lg hover:bg-[#2563eb] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {saving ? '저장 중...' : '저장'}
                  </button>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="flex-1 h-10 bg-[#f2f5f9] text-[#111827] text-[14px] font-semibold rounded-lg hover:bg-[#e5ebf5] transition-colors"
                  >
                    취소
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 3개 섹션 그리드 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* 1. 포인트 섹션 */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#eef2f7] flex flex-col h-full">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-[32px]">⭐</span>
              <h2 className="text-[24px] font-bold text-[#111827]">포인트</h2>
            </div>

            <div className="bg-gradient-to-r from-[#3b82f6] to-[#2563eb] rounded-xl p-6 text-white mb-6">
              <p className="text-[14px] text-blue-100 mb-2">보유 포인트</p>
              <p className="text-[44px] font-bold">{points.toLocaleString()}</p>
            </div>

            <div className="mb-6 flex-1">
              <h3 className="text-[14px] font-semibold text-[#111827] mb-4">최근 포인트 내역</h3>
              <div className="space-y-3 max-h-40 overflow-y-auto">
                {pointsHistory.length > 0 ? (
                  pointsHistory.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-[13px]">
                      <div>
                        <p className="text-[#111827] font-semibold">{item.type}</p>
                        <p className="text-[#6b7380] text-[12px]">
                          {new Date(item.created_at).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                      <p className="text-[#10b981] font-semibold">+{item.amount}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-[#6b7380] text-center py-4">포인트 내역이 없습니다.</p>
                )}
              </div>
            </div>

            <Link href="/characters" className="block w-full">
              <button className="w-full h-10 bg-[#f2f5f9] text-[#111827] text-[14px] font-semibold rounded-lg hover:bg-[#e5ebf5] transition-colors">
                캐릭터로 포인트 얻기
              </button>
            </Link>
          </div>

          {/* 2. 캐릭터 섹션 */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#eef2f7] flex flex-col h-full">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-[32px]">🤖</span>
              <h2 className="text-[24px] font-bold text-[#111827]">캐릭터</h2>
            </div>

            <div className="bg-[#f0f9ff] rounded-xl p-4 mb-6 text-center">
              <p className="text-[40px] font-bold text-[#3b82f6]">{characters.length}</p>
              <p className="text-[14px] text-[#6b7380] mt-2">생성한 캐릭터</p>
            </div>

            <div className="mb-6 flex-1">
              <h3 className="text-[14px] font-semibold text-[#111827] mb-4">내 캐릭터</h3>
              <div className="space-y-3 max-h-40 overflow-y-auto">
                {characters.length > 0 ? (
                  characters.map((char) => (
                    <div key={char.id} className="flex items-center justify-between text-[13px]">
                      <div>
                        <p className="text-[#111827] font-semibold">{char.name}</p>
                        <p className="text-[#6b7380] text-[12px]">
                          생성: {new Date(char.created_at).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                      <span className="bg-[#d1fae5] text-[#065f46] text-[11px] font-semibold px-2 py-1 rounded-full">
                        {char.status}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-[#6b7380] text-center py-4">생성한 캐릭터가 없습니다.</p>
                )}
              </div>
            </div>

            <Link href="/characters/create" className="block w-full">
              <button className="w-full h-10 bg-[#10b981] text-white text-[14px] font-semibold rounded-lg hover:bg-[#059669] transition-colors">
                새 캐릭터 생성
              </button>
            </Link>
          </div>

          {/* 3. 이미지 생성 섹션 */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#eef2f7] flex flex-col h-full">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-[32px]">🎨</span>
              <h2 className="text-[24px] font-bold text-[#111827]">이미지 생성</h2>
            </div>

            <div className="bg-[#fef3c7] rounded-xl p-4 mb-6 text-center">
              <p className="text-[40px] font-bold text-[#d97706]">{imageGeneration.length}</p>
              <p className="text-[14px] text-[#6b7380] mt-2">생성된 이미지</p>
            </div>

            <div className="mb-6 flex-1">
              <h3 className="text-[14px] font-semibold text-[#111827] mb-4">최근 생성</h3>
              <div className="space-y-3 max-h-40 overflow-y-auto">
                {imageGeneration.length > 0 ? (
                  imageGeneration.map((img) => (
                    <div key={img.id} className="flex items-start justify-between text-[13px]">
                      <div className="flex-1 min-w-0">
                        <p className="text-[#111827] font-semibold truncate">{img.prompt}</p>
                        <p className="text-[#6b7380] text-[12px]">
                          {new Date(img.created_at).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                      <span
                        className={`text-[11px] font-semibold px-2 py-1 rounded-full whitespace-nowrap ml-2 ${
                          img.status === 'completed' || img.status === '완료'
                            ? 'bg-[#d1fae5] text-[#065f46]'
                            : 'bg-[#fee2e2] text-[#991b1b]'
                        }`}
                      >
                        {img.status === 'completed' ? '완료' : img.status === 'failed' ? '실패' : img.status}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-[#6b7380] text-center py-4">생성된 이미지가 없습니다.</p>
                )}
              </div>
            </div>

            <Link href="/characters/create" className="block w-full">
              <button className="w-full h-10 bg-[#f2f5f9] text-[#111827] text-[14px] font-semibold rounded-lg hover:bg-[#e5ebf5] transition-colors">
                이미지 생성하기
              </button>
            </Link>
          </div>
        </div>

        {/* 최근 대화 섹션 */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-[#eef2f7]">
          <h2 className="text-[28px] font-bold text-[#111827] mb-6">최근 대화</h2>

          {conversations.length > 0 ? (
            <div className="space-y-3">
              {conversations.slice(0, 5).map((conv) => (
                <div key={conv.id} className="flex items-center justify-between p-4 bg-[#fafbfd] rounded-xl">
                  <div>
                    <p className="text-[#111827] font-semibold">{conv.character_name}</p>
                    <p className="text-[#6b7380] text-[13px] mt-1">
                      {conv.title || '제목 없음'} • {conv.message_count}개 메시지
                    </p>
                  </div>
                  <Link href={`/chat?conversation=${conv.id}`}>
                    <button className="h-9 px-4 rounded-lg bg-[#3b82f6] text-white text-[13px] font-semibold hover:bg-[#2563eb] transition-colors">
                      이어서 하기
                    </button>
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-[#6b7380] mb-4">아직 대화 기록이 없습니다.</p>
              <Link href="/characters">
                <button className="h-10 px-6 rounded-full bg-[#3b82f6] text-white text-[14px] font-semibold hover:bg-[#2563eb] transition-colors">
                  캐릭터와 대화 시작하기
                </button>
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
