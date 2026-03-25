import "./globals.css"; 
export const metadata = {
  title: "Plan Africa",
  description: "Application de demande de plans 2D et 3D",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
       <body className="flex min-h-screen flex-col">
  {/* HEADER */}
  <header className="border-b bg-white px-6 py-4 flex justify-between items-center">
    <a href="/" className="font-bold text-lg">Plan Africa</a>
    <nav className="flex gap-6 text-sm">
      <a href="/" className="hover:text-emerald-600">Accueil</a> 
      <a href="/comment-ca-marche" className="hover:text-emerald-600">Comment ça marche</a>
      <a href="/contact" className="hover:text-emerald-600">Contact</a>
    </nav>
  </header>

  {/* CONTENU */}
  <main className="flex-1">{children}</main>

  {/* FOOTER */}
  <footer className="border-t bg-white px-6 py-6 text-sm text-slate-600">
    <div className="mx-auto max-w-6xl flex flex-col gap-4 sm:flex-row sm:justify-between">
      <p>© {new Date().getFullYear()} Plan Africa. Tous droits réservés.</p>

      <div className="flex gap-4">
        <a href="/contact" className="hover:text-emerald-600">Contact</a>
        <a href="#" className="hover:text-emerald-600">Mentions légales</a>
      </div>
    </div>
  </footer>
  </body>
    </html>
  );
}
