"use client";

import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";
import { trackEvent } from "../../lib/trackEvent";

export default function PricingPage() {
  const [pricing, setPricing] = useState([]);

  useEffect(() => {
    async function loadPricing() {
      const { data, error } = await supabase
        .from("pricing")
        .select("*")
        .order("id", { ascending: true });

      if (!error && data) {
        setPricing(data);
      }
    }

    loadPricing();

    trackEvent({
      eventName: "view_pricing",
      page: "/prix",
    });
  }, []);

  async function goToForm(formula) {
    try {
      await trackEvent({
        eventName: "select_formula",
        page: "/prix",
        formula,
      });
    } catch (e) {
      console.error("Tracking error", e);
    }

    window.location.href = `/?formula=${formula}`;
  }

  const basic = pricing.find((p) => p.formula === "basic");
  const standard = pricing.find((p) => p.formula === "standard");
  const premium = pricing.find((p) => p.formula === "premium");

  function euro(amount) {
    return typeof amount === "number" ? `${amount / 100}€` : "-";
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Tarifs
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Choisissez la formule adaptée à votre projet
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Comparez nos formules et sélectionnez celle qui correspond le mieux
            à votre niveau de besoin.
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {/* ESSENTIEL */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">
              {basic?.label || "Essentiel"}
            </h3>
            <p className="mt-2 text-3xl font-bold">{euro(basic?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 2 propositions de plans</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Logique du plan optimisée</li>
              <li>✔ Checklist construction</li>
              <li>❌ Estimation du coût</li>
              <li>❌ Adaptation locale</li>
              <li>❌ Modification incluse</li>
            </ul>

            <button
              onClick={() => goToForm("basic")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Commencer avec {basic?.label || "Essentiel"}
            </button>
          </div>

          {/* CONFORT */}
          <div className="rounded-3xl border-2 border-emerald-500 bg-white p-8 shadow-lg">
            <div className="mb-2 text-xs font-semibold text-emerald-600">
              ⭐ RECOMMANDÉ
            </div>

            <h3 className="text-xl font-semibold">
              {standard?.label || "Confort"}
            </h3>
            <p className="mt-2 text-3xl font-bold">{euro(standard?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions de plans</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Estimation du coût</li>
              <li>✔ Adaptation locale</li>
              <li>✔ Détail des surfaces</li>
              <li>✔ 1 modification incluse</li>
              <li>❌ Variantes de plan</li>
            </ul>

            <button
              onClick={() => goToForm("standard")}
              className="mt-8 w-full rounded-xl bg-emerald-600 px-4 py-3 text-white font-semibold hover:bg-emerald-700"
            >
              Commencer avec {standard?.label || "Confort"}
            </button>
          </div>

          {/* PREMIUM */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">
              {premium?.label || "Premium"}
            </h3>
            <p className="mt-2 text-3xl font-bold">{euro(premium?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions optimisées</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Estimation du coût avancée</li>
              <li>✔ Adaptation locale</li>
              <li>✔ Variantes de plan</li>
              <li>✔ 2 modifications incluses</li>
              <li>✔ Optimisation avancée</li>
              <li>✔ Traitement prioritaire</li>
            </ul>

            <button
              onClick={() => goToForm("premium")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Commencer avec {premium?.label || "Premium"}
            </button>
          </div>
        </div>

        <div className="mt-12 rounded-3xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">Ce que vous recevez</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="font-medium">Des plans personnalisés</p>
              <p className="mt-2 text-sm text-slate-600">
                Chaque formule s’appuie sur les informations de votre projet.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="font-medium">Une approche claire</p>
              <p className="mt-2 text-sm text-slate-600">
                Vous comparez plusieurs propositions avant de choisir.
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="font-medium">Un service rapide</p>
              <p className="mt-2 text-sm text-slate-600">
                Livraison selon la formule choisie, avec priorité sur Premium.
              </p>
            </div>
          </div>
        </div>

        <p className="mt-10 text-center text-sm text-slate-500">
          Ces plans sont destinés à la pré-conception et ne remplacent pas un
          plan technique de construction.
        </p>
      </section>
    </main>
  );
}