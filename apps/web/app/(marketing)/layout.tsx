import NavbarRefined from '@/components/ui/NavbarRefined'
import StickyPromoBar from '@/components/ui/StickyPromoBar'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ValidaHub - Validação inteligente de catálogos para marketplaces',
  description: 'Valide e corrija seus catálogos CSV com qualidade e velocidade. Regras canônicas por marketplace, correções automáticas e exportação pronta para publicação.',
  keywords: 'validação csv, marketplace, mercado livre, amazon, b2w, magazine luiza, catálogo produtos',
  openGraph: {
    title: 'ValidaHub - Validação inteligente de catálogos',
    description: 'Valide e corrija seus catálogos CSV com qualidade e velocidade',
    type: 'website',
    locale: 'pt_BR',
    url: 'https://validahub.com',
    siteName: 'ValidaHub',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ValidaHub - Validação inteligente de catálogos',
    description: 'Valide e corrija seus catálogos CSV com qualidade e velocidade',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <StickyPromoBar />
      <NavbarRefined />
      <div className="pt-16 min-h-screen dark:bg-zinc-950 bg-white">
        {children}
      </div>
    </>
  )
}