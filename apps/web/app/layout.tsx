import "./globals.css";
import { Providers } from "@/components/providers";

export const metadata = {
  title: "ValidaHub",
  description: "Validação e correção de CSV/Sheets por marketplace×categoria",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}