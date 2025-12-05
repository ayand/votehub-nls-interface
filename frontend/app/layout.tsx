import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'VoteHub ChatBot',
  description: 'Full stack app with Flask and NextJS',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
