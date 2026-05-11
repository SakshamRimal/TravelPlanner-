import type { Metadata } from "next";

import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import QueryProvider from "@/lib/queryClient";

export const metadata: Metadata = {
  title: "TravelPlanner",
  description: "AI-powered travel planner",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <Navbar />
          <main className="container-page py-8">{children}</main>
        </QueryProvider>
      </body>
    </html>
  );
}
