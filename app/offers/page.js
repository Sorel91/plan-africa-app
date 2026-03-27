"use client";

import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";

export default function OffersPage() {
  const [requestData, setRequestData] = useState(null);
  const [pricing, setPricing] = useState([]);

  const requestId =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search).get("requestId")
      : null;

  useEffect(() => {
    async function loadData() {
      if (requestId) {
        const { data: request } = await supabase
          .from("requests")
          .select("*")
          .eq("id", requestId)
          .single();

        setRequestData(request || null);
      }

      const { data: pricingData } = await supabase
        .from("pricing")
        .select("*")
        .order("id", { ascending: true });

      setPricing(pricingData || []);
    }

    loadData();
  }, [requestId]);

  async function handleCheckout(formula) {
    const res = await fetch("/api/create-checkout-session", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ formula, requestId }),
    });

    const data = await res.json();

    if (data.url) {
      window.location.href = data.url;
    }
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
            Planora
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Choisissez votre formule
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Basé sur votre projet, voici les meilleures options pour concevoir votre future maison.
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {/* ESSENTIEL */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">{basic?.label || "Essentiel"}</h3>
            <p className="mt-2 text-3xl font-bold">{euro(basic?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 2 propositions de plans</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Logique du plan optimisée</li>
              <li>✔ Checklist construction</li>
              <li>❌ Estimation du coût</li>
              <li>❌ Adaptation locale</li>
              <li>❌ Détail des surfaces</li>
              <li>❌ Modification incluse</li>
              <li>🕒 Livraison en 48h</li>
            </ul>

            <button
              onClick={() => handleCheckout("basic")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 font-semibold text-white hover:bg-slate-800"
            >
              Choisir {basic?.label || "Essentiel"}
            </button>
          </div>

          {/* CONFORT */}
          <div className="rounded-3xl border-2 border-emerald-500 bg-white p-8 shadow-lg">
            <div className="mb-2 text-xs font-semibold text-emerald-600">
              ⭐ RECOMMANDÉ
            </div>

            <h3 className="text-xl font-semibold">{standard?.label || "Confort"}</h3>
            <p className="mt-2 text-3xl font-bold">{euro(standard?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions de plans</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Logique du plan optimisée</li>
              <li>✔ Checklist construction</li>
              <li>✔ Estimation du coût</li>
              <li>✔ Adaptation locale</li>
              <li>✔ Détail des surfaces</li>
              <li>✔ 1 modification incluse</li>
              <li>❌ Variantes de plan</li>
              <li>🕒 Livraison en 24h à 48h</li>
            </ul>

            <button
              onClick={() => handleCheckout("standard")}
              className="mt-8 w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-700"
            >
              Choisir {standard?.label || "Confort"}
            </button>
          </div>

          {/* PREMIUM */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">{premium?.label || "Premium"}</h3>
            <p className="mt-2 text-3xl font-bold">{euro(premium?.amount)}</p>

            <ul className="mt-6 space-y-2 text-sm text-slate-600">
              <li>✔ 3 propositions optimisées</li>
              <li>✔ Plan 2D avec dimensions</li>
              <li>✔ Logique du plan optimisée</li>
              <li>✔ Checklist construction</li>
              <li>✔ Estimation du coût avancée</li>
              <li>✔ Adaptation locale</li>
              <li>✔ Détail des surfaces</li>
              <li>✔ Variantes de plan</li>
              <li>✔ 2 modifications incluses</li>
              <li>✔ Optimisation avancée</li>
              <li>✔ Traitement prioritaire</li>
              <li>🕒 Livraison prioritaire en 24h</li>
            </ul>

            <button
              onClick={() => handleCheckout("premium")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 font-semibold text-white hover:bg-slate-800"
            >
              Choisir {premium?.label || "Premium"}
            </button>
          </div>
        </div>

        {requestData && (
          <div className="mx-auto mt-14 max-w-4xl rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-900">
              Récapitulatif de votre projet
            </h2>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Lieu du projet</p>
                <p className="mt-1 font-medium">{requestData.country || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Type de maison</p>
                <p className="mt-1 font-medium">{requestData.house_type || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Nombre de chambres</p>
                <p className="mt-1 font-medium">{requestData.bedrooms || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Surface</p>
                <p className="mt-1 font-medium">{requestData.surface || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4 sm:col-span-2">
                <p className="text-sm text-slate-500">Budget</p>
                <p className="mt-1 font-medium">{requestData.budget || "-"}</p>
              </div>
            </div>

            <div className="mt-4 rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Description du projet</p>
              <p className="mt-1 whitespace-pre-line font-medium">
                {requestData.description || "-"}
              </p>
            </div>
          </div>
        )}

        <p className="mt-10 text-center text-sm text-slate-500">
          Ces plans sont destinés à la pré-conception et ne remplacent pas un plan technique de construction.
        </p>
      </section>
    </main>
  );
}