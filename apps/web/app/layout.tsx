import "./globals.css";
import {WalletSessionProvider} from "@/components/WalletSession";
import {GlobalNavbar} from "@/components/GlobalNavbar";

export const metadata = {
  title: "SPACLY",
  description: "GenLayer-backed intelligent migration acceptance protocol",
};

export default function Layout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body>
        <WalletSessionProvider>
          <GlobalNavbar />
          {children}
          <footer className="wrap section muted" style={{textAlign: "center", borderTop: "1px solid var(--line)", marginTop: "40px", paddingTop: "24px"}}>
            SPACLY · Studionet 61999 · Powered by GenLayer Intelligent Contracts
          </footer>
        </WalletSessionProvider>
      </body>
    </html>
  );
}
