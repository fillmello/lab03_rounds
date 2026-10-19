import type { Metadata } from "next";
import "./globals.css";
import { Header } from "../components/header";

export const metadata: Metadata = {
  title: "Moeda Estudantil",
  description: "Reconhecimento que vira oportunidade.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
