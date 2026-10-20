import type { Metadata } from "next";
import type { ReactNode } from "react";

import { QueryProvider } from "@providers/query/queryProvider";

import "./globals.css";

export const metadata: Metadata = {
  title: "Atlas",
  description: "Upload a file to Atlas.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
