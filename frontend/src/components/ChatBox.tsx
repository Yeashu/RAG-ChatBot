"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, User, Bot, FileText } from "lucide-react";
import styles from "./ChatBox.module.css";
import { chat, SourceChunk } from "../lib/api";

interface Message {
  role: "user" | "bot";
  content: string;
  sources?: SourceChunk[];
}

interface ChatBoxProps {
  documentId: string;
}

export function ChatBox({ documentId }: ChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      content: "Document uploaded successfully! What would you like to know about it?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    try {
      const response = await chat(documentId, userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (error: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: `Error: ${error.message || "Failed to get response"}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={`${styles.chatContainer} glass animate-fade-in`}>
      <div className={styles.messagesArea}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`${styles.messageWrapper} ${
              msg.role === "user" ? styles.userMessage : styles.botMessage
            } animate-fade-in`}
          >
            <div className={styles.avatar}>
              {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className={styles.messageContent}>
              <div className={styles.bubble}>
                <p>{msg.content}</p>
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className={styles.sourcesContainer}>
                  <p className={styles.sourcesTitle}>Sources:</p>
                  <div className={styles.sourcesList}>
                    {msg.sources.map((source, sIdx) => (
                      <div key={sIdx} className={styles.sourceTag}>
                        <FileText size={12} />
                        <span>Page {source.page_number}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className={`${styles.messageWrapper} ${styles.botMessage} animate-fade-in`}>
            <div className={styles.avatar}>
              <Bot size={20} />
            </div>
            <div className={styles.messageContent}>
              <div className={styles.bubble}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <form onSubmit={handleSend} className={styles.inputForm}>
          <textarea
            className={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the document..."
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={!input.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
