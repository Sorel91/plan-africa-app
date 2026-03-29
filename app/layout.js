import "./globals.css";

export const metadata = {
  title: "Planora — Visualisez votre maison avant de construire",
  description: "Obtenez des plans personnalisés rapidement avec Planora.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
        <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 lg:px-8">
            <a
              href="/"
              className="text-lg font-bold tracking-tight text-slate-900"
            >
              Planora
            </a>

            <nav className="hidden items-center gap-3 md:flex">
              <a
                href="/"
                className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-emerald-700"
              >
                Accueil
              </a>

              <a
                href="/comment-ca-marche"
                className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-emerald-700"
              >
                Comment ça marche
              </a>

              <a
                href="/exemples"
                className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-emerald-700"
              >
                Exemples
              </a>

              <a
                href="/prix"
                className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
              >
                Voir les prix
              </a>

              <a
                href="/contact"
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-emerald-600 hover:text-emerald-700"
              >
                Contact
              </a>
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-slate-200 bg-white px-6 py-6 text-sm text-slate-600">
          <div className="mx-auto flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p>© {new Date().getFullYear()} Planora. Tous droits réservés.</p>

            <div className="flex gap-4">
              <a href="/prix" className="hover:text-emerald-600">
                Prix
              </a>
              <a href="/exemples" className="hover:text-emerald-600">
                Exemples
              </a>
              <a href="/contact" className="hover:text-emerald-600">
                Contact
              </a>
              <a href="/comment-ca-marche" className="hover:text-emerald-600">
                Comment ça marche
              </a>
            </div>
          </div>
        </footer>
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-417498809">
</script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'AW-417498809');
</script>
      </body>
    </html>
  );
}