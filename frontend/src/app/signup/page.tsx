'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
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

    console.log('[Signup] Form submitted with:', { email: formData.email, name: formData.name });

    // 유효성 검사
    if (!formData.email || !formData.password || !formData.name) {
      setError('모든 필드를 입력해주세요.');
      setLoading(false);
      console.log('[Signup] Validation failed: missing fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      setLoading(false);
      console.log('[Signup] Validation failed: passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('비밀번호는 최소 8자 이상이어야 합니다.');
      setLoading(false);
      console.log('[Signup] Validation failed: password too short');
      return;
    }

    try {
      // API 함수 사용으로 변경
      const { register } = await import('@/lib/api');
      
      console.log('[Signup] Sending request:', {
        email: formData.email,
        username: formData.name,
        first_name: formData.name,
      });

      const data = await register(
        formData.email,
        formData.name,
        formData.name,
        formData.password,
        formData.confirmPassword
      );

      console.log('[Signup] Registration successful, storing token and user data');
      localStorage.setItem('token', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('user', JSON.stringify(data.user));

      console.log('[Signup] Redirecting to home page');
      router.push('/');
    } catch (err: any) {
      console.error('[Signup] Error:', err);
      setError(err.message || '회원가입에 실패했습니다.');
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
            <h1 className="text-[36px] font-bold text-[#111827]">회원가입</h1>
            <p className="mt-2 text-[14px] text-[#6b7380]">
              캐릭터챗에 가입하여 AI 학습을 시작하세요
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* 이름 */}
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
                placeholder="이름을 입력하세요"
                className="w-full h-11 px-4 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
              />
            </div>

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
                placeholder="8자 이상의 비밀번호"
                className="w-full h-11 px-4 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
              />
            </div>

            {/* 비밀번호 확인 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-[14px] font-semibold text-[#111827] mb-2">
                비밀번호 확인
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="비밀번호를 다시 입력하세요"
                className="w-full h-11 px-4 border border-[#e5ebf5] rounded-lg text-[14px] outline-none focus:ring-2 focus:ring-[#3b82f6] transition-all"
              />
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="p-3 bg-[#fee2e2] border border-[#fca5a5] rounded-lg text-[13px] text-[#dc2626]">
                {error}
              </div>
            )}

            {/* 가입 버튼 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-[#3b82f6] text-white text-[16px] font-bold rounded-lg hover:bg-[#2563eb] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '가입 중...' : '회원가입'}
            </button>

            {/* 로그인 링크 */}
            <div className="text-center text-[14px] text-[#6b7380]">
              이미 계정이 있으신가요?{' '}
              <Link href="/login" className="font-semibold text-[#3b82f6] hover:underline">
                로그인
              </Link>
            </div>
          </form>
        </div>
      </main>

      <Footer />
    </div>
  );
}
