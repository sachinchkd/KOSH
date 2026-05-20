import type { Metadata } from "next";
import "./globals.css";

import { Providers } from "./providers";




export const metadata: Metadata = {
  title: "KOSH v1.0",
  description: "Friendly saving management app",
  openGraph: {
    title: "Kosh",
    description: "Your app description",
    url: "https://kosh-web-chi.vercel.app/",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
