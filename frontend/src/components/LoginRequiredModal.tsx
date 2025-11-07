'use client';

import { useRouter } from 'next/navigation';

interface LoginRequiredModalProps {
  isOpen: boolean;
  onClose: () => void;
  message?: string;
  redirectUrl?: string;
}

export default function LoginRequiredModal({ 
  isOpen, 
  onClose, 
  message = "이 기능을 사용하려면 로그인이 필요합니다.",
  redirectUrl 
}: LoginRequiredModalProps) {
  const router = useRouter();

  if (!isOpen) return null;

  const handleLogin = () => {
    const currentPath = redirectUrl || window.location.pathname;
    router.push(`/login?redirect=${encodeURIComponent(currentPath)}`);
  };

  return (
    <div 
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 px-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 아이콘 */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-[#eff6ff] rounded-full flex items-center justify-center">
            <span className="text-[32px]">🔐</span>
          </div>
        </div>

        {/* 제목 */}
        <h2 className="text-[24px] font-bold text-[#111827] text-center mb-3">
          로그인이 필요합니다
        </h2>

        {/* 메시지 */}
        <p className="text-[16px] text-[#6b7380] text-center mb-8 leading-relaxed">
          {message}
        </p>

        {/* 버튼 */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 h-12 px-6 rounded-full border-2 border-[#e5ebf5] text-[#6b7380] font-semibold hover:bg-[#f9fafb] transition-colors"
          >
            취소
          </button>
          <button
            onClick={handleLogin}
            className="flex-1 h-12 px-6 rounded-full bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] text-white font-semibold hover:shadow-lg hover:scale-105 transition-all"
          >
            로그인하기
          </button>
        </div>
      </div>
    </div>
  );
}

