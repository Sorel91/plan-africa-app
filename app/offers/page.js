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

        {/* HEADER */}
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold sm:text-5xl">
            Choisissez votre formule
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Basé sur votre projet, voici les meilleures options pour concevoir votre future maison.
          </p>
        </div>

        {/* OFFRES */}
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
              <li>❌ Modification incluse</li>
            </ul>

            <button
              onClick={() => handleCheckout("basic")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Choisir Essentiel
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
              <li>✔ Estimation du coût</li>
              <li>✔ Adaptation locale</li>
              <li>✔ Détail des surfaces</li>
              <li>✔ 1 modification incluse</li>
              <li>❌ Variantes de plan</li>
            </ul>

            <button
              onClick={() => handleCheckout("standard")}
              className="mt-8 w-full rounded-xl bg-emerald-600 px-4 py-3 text-white font-semibold hover:bg-emerald-700"
            >
              Choisir Confort
            </button>
          </div>

          {/* PREMIUM */}
          <div className="rounded-3xl border bg-white p-8 shadow-sm">
            <h3 className="text-xl font-semibold">{premium?.label || "Premium"}</h3>
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
              onClick={() => handleCheckout("premium")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Choisir Premium
            </button>
          </div>

        </div>

        {/* RÉCAP */}
        {requestData && (
          <div className="mt-14 rounded-3xl border bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold">
              Votre projet
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              {requestData.description}
            </p>
          </div>
        )}

      </section>
    </main>
  );
}