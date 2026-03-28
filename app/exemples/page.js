export default function DeliverablesPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">

        {/* HEADER */}
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Planora
          </span>

          <h1 className="mt-4 text-4xl font-bold sm:text-5xl">
            Ce que vous recevez
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Voici concrètement le type de rendu que vous recevez après votre commande.
          </p>
        </div>

        {/* LIVRABLE 1 */}
        <div className="mt-12 grid gap-8 lg:grid-cols-2 items-center">
          <div>
            <h2 className="text-2xl font-semibold">
              Plan 2D avec dimensions
            </h2>

            <p className="mt-3 text-slate-600">
              Un plan clair et structuré de votre future maison avec les dimensions
              principales, pour visualiser immédiatement votre projet.
            </p>

            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li>✔ Répartition des pièces</li>
              <li>✔ Dimensions principales</li>
              <li>✔ Circulation logique</li>
            </ul>
          </div>

          <div className="rounded-3xl border bg-white p-4 shadow-sm">
            <img
              src="/images/plan_2D.jpg"
              alt="Plan maison"
              className="rounded-2xl"
            />
          </div>
        </div>

        {/* LIVRABLE 2 */}
        <div className="mt-16 grid gap-8 lg:grid-cols-2 items-center">
          <div className="order-2 lg:order-1 rounded-3xl border bg-white p-4 shadow-sm">
            <img
              src="https://images.unsplash.com/photo-1503387762-592deb58ef4e"
              alt="Organisation maison"
              className="rounded-2xl"
            />
          </div>

          <div className="order-1 lg:order-2">
            <h2 className="text-2xl font-semibold">
              Organisation optimisée des espaces
            </h2>

            <p className="mt-3 text-slate-600">
              Une réflexion sur la logique globale de votre maison pour améliorer
              le confort et la cohérence des espaces.
            </p>

            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li>✔ Espaces jour / nuit bien séparés</li>
              <li>✔ Optimisation des déplacements</li>
              <li>✔ Adapté à votre mode de vie</li>
            </ul>
          </div>
        </div>

        {/* LIVRABLE 3 */}
        <div className="mt-16 grid gap-8 lg:grid-cols-2 items-center">
          <div>
            <h2 className="text-2xl font-semibold">
              Checklist construction
            </h2>

            <p className="mt-3 text-slate-600">
              Une checklist claire pour vous guider dans la suite de votre projet
              et ne rien oublier.
            </p>

            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li>✔ Étapes clés du projet</li>
              <li>✔ Points de vigilance</li>
              <li>✔ Aide à la prise de décision</li>
            </ul>
          </div>

          <div className="rounded-3xl border bg-white p-4 shadow-sm">
            <img
              src="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c"
              alt="Checklist"
              className="rounded-2xl"
            />
          </div>
        </div>

        {/* LIVRABLE 4 */}
        <div className="mt-16 grid gap-8 lg:grid-cols-2 items-center">
          <div className="order-2 lg:order-1 rounded-3xl border bg-white p-4 shadow-sm">
            <img
              src="https://images.unsplash.com/photo-1497366216548-37526070297c"
              alt="Variantes"
              className="rounded-2xl"
            />
          </div>

          <div className="order-1 lg:order-2">
            <h2 className="text-2xl font-semibold">
              Variantes de plans (selon formule)
            </h2>

            <p className="mt-3 text-slate-600">
              Plusieurs propositions pour comparer et choisir la meilleure
              configuration pour votre projet.
            </p>

            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li>✔ Comparaison facile</li>
              <li>✔ Ajustements possibles</li>
              <li>✔ Vision plus complète</li>
            </ul>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <a
            href="/prix"
            className="inline-block rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white hover:bg-emerald-700"
          >
            Voir les formules
          </a>
        </div>

      </section>
    </main>
  );
}