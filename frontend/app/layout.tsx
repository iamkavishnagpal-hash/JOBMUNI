import type { Metadata } from "next";
import "./globals.css";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { MobileNavBar } from "@/components/layout/MobileNavBar";

export const metadata: Metadata = {
  title: "Kavish Career OS — Executive Operating System",
  description: "Personal Career Operating System for Senior Data, BI & Analytics Leaders",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen flex antialiased selection:bg-accent-indigo selection:text-white">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0 overflow-y-auto max-h-screen">
          <main className="p-4 sm:p-6 md:p-8 max-w-7xl w-full mx-auto">{children}</main>
        </div>
        <MobileNavBar />
      </body>
    </html>
  );
}
