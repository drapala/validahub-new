import "./globals.css";
import { Providers } from "@/components/providers";
import { Inter } from 'next/font/google';

// Otimização de fonte com next/font
const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
  fallback: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
});

export const metadata = {
  title: "ValidaHub - Valide seus CSVs para marketplaces",
  description: "Reduza rejeições de 30% para menos de 3%. Validação automática de produtos para Mercado Livre, Amazon e mais.",
  openGraph: {
    title: 'ValidaHub - Valide seus CSVs para marketplaces',
    description: 'Reduza rejeições de 30% para menos de 3%. Validação automática.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}