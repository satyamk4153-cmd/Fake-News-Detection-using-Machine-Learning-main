import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TruthLens — News Credibility Assessment & Misinformation Analysis',
  description:
    'A machine-learning-assisted credibility assessment platform for analyzing potentially misleading news content with transparent multi-model signals and calibrated uncertainty.',
  keywords: [
    'news credibility',
    'misinformation detection',
    'fact checking',
    'machine learning',
    'calibrated confidence',
    'journalism verification',
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const observer = new MutationObserver((mutations) => {
                  for (const m of mutations) {
                    if (m.type === 'attributes' && m.attributeName === 'bis_skin_checked' && m.target && m.target.removeAttribute) {
                      m.target.removeAttribute('bis_skin_checked');
                    }
                  }
                });
                observer.observe(document.documentElement, { attributes: true, subtree: true, attributeFilter: ['bis_skin_checked'] });
              } catch(e) {}
            `,
          }}
        />
      </head>
      <body className="antialiased font-sans" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
