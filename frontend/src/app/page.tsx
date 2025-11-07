'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import LoginRequiredModal from "@/components/LoginRequiredModal";
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

export default function Home() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loggedIn = localStorage.getItem("isLoggedIn") === "true";
    setIsLoggedIn(loggedIn);

    const loadCharacters = async () => {
      try {
        setLoading(true);
        setError(null);
        const token = localStorage.getItem("token");
        const data = await fetchCharacters(token || undefined);
        setCharacters(data);
      } catch (err) {
        console.error("캐릭터 로드 오류:", err);
        setError("캐릭터를 불러오지 못했습니다.");
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

  const displayCharacters = characters.slice(0, 6);

  return (
    <div className="min-h-screen bg-white text-[#111827]">
      <Header />

      {/* 로그인 필요 모달 */}
      <LoginRequiredModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        message="캐릭터와 대화하려면 로그인이 필요합니다."
        redirectUrl={selectedCharacterId ? `/chat?character=${selectedCharacterId}` : "/characters"}
      />

      <main>
        {/* 히어로 섹션 - 개선된 디자인 */}
        <section className="mx-auto w-full max-w-screen-xl px-6 pt-20 pb-12">
          <div className="text-center">
            <div className="inline-block mb-4">
              <span className="text-[60px]">🤖</span>
            </div>
            <h1 className="text-[52px] font-bold leading-tight text-[#111827]">
              AI 캐릭터와 함께<br />새로운 학습을 시작하세요
            </h1>
            <p className="mt-6 text-[20px] text-[#6b7380] max-w-3xl mx-auto">
              각 과목의 전문 AI 튜터와 1:1 대화하며 학습하세요. 언제든지, 어디서든 당신의 학습 속도에 맞춰 진행됩니다.
            </p>
            <div className="mt-10 flex gap-4 justify-center">
              <Link href="/characters">
                <button className="h-14 px-10 rounded-full bg-[#10b981] text-white text-[16px] font-bold hover:bg-[#059669] transition">
                  모든 캐릭터 보기
                </button>
              </Link>
              {isLoggedIn && (
                <Link href="/characters/create">
                  <button className="h-14 px-10 rounded-full bg-[#f2f5f9] text-[#111827] text-[16px] font-bold hover:bg-[#e5ebf5] transition">
                    ✨ 캐릭터 생성하기
                  </button>
                </Link>
              )}
            </div>
          </div>
        </section>

        {/* 캐릭터 섹션 */}
        <section className="mx-auto w-full max-w-screen-xl px-6 py-12">
          <div className="text-center mb-12">
            <h2 className="text-[40px] font-bold text-[#111827]">추천 캐릭터</h2>
            <p className="mt-3 text-[18px] text-[#6b7380]">
              지금 바로 대화할 수 있는 캐릭터들을 만나보세요
            </p>
          </div>

          {/* 로딩 상태 */}
          {loading && (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="inline-block animate-spin mb-4">
                  <div className="text-[48px]">🤖</div>
                </div>
                <p className="text-[16px] text-[#6b7380]">캐릭터를 준비하는 중...</p>
              </div>
            </div>
          )}

          {/* 에러 상태 */}
          {error && !loading && (
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <div className="text-[48px] mb-4">😓</div>
                <p className="text-[16px] text-[#111827] font-semibold mb-2">캐릭터를 준비 중입니다</p>
                <p className="text-[14px] text-[#6b7380]">잠시 후 다시 시도해주세요.</p>
              </div>
            </div>
          )}

          {/* 캐릭터 그리드 */}
          {!loading && !error && (
            <div>
              {displayCharacters.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                  {displayCharacters.map((character) => (
                    <article
                      key={character.id}
                      className="flex flex-col items-center rounded-2xl bg-white p-6 text-center h-full shadow-sm hover:shadow-lg transition-shadow border border-[#eef2f7]"
                    >
                      <div
                        className={`h-[180px] w-[180px] rounded-full ${getBackgroundColor(character.subject)} flex items-center justify-center overflow-hidden`}
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
                      <h3 className="mt-5 text-[18px] font-bold text-[#111827]">{character.name}</h3>
                      <p className="mt-2 text-[13px] text-[#6b7380] flex-1 leading-relaxed">
                        {character.short_description}
                      </p>
                      <div className="mt-3 flex gap-2 flex-wrap justify-center">
                        {character.tags.slice(0, 2).map((tag) => (
                          <span
                            key={tag}
                            className="text-[11px] bg-[#f0f0f0] text-[#666] px-2.5 py-1 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                      <button
                        onClick={() => handleChatClick(character.id)}
                        className="mt-5 h-11 px-6 rounded-full bg-[#3b82f6] text-white text-[14px] font-bold hover:bg-[#2563eb] transition flex items-center justify-center"
                      >
                        대화하기
                      </button>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center min-h-[400px]">
                  <div className="text-center">
                    <div className="text-[48px] mb-3">✨</div>
                    <p className="text-[16px] text-[#111827] font-semibold">새로운 캐릭터를 준비 중입니다</p>
                    <p className="text-[14px] text-[#6b7380] mt-2">곧 만나볼 수 있을 거예요!</p>
                  </div>
                </div>
              )}

              {/* 더보기 버튼 */}
              {displayCharacters.length > 0 && characters.length > 6 && (
                <div className="text-center mt-12">
                  <Link href="/characters">
                    <button className="h-12 px-8 rounded-full bg-[#f2f5f9] text-[#111827] text-[16px] font-bold hover:bg-[#e5ebf5] transition">
                      모든 캐릭터 보기 ({characters.length}명)
                    </button>
                  </Link>
                </div>
              )}
            </div>
          )}
        </section>

        {/* 특징 섹션 */}
        <section className="mx-auto w-full max-w-screen-xl px-6 py-16 bg-gradient-to-b from-transparent to-[#fafbfd]">
          <div className="text-center mb-12">
            <h2 className="text-[40px] font-bold text-[#111827]">왜 우리를 선택하나요?</h2>
            <p className="mt-3 text-[18px] text-[#6b7380]">
              안전하고 효과적인 학습 경험을 제공합니다
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* 카드 1 */}
            <div className="rounded-2xl bg-white p-8 text-center shadow-sm border border-[#eef2f7]">
              <div className="text-[40px] mb-4">🎓</div>
              <h3 className="text-[20px] font-bold text-[#111827] mb-3">맞춤 학습</h3>
              <p className="text-[14px] text-[#6b7380] leading-relaxed">
                학생의 수준과 속도에 맞춘 개인화된 학습을 제공합니다. 반복 학습과 피드백으로 이해도를 높입니다.
              </p>
            </div>

            {/* 카드 2 */}
            <div className="rounded-2xl bg-white p-8 text-center shadow-sm border border-[#eef2f7]">
              <div className="text-[40px] mb-4">⚡</div>
              <h3 className="text-[20px] font-bold text-[#111827] mb-3">실시간 응답</h3>
              <p className="text-[14px] text-[#6b7380] leading-relaxed">
                AI 기술로 즉시 응답하여 대기 시간 없이 자연스러운 대화를 나눕니다. 24/7 항상 준비되어 있습니다.
              </p>
            </div>

            {/* 카드 3 */}
            <div className="rounded-2xl bg-white p-8 text-center shadow-sm border border-[#eef2f7]">
              <div className="text-[40px] mb-4">🔒</div>
              <h3 className="text-[20px] font-bold text-[#111827] mb-3">안전한 환경</h3>
              <p className="text-[14px] text-[#6b7380] leading-relaxed">
                School Mode로 학생 친화적인 응답을 보장하고, 건강한 학습 환경을 유지합니다.
              </p>
            </div>
          </div>
        </section>

        {/* CTA 섹션 */}
        <section className="mx-auto w-full max-w-screen-xl px-6 py-16 text-center">
          <div className="bg-gradient-to-r from-[#3b82f6] to-[#2563eb] rounded-3xl p-12 text-white">
            <h2 className="text-[36px] font-bold mb-4">지금 시작하세요</h2>
            <p className="text-[18px] text-blue-100 mb-8 max-w-2xl mx-auto">
              회원가입 후 바로 AI 캐릭터와 대화를 시작할 수 있습니다. 무료로 시작해보세요!
            </p>
            {!isLoggedIn ? (
              <Link href="/login">
                <button className="h-13 px-10 rounded-full bg-white text-[#3b82f6] text-[16px] font-bold hover:bg-blue-50 transition">
                  로그인 / 회원가입
                </button>
              </Link>
            ) : (
              <Link href="/characters">
                <button className="h-13 px-10 rounded-full bg-white text-[#3b82f6] text-[16px] font-bold hover:bg-blue-50 transition">
                  캐릭터 만나보기
                </button>
              </Link>
            )}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
