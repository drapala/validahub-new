"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Toaster } from "sonner";
import { AuthProvider } from "@/src/auth/ui/providers/auth-provider";
import { SessionProvider } from "next-auth/react";
import { ThemeProvider } from "next-themes";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient());
  return (
    <SessionProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <QueryClientProvider client={client}>
          <AuthProvider>
            {children}
            <Toaster richColors position="bottom-right" />
          </AuthProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </SessionProvider>
  );
}