'use client';

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// 초기 상태를 동기적으로 가져오는 함수
function getInitialAuthState() {
  if (typeof window === 'undefined') {
    return { isLoggedIn: false, userName: '' };
  }
  
  try {
    const loggedIn = localStorage.getItem("isLoggedIn") === "true";
    let userName = "";
    
    if (loggedIn) {
      const user = localStorage.getItem("user");
      if (user) {
        const userData = JSON.parse(user);
        userName = userData.first_name || userData.username || userData.name || "";
      }
    }
    
    return { isLoggedIn: loggedIn, userName };
  } catch (error) {
    console.error("Failed to get auth state:", error);
    return { isLoggedIn: false, userName: '' };
  }
}

export default function Header() {
  const router = useRouter();
  const [authState, setAuthState] = useState<{ isLoggedIn: boolean; userName: string }>({ 
    isLoggedIn: false, 
    userName: '' 
  });
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // 클라이언트에서 즉시 상태 업데이트
    const state = getInitialAuthState();
    setAuthState(state);
    setIsReady(true);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setAuthState({ isLoggedIn: false, userName: '' });
    router.push("/");
  };

  return (
    <header 
      className="sticky top-0 z-10 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/90 border-b border-[#e5ebf5] transition-opacity duration-100"
      style={{ opacity: isReady ? 1 : 0 }}
    >
      <div className="mx-auto w-full max-w-screen-xl px-6">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="text-[20px] font-bold hover:opacity-80">캐릭터챗</Link>
          <nav className="hidden gap-8 text-[14px] font-medium text-[#111827] sm:flex items-center">
            <Link href="/" className="hover:text-[#3b82f6] transition-colors">소개</Link>
            <Link href="/points" className="hover:text-[#3b82f6] transition-colors">포인트</Link>
            <Link href="/characters" className="hover:text-[#3b82f6] transition-colors">캐릭터</Link>
            <Link href="/image" className="hover:text-[#3b82f6] transition-colors">이미지 생성</Link>

            <div className="flex items-center gap-3 pl-4 border-l border-[#e5ebf5]">
              {authState.isLoggedIn ? (
                <>
                  <span className="text-[14px] text-[#6b7380] font-medium whitespace-nowrap">{authState.userName}님</span>
                  <Link
                    href="/profile"
                    className="h-9 px-4 bg-[#3b82f6] text-white rounded-full hover:bg-[#2563eb] transition-colors flex items-center justify-center text-[14px] font-semibold whitespace-nowrap"
                  >
                    프로필
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="h-9 px-4 bg-[#ef4444] text-white rounded-full hover:bg-[#dc2626] transition-colors flex items-center justify-center text-[14px] font-semibold whitespace-nowrap"
                  >
                    로그아웃
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="h-9 px-5 border-2 border-[#3b82f6] text-[#3b82f6] rounded-full hover:bg-[#eff6ff] transition-colors flex items-center justify-center text-[14px] font-semibold whitespace-nowrap"
                  >
                    로그인
                  </Link>
                  <Link
                    href="/signup"
                    className="h-9 px-5 bg-[#3b82f6] text-white rounded-full hover:bg-[#2563eb] transition-colors flex items-center justify-center text-[14px] font-semibold whitespace-nowrap"
                  >
                    회원가입
                  </Link>
                </>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}

