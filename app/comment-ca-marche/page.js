export default function HowItWorksPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-5xl px-6 py-12 lg:px-8 lg:py-16">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Comment ça marche
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Un processus simple en 3 étapes
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Décrivez votre besoin, choisissez votre formule, puis recevez votre plan
            rapidement.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-lg font-bold text-emerald-700">
              1
            </div>
            <h2 className="mt-6 text-xl font-semibold">Décrivez votre projet</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Remplissez le formulaire avec les informations principales :
              pays, type de plan, surface et description de votre besoin.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-lg font-bold text-emerald-700">
              2
            </div>
            <h2 className="mt-6 text-xl font-semibold">Choisissez votre formule</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Sélectionnez l’offre qui vous convient le mieux selon votre niveau de
              besoin, puis finalisez votre paiement en ligne.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-lg font-bold text-emerald-700">
              3
            </div>
            <h2 className="mt-6 text-xl font-semibold">Recevez votre plan</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Une fois la commande validée, votre demande est traitée et votre plan
              est préparé selon la formule choisie.
            </p>
          </div>
        </div>

        <div className="mt-12 text-center">
          <a
            href="/"
            className="inline-block rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white transition hover:bg-emerald-700"
          >
            Commencer maintenant
          </a>
        </div>
      </section>
    </main>
  );
}