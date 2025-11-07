'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import LoginRequiredModal from "@/components/LoginRequiredModal";

interface PointPackage {
  id: number;
  name: string;
  points: number;
  price: number;
  bonus?: number;
  popular?: boolean;
}

const pointPackages: PointPackage[] = [
  {
    id: 1,
    name: "스타터",
    points: 100,
    price: 1000,
  },
  {
    id: 2,
    name: "베이직",
    points: 500,
    price: 4500,
    bonus: 50,
  },
  {
    id: 3,
    name: "프로",
    points: 1000,
    price: 8000,
    bonus: 200,
    popular: true,
  },
  {
    id: 4,
    name: "프리미엄",
    points: 3000,
    price: 20000,
    bonus: 1000,
  },
];

export default function PointsPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState<PointPackage | null>(null);
  const [userPoints, setUserPoints] = useState(0);

  useEffect(() => {
    // 로그인 상태 확인
    const loggedIn = localStorage.getItem("isLoggedIn") === "true";
    setIsLoggedIn(loggedIn);

    // 사용자 포인트 가져오기 (실제로는 API 호출)
    if (loggedIn) {
      const user = localStorage.getItem("user");
      if (user) {
        try {
          const userData = JSON.parse(user);
          // TODO: 실제 API에서 포인트 정보 가져오기
          setUserPoints(userData.points || 0);
        } catch (e) {
          console.error('Failed to parse user data:', e);
        }
      }
    }
  }, []);

  const handlePurchaseClick = (pkg: PointPackage) => {
    if (!isLoggedIn) {
      setSelectedPackage(pkg);
      setShowLoginModal(true);
    } else {
      // TODO: 실제 결제 프로세스 구현
      alert(`${pkg.name} 패키지 구매 기능은 준비 중입니다.`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f9ff] via-white to-[#f0f4ff]">
      <Header />

      {/* 로그인 필요 모달 */}
      <LoginRequiredModal 
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        message="포인트를 구매하려면 로그인이 필요합니다."
        redirectUrl="/points"
      />

      <main className="mx-auto w-full max-w-screen-xl px-6 py-12">
        {/* 헤더 섹션 */}
        <div className="text-center mb-12">
          <h1 className="text-[48px] font-bold text-[#111827] mb-4">
            💎 포인트 충전
          </h1>
          <p className="text-[18px] text-[#6b7380] max-w-2xl mx-auto">
            포인트로 AI 캐릭터와 대화하고, 이미지를 생성하세요.
            <br />
            더 많이 충전할수록 보너스 포인트를 드립니다!
          </p>

          {/* 현재 포인트 (로그인 시에만 표시) */}
          {isLoggedIn && (
            <div className="mt-8 inline-block bg-white rounded-2xl px-8 py-4 shadow-lg border border-[#e5ebf5]">
              <div className="text-[14px] text-[#6b7380] mb-1">보유 포인트</div>
              <div className="text-[32px] font-bold text-[#3b82f6]">
                {userPoints.toLocaleString()} P
              </div>
            </div>
          )}
        </div>

        {/* 포인트 패키지 그리드 */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {pointPackages.map((pkg) => (
            <div
              key={pkg.id}
              className={`relative bg-white rounded-3xl p-6 shadow-lg border-2 transition-all hover:scale-105 flex flex-col ${
                pkg.popular
                  ? "border-[#3b82f6] shadow-xl"
                  : "border-[#eef2f7]"
              }`}
            >
              {/* 인기 배지 */}
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white text-[12px] font-bold px-4 py-1 rounded-full">
                    ⭐ 인기
                  </span>
                </div>
              )}

              {/* 패키지 정보 */}
              <div className="text-center flex-1 flex flex-col">
                <h3 className="text-[20px] font-bold text-[#111827] mb-2">
                  {pkg.name}
                </h3>
                <div className="text-[48px] font-bold text-[#3b82f6] mb-2">
                  {pkg.points.toLocaleString()}
                </div>
                <div className="text-[14px] text-[#6b7380] mb-4">포인트</div>

                {/* 보너스 - 최소 높이 유지 */}
                <div className="mb-4 min-h-[36px] flex items-center justify-center">
                  {pkg.bonus && (
                    <div className="py-2 px-4 bg-[#eff6ff] rounded-full inline-block">
                      <span className="text-[14px] font-semibold text-[#3b82f6]">
                        + {pkg.bonus} 보너스
                      </span>
                    </div>
                  )}
                </div>

                {/* 가격 */}
                <div className="text-[28px] font-bold text-[#111827] mb-6">
                  ₩{pkg.price.toLocaleString()}
                </div>

                {/* 구매 버튼 - 하단 고정 */}
                <div className="mt-auto">
                  <button
                    onClick={() => handlePurchaseClick(pkg)}
                    className={`w-full h-12 rounded-full font-bold transition-all ${
                      pkg.popular
                        ? "bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white hover:shadow-xl"
                        : "bg-[#f0f4ff] text-[#3b82f6] hover:bg-[#e0edff]"
                    }`}
                  >
                    구매하기
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 포인트 사용 안내 */}
        <div className="bg-white rounded-3xl p-8 shadow-lg border border-[#eef2f7]">
          <h2 className="text-[24px] font-bold text-[#111827] mb-6 text-center">
            📌 포인트 사용 안내
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#eff6ff] rounded-full flex items-center justify-center">
                <span className="text-[32px]">💬</span>
              </div>
              <h3 className="text-[18px] font-bold text-[#111827] mb-2">
                AI 대화
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                캐릭터와 대화할 때<br />
                메시지당 <span className="font-semibold text-[#3b82f6]">1-5 포인트</span>
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#f0f9ff] rounded-full flex items-center justify-center">
                <span className="text-[32px]">🎨</span>
              </div>
              <h3 className="text-[18px] font-bold text-[#111827] mb-2">
                이미지 생성
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                AI 이미지 생성 시<br />
                이미지당 <span className="font-semibold text-[#3b82f6]">10-20 포인트</span>
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-[#f0f4ff] rounded-full flex items-center justify-center">
                <span className="text-[32px]">✨</span>
              </div>
              <h3 className="text-[18px] font-bold text-[#111827] mb-2">
                프리미엄 기능
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                고급 AI 모델 사용 시<br />
                <span className="font-semibold text-[#3b82f6]">추가 포인트 소모</span>
              </p>
            </div>
          </div>
        </div>

        {/* FAQ 섹션 */}
        <div className="mt-12 bg-gradient-to-r from-[#f0f9ff] to-[#f0f4ff] rounded-3xl p-8 border border-[#bfdbfe]">
          <h2 className="text-[24px] font-bold text-[#111827] mb-6 text-center">
            ❓ 자주 묻는 질문
          </h2>
          <div className="space-y-4 max-w-3xl mx-auto">
            <div className="bg-white rounded-2xl p-6">
              <h3 className="text-[16px] font-bold text-[#111827] mb-2">
                포인트는 환불이 가능한가요?
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                구매 후 7일 이내, 사용하지 않은 포인트에 한해 환불이 가능합니다.
              </p>
            </div>
            <div className="bg-white rounded-2xl p-6">
              <h3 className="text-[16px] font-bold text-[#111827] mb-2">
                포인트에 유효기간이 있나요?
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                구매한 포인트는 구매일로부터 1년간 유효합니다.
              </p>
            </div>
            <div className="bg-white rounded-2xl p-6">
              <h3 className="text-[16px] font-bold text-[#111827] mb-2">
                보너스 포인트도 같은 방식으로 사용되나요?
              </h3>
              <p className="text-[14px] text-[#6b7380]">
                네, 보너스 포인트도 일반 포인트와 동일하게 사용할 수 있습니다.
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

