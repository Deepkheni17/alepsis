import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Invoice Processing System',
  description: 'AI-powered invoice processing and management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-gray-800 text-white p-4">
          <div className="container mx-auto flex gap-6">
            <Link href="/" className="font-bold hover:text-gray-300">
              Invoice System
            </Link>
            <Link href="/invoices" className="hover:text-gray-300">
              All Invoices
            </Link>
            <Link href="/upload" className="hover:text-gray-300">
              Upload
            </Link>
          </div>
        </nav>
        <main className="container mx-auto p-6">
          {children}
        </main>
      </body>
    </html>
  )
}
