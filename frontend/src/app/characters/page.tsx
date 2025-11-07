'use client';

import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import LoginRequiredModal from "@/components/LoginRequiredModal";
import { useState, useEffect } from "react";
import { fetchCharacters, Character } from "@/lib/api";

// 과목별 색상 매핑
const subjectColors: Record<string, string> = {
  korean: "bg-[#e6f2ff]",
  math: "bg-[#e8f9f0]",
  english: "bg-[#fff1d9]",
  science: "bg-[#f0e6ff]",
  history: "bg-[#ffe6e6]",
  social_studies: "bg-[#fff9e6]",
};

export default function CharactersPage() {
  const router = useRouter();
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);

  useEffect(() => {
    // 로그인 상태 확인
    const loggedIn = localStorage.getItem("isLoggedIn") === "true";
    setIsLoggedIn(loggedIn);

    const loadCharacters = async () => {
      try {
        setLoading(true);
        setError(null);
        // localStorage에서 토큰 가져오기
        const token = localStorage.getItem('token');
        const data = await fetchCharacters(token || undefined);
        setCharacters(data);
      } catch (err) {
        console.error('캐릭터 로드 오류:', err);
        setError('캐릭터를 불러오지 못했습니다. 나중에 다시 시도해주세요.');
      } finally {
        setLoading(false);
      }
    };

    loadCharacters();
  }, []);

  const handleChatClick = (characterId: number) => {
    if (!isLoggedIn) {
      setSelectedCharacterId(characterId);
      setShowLoginModal(true);
    } else {
      router.push(`/chat?character=${characterId}`);
    }
  };

  const getBackgroundColor = (subject: string): string => {
    return subjectColors[subject.toLowerCase()] || "bg-[#f0f0f0]";
  };

  return (
    <div className="min-h-screen bg-white text-[#111827]">
      <Header />
      
      {/* 로그인 필요 모달 */}
      <LoginRequiredModal 
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        message="캐릭터와 대화하려면 로그인이 필요합니다."
        redirectUrl={`/chat?character=${selectedCharacterId}`}
      />

      <main className="mx-auto w-full max-w-screen-xl px-6 py-10">
        {/* 제목 및 생성 버튼 */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-[36px] font-bold text-[#111827]">캐릭터 전체 보기</h1>
          {isLoggedIn && (
            <Link href="/characters/create">
              <button className="h-12 px-8 rounded-full bg-[#10b981] text-white text-[16px] font-bold hover:bg-[#059669] transition flex items-center gap-2">
                <span>✨</span>
                <span>캐릭터 생성하기</span>
              </button>
            </Link>
          )}
        </div>

        {/* 로딩 상태 */}
        {loading && (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="inline-block animate-spin">
                <div className="text-[48px]">🤖</div>
              </div>
              <p className="text-[16px] text-[#6b7380] mt-4">캐릭터를 준비하는 중...</p>
            </div>
          </div>
        )}

        {/* 에러 상태 */}
        {error && (
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="text-[48px] mb-4">😓</div>
              <p className="text-[16px] text-[#111827] font-semibold mb-2">캐릭터를 준비 중입니다</p>
              <p className="text-[14px] text-[#6b7380] mb-6">잠시 후 다시 시도해주세요.</p>
              <button
                onClick={() => window.location.reload()}
                className="h-10 px-6 rounded-full bg-[#3b82f6] text-white text-[14px] font-bold hover:bg-[#2563eb] transition"
              >
                다시 확인하기
              </button>
            </div>
          </div>
        )}

        {/* 카드 그리드 */}
        {!loading && !error && (
          <div className="grid grid-cols-4 gap-6">
            {characters.length > 0 ? (
              characters.map((character) => (
                <article
                  key={character.id}
                  className="flex flex-col items-center rounded-2xl bg-white p-4 text-center h-full shadow-sm hover:shadow-md transition-shadow"
                >
                  <div
                    className={`h-[160px] w-[160px] rounded-full ${getBackgroundColor(character.subject)} flex items-center justify-center overflow-hidden`}
                  >
                    {character.avatar_url ? (
                      <img
                        src={character.avatar_url}
                        alt={character.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <span className="text-[48px]">🤖</span>
                    )}
                  </div>
                  <h3 className="mt-4 text-[16px] font-bold text-[#111827]">{character.name}</h3>
                  <p className="mt-1.5 text-[13px] text-[#6b7380] flex-1">{character.short_description}</p>
                  <div className="mt-2 flex gap-2 flex-wrap justify-center">
                    {character.tags.slice(0, 2).map((tag) => (
                      <span
                        key={tag}
                        className="text-[11px] bg-[#f0f0f0] text-[#666] px-2 py-1 rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => handleChatClick(character.id)}
                    className="mt-3 h-10 px-6 rounded-full bg-[#3b82f6] text-white text-[14px] font-bold hover:bg-[#2563eb] transition flex items-center justify-center"
                  >
                    대화하기
                  </button>
                </article>
              ))
            ) : (
              <div className="col-span-4 flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                  <div className="text-[48px] mb-3">✨</div>
                  <p className="text-[16px] text-[#111827] font-semibold mb-1">새로운 캐릭터를 준비 중입니다</p>
                  <p className="text-[14px] text-[#6b7380]">곧 만나볼 수 있을 거예요!</p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

