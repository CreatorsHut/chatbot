'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

function LoginPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectUrl = searchParams.get('redirect') || '/';
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // 유효성 검사
    if (!formData.email || !formData.password) {
      setError('이메일과 비밀번호를 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      // API 호출
      const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.error || data.message || '로그인에 실패했습니다.');
        setLoading(false);
        return;
      }

      const data = await response.json();
      
      // 토큰 및 사용자 정보 저장
      localStorage.setItem('token', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('isLoggedIn', 'true');

      // 리다이렉트 URL로 이동 (기본값: 홈)
      router.push(redirectUrl);
    } catch (err) {
      console.error('Login error:', err);
      setError('네트워크 오류가 발생했습니다. 서버가 실행 중인지 확인해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Header />

      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-[36px] font-bold text-[#111827]">로그인</h1>
            <p className="mt-2 text-[14px] text-[#6b7380]">
              캐릭터챗에 로그인하여 학습을 시작하세요
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* 이메일 */}
            <div>
              <label htmlFor="email" className="block text-[14px] font-semibold text-[#111827] mb-2">
                이메일
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="이메일을 입력하세요"
                className="w-full h-11 px-4 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
              />
            </div>

            {/* 비밀번호 */}
            <div>
              <label htmlFor="password" className="block text-[14px] font-semibold text-[#111827] mb-2">
                비밀번호
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="비밀번호를 입력하세요"
                className="w-full h-11 px-4 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
              />
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="p-3 bg-[#fee2e2] border border-[#fca5a5] rounded-lg text-[13px] text-[#dc2626]">
                {error}
              </div>
            )}

            {/* 로그인 버튼 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-[#3b82f6] text-white text-[16px] font-bold rounded-lg hover:bg-[#2563eb] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>

            {/* 회원가입 링크 */}
            <div className="text-center text-[14px] text-[#6b7380]">
              계정이 없으신가요?{' '}
              <Link href="/signup" className="font-semibold text-[#3b82f6] hover:underline">
                회원가입
              </Link>
            </div>
          </form>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin">
            <div className="text-[48px]">🔐</div>
          </div>
          <p className="text-[16px] text-[#6b7380] mt-4">로그인 페이지 로딩 중...</p>
        </div>
      </div>
    }>
      <LoginPageContent />
    </Suspense>
  );
}
