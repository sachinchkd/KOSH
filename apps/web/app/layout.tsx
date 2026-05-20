import type { Metadata } from "next";
import "./globals.css";

import { Providers } from "./providers";




export const metadata: Metadata = {
  title: "KOSH",
  description: "Friendly saving management app"
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
