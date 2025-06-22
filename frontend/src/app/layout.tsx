import type { Metadata } from 'next'
import './globals.css'
import Navigation from '@/components/Navigation'
import FloatingChatBot from '@/components/FloatingChatBot'

export const metadata: Metadata = {
  title: 'stubble burning detection system',
  description: 'advanced fire detection and prediction for northern india',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-ash-light">
          <Navigation />
          <main className="pt-16">
            {children}
          </main>
          <FloatingChatBot />
        </div>
      </body>
    </html>
  )
}