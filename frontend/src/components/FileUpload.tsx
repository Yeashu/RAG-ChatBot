"use client";

import React, { useCallback, useState } from "react";
import { UploadCloud, File as FileIcon, Loader2 } from "lucide-react";
import styles from "./FileUpload.module.css";

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  isLoading: boolean;
}

export function FileUpload({ onUpload, isLoading }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        if (file.type === "application/pdf") {
          setSelectedFile(file);
          onUpload(file);
        } else {
          alert("Please upload a PDF file.");
        }
      }
    },
    [onUpload]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      e.preventDefault();
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        if (file.type === "application/pdf") {
          setSelectedFile(file);
          onUpload(file);
        } else {
          alert("Please upload a PDF file.");
        }
      }
    },
    [onUpload]
  );

  return (
    <div className={styles.uploadContainer}>
      <div
        className={`${styles.dropZone} ${dragActive ? styles.active : ""} glass`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          accept="application/pdf"
          className={styles.fileInput}
          onChange={handleChange}
          disabled={isLoading}
        />
        <label htmlFor="file-upload" className={styles.label}>
          {isLoading ? (
            <div className={styles.stateWrapper}>
              <Loader2 className={`${styles.icon} animate-pulse`} style={{ animation: 'spin 1s linear infinite' }} />
              <p>Processing document...</p>
            </div>
          ) : selectedFile ? (
            <div className={styles.stateWrapper}>
              <FileIcon className={styles.icon} />
              <p>{selectedFile.name}</p>
            </div>
          ) : (
            <div className={styles.stateWrapper}>
              <UploadCloud className={styles.icon} />
              <p>Drag and drop your PDF here</p>
              <span className={styles.subText}>or click to browse</span>
            </div>
          )}
        </label>
      </div>
    </div>
  );
}
