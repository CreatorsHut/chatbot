'use client';

import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useState, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  fetchCharacter,
  fetchCharacters,
  fetchConversations,
  createConversation,
  fetchConversationMessages,
  streamChat,
  addMessage,
  Character,
  CharacterDetail,
  Conversation,
  Message,
} from "@/lib/api";

const subjectColors: Record<string, string> = {
  korean: "bg-[#e6f2ff]",
  math: "bg-[#e8f9f0]",
  english: "bg-[#fff1d9]",
  science: "bg-[#f0e6ff]",
  history: "bg-[#ffe6e6]",
  social_studies: "bg-[#fff9e6]",
};

function ChatPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const characterIdParam = searchParams.get("character");
  const characterIdNum = characterIdParam ? parseInt(characterIdParam) : null;

  // 상태 관리
  const [characters, setCharacters] = useState<Character[]>([]);
  const [currentCharacter, setCurrentCharacter] = useState<CharacterDetail | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'bot' | 'choice'; text: string }>>(
    []
  );
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [messageInput, setMessageInput] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [streaming, setStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 과목별 색상 가져오기
  const getBackgroundColor = (subject: string): string => {
    return subjectColors[subject.toLowerCase()] || "bg-[#f0f0f0]";
  };

  // 메시지 파싱: 지문(*...*), 배경([...]), 심리((...))와 대사 구분
  const parseMessage = (text: string) => {
    const parts: Array<{ type: 'narration' | 'dialogue' | 'background' | 'thought'; content: string }> = [];
    let currentPos = 0;
    
    // 정규식으로 특수 표기 찾기
    const patterns = [
      { regex: /\*([^*]+)\*/g, type: 'narration' as const },      // *행동*
      { regex: /\[([^\]]+)\]/g, type: 'background' as const },    // [배경]
      { regex: /\(([^)]+)\)/g, type: 'thought' as const },        // (심리)
    ];

    const matches: Array<{ index: number; length: number; type: string; content: string }> = [];

    patterns.forEach(({ regex, type }) => {
      let match;
      while ((match = regex.exec(text)) !== null) {
        matches.push({
          index: match.index,
          length: match[0].length,
          type,
          content: match[1],
        });
      }
    });

    // 인덱스 순으로 정렬
    matches.sort((a, b) => a.index - b.index);

    // 텍스트를 파트로 나누기
    matches.forEach((match) => {
      // 이전 대사 부분
      if (currentPos < match.index) {
        const dialogue = text.slice(currentPos, match.index).trim();
        if (dialogue) {
          parts.push({ type: 'dialogue', content: dialogue });
        }
      }
      // 지문/배경/심리 부분
      parts.push({ type: match.type as any, content: match.content });
      currentPos = match.index + match.length;
    });

    // 남은 대사 부분
    if (currentPos < text.length) {
      const dialogue = text.slice(currentPos).trim();
      if (dialogue) {
        parts.push({ type: 'dialogue', content: dialogue });
      }
    }

    return parts.length > 0 ? parts : [{ type: 'dialogue' as const, content: text }];
  };

  // 메시지 자동 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 초기 데이터 로드
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);

        // localStorage에서 토큰 가져오기
        const token = localStorage.getItem("token") || "";
        
        // 캐릭터 목록 로드
        const charsData = await fetchCharacters(token || undefined);
        setCharacters(charsData);

        // URL 파라미터로 캐릭터 선택
        let selectedCharacterId: number | null = null;
        if (characterIdNum) {
          const found = charsData.find((c) => c.id === characterIdNum);
          selectedCharacterId = found?.id || charsData[0]?.id || null;
        } else {
          selectedCharacterId = charsData[0]?.id || null;
        }

        if (selectedCharacterId) {
          // 캐릭터 상세 정보 로드 (greeting_message 포함)
          const charDetail = await fetchCharacter(selectedCharacterId);
          setCurrentCharacter(charDetail);
          // 캐릭터별 대화 목록 로드
          const convsData = await fetchConversations(token);
          const filteredConvs = convsData.filter(
            (c) => c.character === selectedCharacterId
          );
          setConversations(filteredConvs);

          // 첫 번째 대화 선택 또는 새로운 대화 생성
          if (filteredConvs.length > 0) {
            const selectedConv = filteredConvs[0];
            setCurrentConversationId(selectedConv.id);
            const msgs = await fetchConversationMessages(token, selectedConv.id);
            setMessages(
              msgs.map((m) => ({
                type: m.role === 'assistant' ? 'bot' : m.role as 'user' | 'bot',
                text: m.content,
              }))
            );
          } else {
            // 새로운 대화 생성
            const newConv = await createConversation(token, selectedCharacterId);
            setCurrentConversationId(newConv.id);
            setConversations([newConv]);
            setMessages([]);
            // 인사말 추가
            const greeting = charDetail.greeting_message || "안녕하세요! 무엇을 도와드릴까요?";
            setMessages([{ type: "bot", text: greeting }]);
          }
        }
      } catch (err) {
        console.error("데이터 로드 오류:", err);
        setError("데이터를 불러오지 못했습니다. 나중에 다시 시도해주세요.");
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [characterIdNum]);

  // 메시지 전송
  const handleSendMessage = async () => {
    if (!messageInput.trim() || !currentCharacter || !currentConversationId) return;

    const userMessage = messageInput.trim();
    setMessageInput("");

    // 사용자 메시지 추가
    setMessages((prev) => [...prev, { type: "user", text: userMessage }]);

    try {
      setStreaming(true);
      const token = localStorage.getItem("token") || "";

      // 스트리밍 시작 (FastAPI가 자동으로 메시지 저장)
      const stream = await streamChat(
        currentConversationId,
        currentCharacter.id,
        userMessage,
        messages.map((m) => ({
          role: m.type === "bot" ? "assistant" : "user",
          content: m.text,
        })),
        token  // 사용자 토큰 전달
      );

      // SSE 파싱
      let botResponse = "";
      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              
              // 에러 체크
              if (data.error) {
                console.error("FastAPI/OpenAI 에러:", data.error);
                setMessages((prev) => [
                  ...prev,
                  { type: "bot", text: `⚠️ 오류: ${data.error}` },
                ]);
                return;
              }
              
              // 완료 체크
              if (data.done) {
                console.log("스트리밍 완료");
                break;
              }
              
              // 콘텐츠 처리
              if (data.content) {
                botResponse += data.content;
                // 실시간 업데이트
                setMessages((prev) => {
                  const lastMsg = prev[prev.length - 1];
                  if (lastMsg && lastMsg.type === "bot") {
                    return [
                      ...prev.slice(0, -1),
                      { ...lastMsg, text: botResponse },
                    ];
                  } else {
                    return [...prev, { type: "bot", text: botResponse }];
                  }
                });
              }
            } catch (e) {
              console.warn("JSON 파싱 오류:", e, "라인:", line);
            }
          }
        }
      }

      // 응답이 없으면 에러 표시
      if (!botResponse) {
        console.error("AI 응답이 없습니다.");
        setMessages((prev) => [
          ...prev,
          { type: "bot", text: "죄송합니다. AI 응답을 받지 못했습니다." },
        ]);
      }

      // FastAPI가 이미 메시지를 저장했으므로 별도 저장 불필요
    } catch (err) {
      console.error("메시지 전송 오류:", err);
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "죄송합니다. 메시지 전송 중 오류가 발생했습니다." },
      ]);
    } finally {
      setStreaming(false);
    }
  };

  // 캐릭터 변경
  const handleCharacterChange = (character: Character) => {
    router.push(`/chat?character=${character.id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin mb-4">
              <div className="text-[48px]">🤖</div>
            </div>
            <p className="text-[16px] text-[#6b7380]">데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-[16px] text-[#ef4444] mb-3">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="h-10 px-6 rounded-full bg-[#3b82f6] text-white text-[14px] font-bold hover:bg-[#2563eb] transition"
            >
              다시 시도
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentCharacter) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-[16px] text-[#6b7380]">캐릭터를 선택해주세요.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-white flex flex-col">
      <Header />

      <main className="flex-1 overflow-hidden mx-auto w-full max-w-screen-xl px-6 py-6 flex gap-6">
        {/* 사이드바 - 고정 너비, 독립적 스크롤 */}
        <aside className="w-[280px] bg-[#fafbfd] rounded-xl p-6 flex flex-col gap-4 overflow-y-auto flex-shrink-0">
          <h2 className="text-[16px] font-bold text-[#111827]">캐릭터</h2>
          {characters.map((character) => (
            <div
              key={character.id}
              onClick={() => handleCharacterChange(character)}
              className={`flex items-center gap-3 p-4 rounded-lg cursor-pointer transition-colors flex-shrink-0 ${
                currentCharacter.id === character.id
                  ? "bg-[#eff6ff] border-2 border-[#3b82f6]"
                  : "bg-white hover:bg-gray-50"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-[12px] ${getBackgroundColor(
                  character.subject
                )}`}
              >
                {character.avatar_url ? (
                  <img src={character.avatar_url} alt={character.name} className="w-full h-full rounded-full" />
                ) : (
                  "🤖"
                )}
              </div>
              <span className="text-[14px] font-semibold text-[#111827] truncate">{character.name}</span>
            </div>
          ))}
        </aside>

        {/* 채팅 메인 - 나머지 공간 차지, 내부 flex로 구성 */}
        <div className="flex-1 flex flex-col gap-5 overflow-hidden">
          {/* 채팅 헤더 */}
          <div className="flex items-center gap-3 justify-between flex-shrink-0">
            <div className="flex items-center gap-3">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center text-[24px] ${getBackgroundColor(
                  currentCharacter.subject
                )}`}
              >
                {currentCharacter.avatar_url ? (
                  <img
                    src={currentCharacter.avatar_url}
                    alt={currentCharacter.name}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  "🤖"
                )}
              </div>
              <div>
                <h1 className="text-[18px] font-bold text-[#111827]">{currentCharacter.name}</h1>
                <p className="text-[12px] text-[#6b7380]">{currentCharacter.subject_display}</p>
              </div>
            </div>
            <button
              onClick={() => router.push("/characters")}
              className="h-10 px-6 rounded-full bg-[#f2f5f9] text-[#111827] text-[14px] font-semibold hover:bg-[#e5ebf5] transition-colors flex-shrink-0"
            >
              ← 뒤로가기
            </button>
          </div>

          {/* 메시지 영역 - 나머지 공간 차지, 독립적 스크롤 */}
          <div className="flex-1 bg-[#fcfcfe] rounded-xl p-5 flex flex-col gap-4 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-[14px] text-[#6b7380]">대화를 시작해주세요.</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.type === "bot"
                      ? "justify-start"
                      : msg.type === "user"
                      ? "justify-end"
                      : "justify-center"
                  }`}
                >
                  {msg.type === "bot" && (
                    <div className="bg-[#eff6ff] rounded-2xl px-4 py-3.5 max-w-2xl flex-shrink-0">
                      <div className="flex flex-col gap-2">
                        {parseMessage(msg.text).map((part, partIdx) => (
                          <div key={partIdx}>
                            {part.type === 'narration' && (
                              <p className="text-[13px] text-[#6b7380] italic">
                                {part.content}
                              </p>
                            )}
                            {part.type === 'background' && (
                              <p className="text-[12px] text-[#9ca3af] italic bg-[#f9fafb] px-2 py-1 rounded">
                                {part.content}
                              </p>
                            )}
                            {part.type === 'thought' && (
                              <p className="text-[13px] text-[#8b5cf6] italic">
                                {part.content}
                              </p>
                            )}
                            {part.type === 'dialogue' && (
                              <p className="text-[14px] text-[#111827] font-medium">
                                {part.content}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {msg.type === "user" && (
                    <div className="bg-[#3b82f6] rounded-2xl px-4 py-3.5 max-w-md flex-shrink-0">
                      <p className="text-[14px] text-white whitespace-pre-wrap">{msg.text}</p>
                    </div>
                  )}
                  {msg.type === "choice" && (
                    <button className="bg-white border-2 border-[#3b82f6] rounded-xl px-5 py-3.5 hover:bg-[#eff6ff] transition-colors flex-shrink-0">
                      <p className="text-[14px] font-semibold text-[#3b82f6]">{msg.text}</p>
                    </button>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* 입력 영역 */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <input
              type="text"
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter" && !streaming) {
                  handleSendMessage();
                }
              }}
              placeholder="메시지를 입력하세요..."
              disabled={streaming}
              className="flex-1 h-11 px-5 bg-[#f2f5f9] border-2 border-transparent rounded-full text-[14px] outline-none focus:border-[#3b82f6] focus:bg-white transition-all disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={streaming || !messageInput.trim()}
              className="h-11 w-[80px] bg-[#3b82f6] text-white rounded-full text-[14px] font-bold hover:bg-[#2563eb] transition-colors flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {streaming ? "전송 중..." : "전송"}
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="inline-block animate-spin">
            <div className="text-[48px]">🤖</div>
          </div>
          <p className="text-[16px] text-[#6b7380] mt-4">로딩 중...</p>
        </div>
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  );
}
