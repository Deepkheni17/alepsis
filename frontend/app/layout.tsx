import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Alepsis — AI-Powered Invoice Processing',
  description: 'Automate invoice extraction and validation with AI. Upload, extract, and manage all your invoices in one secure platform.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  )
}
