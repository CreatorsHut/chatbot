export default function Footer() {
  return (
    <footer className="mx-auto w-full max-w-screen-xl px-6 py-10 text-[12px] text-[#6b7380] text-center">
      <div className="flex flex-wrap items-center justify-center gap-3">
        <span>© 2025 캐릭터챗</span>
        <a className="hover:opacity-80" href="#terms">이용약관</a>
        <a className="hover:opacity-80" href="#privacy">개인정보처리방침</a>
      </div>
    </footer>
  );
}

