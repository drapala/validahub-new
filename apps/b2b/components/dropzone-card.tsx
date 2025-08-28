"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { FileUp } from "lucide-react";

export function DropzoneCard({
  onFileAccepted,
  currentFile
}: {
  onFileAccepted: (file: File) => void;
  currentFile: File | null;
}) {
  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) onFileAccepted(accepted[0]);
  }, [onFileAccepted]);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    multiple: false
  });

  return (
    <div
      {...getRootProps()}
      className="card p-6 text-center cursor-pointer"
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-2">
        <FileUp />
        {isDragActive ? (
          <p>Solte o arquivo aqui…</p>
        ) : currentFile ? (
          <div>
            <p className="font-medium">{currentFile.name}</p>
            <p className="text-zinc-400 text-sm">
              {(currentFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <>
            <p className="font-medium">Arraste e solte seu CSV aqui</p>
            <p className="text-zinc-400 text-sm">ou clique para selecionar</p>
          </>
        )}
      </div>
    </div>
  );
}