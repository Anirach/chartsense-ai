import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChartSense AI — ระบบสนับสนุนการตัดสินใจทางคลินิก",
  description: "AI-Powered Clinical Decision Support Platform for Thai Hospitals",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="th" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
