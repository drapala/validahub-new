"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="container-app py-24">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="text-center space-y-6"
      >
        <h1 className="text-5xl font-semibold tracking-tight">
          Valide e corrija seus catálogos CSV com qualidade e velocidade
        </h1>
        <p className="text-zinc-400 max-w-2xl mx-auto">
          Fluxo síncrono para até 1k linhas e assíncrono para alto volume.
          Correções seguras com preview, links assinados e histórico de jobs.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/upload" className="btn btn-primary">Começar agora</Link>
          <Link href="/docs" className="btn btn-ghost">Documentação</Link>
        </div>
      </motion.div>
    </main>
  );
}