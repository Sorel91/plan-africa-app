export default function ExamplesPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
        {/* HEADER */}
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Exemples
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Exemples de rendus
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Découvrez des exemples de projets et le type de rendu que vous pouvez
            recevoir avec Planora.
          </p>
        </div>

        {/* INTRO */}
        <div className="mx-auto mt-8 max-w-4xl rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm leading-7 text-slate-600">
            Chaque projet est personnalisé. Les exemples ci-dessous sont là pour vous
            aider à visualiser le niveau de clarté, d’organisation et de détail que
            vous pouvez attendre selon votre besoin.
          </p>
        </div>

        {/* EXEMPLES */}
        <div className="mt-12 space-y-8">
          {/* EXEMPLE 1 */}
          <div className="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2">
            <div>
              <div className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                Exemple 1 — Maison familiale
              </div>

              <h2 className="mt-4 text-2xl font-semibold">
                Maison familiale 3 chambres
              </h2>

              <p className="mt-3 text-slate-600">
                Projet pour une maison simple et fonctionnelle, avec salon, cuisine,
                3 chambres et 2 salles d’eau.
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Besoin client</p>
                  <p className="mt-1 text-sm font-medium">
                    Une maison pratique, claire et rapide à visualiser
                  </p>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Ce qu’il reçoit</p>
                  <p className="mt-1 text-sm font-medium">
                    Plusieurs propositions de plans + dimensions + logique d’organisation
                  </p>
                </div>
              </div>

              <ul className="mt-5 space-y-2 text-sm text-slate-600">
                <li>✔ Organisation claire des espaces</li>
                <li>✔ Répartition cohérente des pièces</li>
                <li>✔ Base exploitable pour échanger avec son entourage ou un professionnel</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm font-semibold text-slate-900">Aperçu du rendu</p>

              <div className="mt-4 grid grid-cols-3 gap-3">
                <div className="col-span-2 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Salon / Séjour
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Cuisine
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Chambre 1
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Chambre 2
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Chambre 3
                </div>
                <div className="col-span-2 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Terrasse / Circulation
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  SDB
                </div>
              </div>
            </div>
          </div>

          {/* EXEMPLE 2 */}
          <div className="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2">
            <div>
              <div className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                Exemple 2 — Villa
              </div>

              <h2 className="mt-4 text-2xl font-semibold">
                Villa avec espaces plus ouverts
              </h2>

              <p className="mt-3 text-slate-600">
                Projet pour une villa avec une circulation plus fluide, une meilleure
                répartition entre les espaces de jour et de nuit, et un rendu plus
                abouti.
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Besoin client</p>
                  <p className="mt-1 text-sm font-medium">
                    Un plan plus réfléchi avec optimisation et variantes
                  </p>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Ce qu’il reçoit</p>
                  <p className="mt-1 text-sm font-medium">
                    3 propositions, détail des surfaces, adaptation locale, estimation du coût
                  </p>
                </div>
              </div>

              <ul className="mt-5 space-y-2 text-sm text-slate-600">
                <li>✔ Meilleure optimisation des espaces</li>
                <li>✔ Vision plus claire du confort de vie</li>
                <li>✔ Plus facile de comparer plusieurs options</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm font-semibold text-slate-900">Aperçu du rendu</p>

              <div className="mt-4 grid grid-cols-4 gap-3">
                <div className="col-span-2 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Grand séjour
                </div>
                <div className="col-span-2 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Cuisine / Salle à manger
                </div>
                <div className="col-span-2 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Suite parentale
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Chambre
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Chambre
                </div>
                <div className="col-span-3 rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  Terrasse / Espace extérieur
                </div>
                <div className="rounded-2xl border bg-white p-4 text-center text-sm text-slate-600 shadow-sm">
                  SDB
                </div>
              </div>
            </div>
          </div>

          {/* EXEMPLE 3 */}
          <div className="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2">
            <div>
              <div className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                Exemple 3 — Premium
              </div>

              <h2 className="mt-4 text-2xl font-semibold">
                Projet avec options plus poussées
              </h2>

              <p className="mt-3 text-slate-600">
                Projet premium pour un client qui veut comparer plusieurs variantes,
                affiner son choix et aller plus loin dans la réflexion.
              </p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Besoin client</p>
                  <p className="mt-1 text-sm font-medium">
                    Une réflexion plus complète, plus flexible, avec priorité
                  </p>
                </div>

                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Ce qu’il reçoit</p>
                  <p className="mt-1 text-sm font-medium">
                    Variantes de plans, modifications incluses et accompagnement plus poussé
                  </p>
                </div>
              </div>

              <ul className="mt-5 space-y-2 text-sm text-slate-600">
                <li>✔ Plus de flexibilité dans la décision</li>
                <li>✔ Plus de profondeur dans la conception</li>
                <li>✔ Priorité de traitement</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-sm font-semibold text-slate-900">Aperçu du rendu</p>

              <div className="mt-4 space-y-3">
                <div className="rounded-2xl border bg-white p-4 shadow-sm">
                  <p className="text-sm font-medium text-slate-900">Variante A</p>
                  <p className="mt-1 text-sm text-slate-600">
                    Organisation centrée sur un grand espace de vie commun
                  </p>
                </div>

                <div className="rounded-2xl border bg-white p-4 shadow-sm">
                  <p className="text-sm font-medium text-slate-900">Variante B</p>
                  <p className="mt-1 text-sm text-slate-600">
                    Répartition plus équilibrée entre intimité et espace ouvert
                  </p>
                </div>

                <div className="rounded-2xl border bg-white p-4 shadow-sm">
                  <p className="text-sm font-medium text-slate-900">Variante C</p>
                  <p className="mt-1 text-sm text-slate-600">
                    Version optimisée selon contraintes et préférences du client
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-14 text-center">
          <a
            href="/prix"
            className="inline-block rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white transition hover:bg-emerald-700"
          >
            Voir les formules
          </a>
        </div>
      </section>
    </main>
  );
}