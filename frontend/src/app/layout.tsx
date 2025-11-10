import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI 교육 캐릭터 채팅 플랫폼 - StudyVerse",
  description: "학생들을 위한 AI 기반 개인 튜터 시스템. 다양한 캐릭터 튜터와 1:1로 대화하며 맞춤형 학습을 받으세요.",
  keywords: ["AI 튜터", "온라인 교육", "학습 플랫폼", "AI 채팅", "개인 과외"],
  viewport: "width=device-width, initial-scale=1",
  verification: {
    google: "cp89UQyIW6fFZpRgTxLkNB3HMR5wkp87QsMWvRXiZQE",
  },
  metadataBase: new URL("https://studyverse.store"),
  alternates: {
    canonical: "https://studyverse.store",
  },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    url: "https://studyverse.store",
    title: "AI 교육 캐릭터 채팅 플랫폼 - StudyVerse",
    description: "학생들을 위한 AI 기반 개인 튜터 시스템",
    siteName: "StudyVerse",
  },
  other: {
    "naver-site-verification": "8ae64c8cd79de2d9f2f7a7d6e3c4b5a6",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
