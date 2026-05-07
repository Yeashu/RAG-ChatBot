"use client";

import React, { useState } from "react";
import Head from "next/head";
import { FileUpload } from "@/components/FileUpload";
import { ChatBox } from "@/components/ChatBox";
import { uploadFile } from "@/lib/api";
import styles from "./page.module.css";
import { BookOpen } from "lucide-react";

export default function Home() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const response = await uploadFile(file);
      setDocumentId(response.document_id);
    } catch (err: any) {
      setError(err.message || "An error occurred during upload.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className={styles.main}>
      <Head>
        <title>RAG Chatbot - Interact with your Documents</title>
        <meta name="description" content="Upload a PDF and chat with its content using RAG." />
      </Head>

      <header className={`${styles.header} glass`}>
        <div className={styles.logoContainer}>
          <div className={styles.logoIcon}>
            <BookOpen size={24} color="var(--color-text-light)" />
          </div>
          <h1 className={styles.title}>DocuChat<span className={styles.dot}>.</span></h1>
        </div>
        <p className={styles.subtitle}>Powered by RAG AI</p>
      </header>

      <div className={styles.content}>
        {error && (
          <div className={styles.errorBanner}>
            <p>{error}</p>
            <button onClick={() => setError(null)} className={styles.closeError}>✕</button>
          </div>
        )}

        {!documentId ? (
          <div className={`${styles.uploadSection} animate-fade-in`}>
            <div className={styles.heroText}>
              <h2>Unlock insights from your documents</h2>
              <p>Upload any PDF and instantly start chatting with its contents. Ask questions, extract summaries, and find exact references in seconds.</p>
            </div>
            <FileUpload onUpload={handleUpload} isLoading={isUploading} />
          </div>
        ) : (
          <div className={`${styles.chatSection} animate-fade-in`}>
            <ChatBox documentId={documentId} />
            <button 
              className={styles.resetButton}
              onClick={() => setDocumentId(null)}
            >
              Upload another document
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
