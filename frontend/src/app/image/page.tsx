'use client';

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import LoginRequiredModal from "@/components/LoginRequiredModal";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { generateImage, ImageGenerationResult } from "@/lib/api";

export default function ImageGenerationPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userToken, setUserToken] = useState<string>("");
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [size, setSize] = useState<"1024x1024" | "1024x1792" | "1792x1024">("1024x1024");
  const [quality, setQuality] = useState<"standard" | "hd">("standard");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<ImageGenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Array<ImageGenerationResult & { prompt: string }>>([]);

  // 로그인 상태 확인 (리다이렉트 없음)
  useEffect(() => {
    const loggedIn = localStorage.getItem("isLoggedIn") === "true";
    const token = localStorage.getItem("token") || "";
    
    setIsLoggedIn(loggedIn);
    setUserToken(token);
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("프롬프트를 입력해주세요.");
      return;
    }

    // 로그인 체크 - 모달 표시
    if (!isLoggedIn || !userToken) {
      setShowLoginModal(true);
      return;
    }

    setGenerating(true);
    setError(null);
    setResult(null);

    try {
      const imageResult = await generateImage(prompt, size, quality, userToken);
      setResult(imageResult);
      
      // 히스토리에 추가
      setHistory(prev => [{ ...imageResult, prompt }, ...prev].slice(0, 6)); // 최대 6개만 유지
    } catch (err: any) {
      console.error('Image generation error:', err);
      setError(err.message || "이미지 생성에 실패했습니다.");
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (url: string, filename: string = 'generated-image.png') => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !generating) {
      e.preventDefault();
      handleGenerate();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f4ff] via-white to-[#fff1f3]">
      <Header />
      
      {/* 로그인 필요 모달 */}
      <LoginRequiredModal 
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        message="이미지 생성 기능을 사용하려면 로그인이 필요합니다."
        redirectUrl="/image"
      />

      <main className="mx-auto w-full max-w-screen-xl px-6 py-12">
        {/* 헤더 섹션 */}
        <div className="text-center mb-12">
          <h1 className="text-[48px] font-bold text-[#111827] mb-4">
            🎨 AI 이미지 생성
          </h1>
          <p className="text-[18px] text-[#6b7380] max-w-2xl mx-auto">
            DALL-E 3를 활용하여 텍스트 설명만으로 놀라운 이미지를 만들어보세요.
            상상하는 모든 것을 현실로 만들 수 있습니다.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* 왼쪽: 입력 폼 */}
          <div className="space-y-6">
            <div className="bg-white rounded-3xl p-8 shadow-lg border border-[#eef2f7]">
              <h2 className="text-[24px] font-bold text-[#111827] mb-6">
                이미지 설정
              </h2>

              {/* 프롬프트 입력 */}
              <div className="mb-6">
                <label className="block text-[16px] font-semibold text-[#111827] mb-3">
                  프롬프트 <span className="text-[#ef4444]">*</span>
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="예: 해질녘 바다를 바라보는 고양이, 수채화 스타일"
                  className="w-full h-32 px-4 py-3 rounded-2xl border-2 border-[#e5ebf5] focus:border-[#3b82f6] focus:outline-none resize-none text-[15px]"
                  disabled={generating}
                />
                <p className="text-[13px] text-[#6b7380] mt-2">
                  💡 상세할수록 더 좋은 결과를 얻을 수 있습니다 (Enter로 생성, Shift+Enter로 줄바꿈)
                </p>
              </div>

              {/* 크기 선택 */}
              <div className="mb-6">
                <label className="block text-[16px] font-semibold text-[#111827] mb-3">
                  이미지 크기
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setSize("1024x1024")}
                    disabled={generating}
                    className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                      size === "1024x1024"
                        ? "border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6]"
                        : "border-[#e5ebf5] text-[#6b7380] hover:border-[#3b82f6]"
                    }`}
                  >
                    정사각형
                    <div className="text-[12px] mt-1">1024×1024</div>
                  </button>
                  <button
                    onClick={() => setSize("1024x1792")}
                    disabled={generating}
                    className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                      size === "1024x1792"
                        ? "border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6]"
                        : "border-[#e5ebf5] text-[#6b7380] hover:border-[#3b82f6]"
                    }`}
                  >
                    세로형
                    <div className="text-[12px] mt-1">1024×1792</div>
                  </button>
                  <button
                    onClick={() => setSize("1792x1024")}
                    disabled={generating}
                    className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                      size === "1792x1024"
                        ? "border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6]"
                        : "border-[#e5ebf5] text-[#6b7380] hover:border-[#3b82f6]"
                    }`}
                  >
                    가로형
                    <div className="text-[12px] mt-1">1792×1024</div>
                  </button>
                </div>
              </div>

              {/* 품질 선택 */}
              <div className="mb-6">
                <label className="block text-[16px] font-semibold text-[#111827] mb-3">
                  품질
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => setQuality("standard")}
                    disabled={generating}
                    className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                      quality === "standard"
                        ? "border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6]"
                        : "border-[#e5ebf5] text-[#6b7380] hover:border-[#3b82f6]"
                    }`}
                  >
                    일반 (빠름)
                  </button>
                  <button
                    onClick={() => setQuality("hd")}
                    disabled={generating}
                    className={`px-4 py-3 rounded-xl border-2 font-medium transition-all ${
                      quality === "hd"
                        ? "border-[#3b82f6] bg-[#eff6ff] text-[#3b82f6]"
                        : "border-[#e5ebf5] text-[#6b7380] hover:border-[#3b82f6]"
                    }`}
                  >
                    고품질 (느림)
                  </button>
                </div>
              </div>

              {/* 생성 버튼 */}
              <button
                onClick={handleGenerate}
                disabled={generating}
                className={`w-full h-14 rounded-full font-bold text-[18px] transition-all ${
                  generating
                    ? "bg-[#cbd5e1] text-[#94a3b8] cursor-not-allowed"
                    : "bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white hover:shadow-xl hover:scale-105"
                }`}
              >
                {generating ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    이미지 생성 중...
                  </span>
                ) : (
                  "✨ 이미지 생성하기"
                )}
              </button>

              {/* 에러 메시지 */}
              {error && (
                <div className="mt-4 p-4 bg-[#fee2e2] border border-[#fecaca] rounded-xl text-[#dc2626] text-[14px]">
                  ⚠️ {error}
                </div>
              )}
            </div>

            {/* 예시 프롬프트 */}
            <div className="bg-white rounded-3xl p-6 shadow-lg border border-[#eef2f7]">
              <h3 className="text-[18px] font-bold text-[#111827] mb-4">💡 예시 프롬프트</h3>
              <div className="space-y-2">
                {[
                  "우주를 떠다니는 고양이, 디지털 아트",
                  "미래 도시의 스카이라인, 네온 불빛, 사이버펑크",
                  "숲 속의 작은 집, 따뜻한 빛, 수채화 스타일",
                  "드래곤과 기사의 대결, 판타지 일러스트",
                  "평화로운 호수가 있는 산, 일몰, 사진처럼",
                ].map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setPrompt(example)}
                    className="w-full text-left px-4 py-2 rounded-lg border border-[#e5ebf5] hover:border-[#3b82f6] hover:bg-[#f0f4ff] text-[14px] text-[#6b7380] transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 오른쪽: 결과 표시 */}
          <div className="space-y-6">
            {/* 생성된 이미지 */}
            {result && (
              <div className="bg-white rounded-3xl p-8 shadow-lg border border-[#eef2f7]">
                <h2 className="text-[24px] font-bold text-[#111827] mb-4">
                  생성 결과
                </h2>
                <div className="relative group">
                  <img
                    src={result.url}
                    alt={result.revised_prompt}
                    className="w-full rounded-2xl shadow-xl"
                  />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-all rounded-2xl flex items-center justify-center opacity-0 group-hover:opacity-100">
                    <button
                      onClick={() => handleDownload(result.url)}
                      className="px-6 py-3 bg-white text-[#111827] rounded-full font-bold hover:scale-110 transition-transform"
                    >
                      💾 다운로드
                    </button>
                  </div>
                </div>
                
                {/* 개선된 프롬프트 */}
                <div className="mt-6 p-4 bg-[#f0f4ff] rounded-xl">
                  <h3 className="text-[14px] font-semibold text-[#111827] mb-2">
                    📝 개선된 프롬프트 (AI가 수정)
                  </h3>
                  <p className="text-[13px] text-[#6b7380] leading-relaxed">
                    {result.revised_prompt}
                  </p>
                </div>

                {/* 모델 정보 */}
                <div className="mt-4 flex items-center justify-between text-[13px] text-[#6b7380]">
                  <span>모델: {result.model}</span>
                  <span>크기: {size}</span>
                  <span>품질: {quality === 'hd' ? '고품질' : '일반'}</span>
                </div>
              </div>
            )}

            {/* 대기 상태 */}
            {!result && !generating && (
              <div className="bg-white rounded-3xl p-12 shadow-lg border border-[#eef2f7] text-center">
                <div className="text-[64px] mb-4">🎨</div>
                <h3 className="text-[20px] font-bold text-[#111827] mb-2">
                  이미지를 생성해보세요
                </h3>
                <p className="text-[15px] text-[#6b7380]">
                  왼쪽에서 프롬프트를 입력하고<br />
                  생성 버튼을 눌러주세요
                </p>
              </div>
            )}

            {/* 생성 중 */}
            {generating && (
              <div className="bg-white rounded-3xl p-12 shadow-lg border border-[#eef2f7] text-center">
                <div className="flex justify-center mb-6">
                  <svg className="animate-spin h-16 w-16 text-[#3b82f6]" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
                <h3 className="text-[20px] font-bold text-[#111827] mb-2">
                  이미지를 생성하고 있습니다...
                </h3>
                <p className="text-[15px] text-[#6b7380]">
                  보통 10~30초 정도 소요됩니다<br />
                  잠시만 기다려주세요
                </p>
              </div>
            )}

            {/* 히스토리 */}
            {history.length > 0 && (
              <div className="bg-white rounded-3xl p-6 shadow-lg border border-[#eef2f7]">
                <h3 className="text-[18px] font-bold text-[#111827] mb-4">📚 최근 생성 이력</h3>
                <div className="grid grid-cols-3 gap-3">
                  {history.map((item, idx) => (
                    <div
                      key={idx}
                      className="relative group cursor-pointer"
                      onClick={() => setResult(item)}
                    >
                      <img
                        src={item.url}
                        alt={item.prompt}
                        className="w-full aspect-square object-cover rounded-xl hover:scale-105 transition-transform"
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/50 transition-all rounded-xl flex items-center justify-center opacity-0 group-hover:opacity-100">
                        <span className="text-white text-[12px] font-semibold">보기</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 안내 섹션 */}
        <div className="mt-12 bg-gradient-to-r from-[#eff6ff] to-[#f0f9ff] rounded-3xl p-8 border border-[#bfdbfe]">
          <h3 className="text-[20px] font-bold text-[#111827] mb-4">📌 사용 팁</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex gap-3">
              <span className="text-[24px]">🎯</span>
              <div>
                <h4 className="font-semibold text-[#111827] mb-1">구체적으로 설명하세요</h4>
                <p className="text-[14px] text-[#6b7380]">색상, 스타일, 분위기, 구도 등을 자세히 표현할수록 원하는 결과를 얻기 쉽습니다.</p>
              </div>
            </div>
            <div className="flex gap-3">
              <span className="text-[24px]">🎨</span>
              <div>
                <h4 className="font-semibold text-[#111827] mb-1">예술 스타일 명시</h4>
                <p className="text-[14px] text-[#6b7380]">"수채화", "디지털 아트", "사진처럼", "만화 스타일" 등을 추가하면 좋습니다.</p>
              </div>
            </div>
            <div className="flex gap-3">
              <span className="text-[24px]">💡</span>
              <div>
                <h4 className="font-semibold text-[#111827] mb-1">조명과 분위기</h4>
                <p className="text-[14px] text-[#6b7380]">"따뜻한 빛", "일몰", "네온 불빛" 같은 표현으로 분위기를 연출할 수 있습니다.</p>
              </div>
            </div>
            <div className="flex gap-3">
              <span className="text-[24px]">⚡</span>
              <div>
                <h4 className="font-semibold text-[#111827] mb-1">영어가 더 효과적</h4>
                <p className="text-[14px] text-[#6b7380]">한국어도 지원하지만, 영어 프롬프트가 더 정확한 결과를 제공할 수 있습니다.</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

