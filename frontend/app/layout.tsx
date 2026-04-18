import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ORVYN | Turn Conversations into Conversions",
  description: "ORVYN - Multi-tenant WhatsApp bot platform with AI assistant and WooCommerce integration.",
  icons: {
    icon: {
      url: '/logo.png',
      sizes: '192x192', // Specify size for a larger favicon
      type: 'image/png',
    },
  },
};

export default function RootLayout({
  children,
}: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
