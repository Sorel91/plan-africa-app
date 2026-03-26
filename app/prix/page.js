"use client";
import { useEffect } from "react";
import { trackEvent } from "../../lib/trackEvent";

export default function PricingPage() {
 async function goToForm(formula) {
  await trackEvent({
    eventName: "select_formula",
    page: "/prix",
    formula,
  });

  window.location.href = `/?formula=${formula}`;
};

  window.location.href = `/?formula=${formula}`;
}
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">

        {/* HEADER */}
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Tarifs
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Choisissez la formule adaptée à votre projet
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Recevez plusieurs propositions de plans personnalisés pour concevoir votre future maison.
          </p>
        </div>

        {/* OFFRES */}
        <div className="mt-12 grid gap-6 lg:grid-cols-3">

          {/* ESSENTIEL */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">Essentiel</h3>
            <p className="mt-2 text-3xl font-bold">29€</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 2 propositions de plans personnalisés</li>
              <li>✔ Adapté à votre besoin</li>
              <li>✔ Plan clair et lisible</li>
              <li>✔ Livraison en 48h</li>
            </ul>

            <button
              onClick={() => goToForm("basic")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Commencer
            </button>
          </div>

          {/* CONFORT */}
          <div className="rounded-3xl border-2 border-emerald-500 bg-white p-8 shadow-lg">
            <div className="mb-2 text-xs text-emerald-600 font-semibold">
              LE PLUS CHOISI
            </div>

            <h3 className="text-xl font-semibold">Confort</h3>
            <p className="mt-2 text-3xl font-bold">59€</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions de plans personnalisés</li>
              <li>✔ Organisation optimisée</li>
              <li>✔ 1 modification incluse</li>
              <li>✔ Livraison en 24h – 48h</li>
            </ul>

            <button
              onClick={() => goToForm("standard")}
              className="mt-8 w-full rounded-xl bg-emerald-600 px-4 py-3 text-white font-semibold hover:bg-emerald-700"
            >
              Commencer
            </button>
          </div>

          {/* PREMIUM */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">Premium</h3>
            <p className="mt-2 text-3xl font-bold">89€</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions optimisées</li>
              <li>✔ Visualisation 3D simple</li>
              <li>✔ 2 modifications incluses</li>
              <li>✔ Traitement prioritaire (24h)</li>
            </ul>

            <button
              onClick={() => goToForm("premium")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Commencer
            </button>
          </div>

        </div>

        {/* DISCLAIMER */}
        <p className="mt-10 text-center text-sm text-slate-500">
          Ces plans sont destinés à la pré-conception et ne remplacent pas un plan technique de construction.
        </p>

      </section>
    </main>
  );
  useEffect(() => {
  trackEvent({
    eventName: "view_pricing",
    page: "/prix",
  });
}, []);
}