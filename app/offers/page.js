"use client";

import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";

export default function OffersPage() {
  const [requestData, setRequestData] = useState(null);

  const requestId =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search).get("requestId")
      : null;

  useEffect(() => {
    async function loadRequest() {
      if (!requestId) return;

      const { data } = await supabase
        .from("requests")
        .select("*")
        .eq("id", requestId)
        .single();

      setRequestData(data);
    }

    loadRequest();
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

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Plan Africa
          </span>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Choisissez votre formule
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Sélectionnez l’offre la plus adaptée à votre besoin et finalisez votre commande.
          </p>
        </div>

        {requestData && (
          <div className="mx-auto mt-10 max-w-3xl rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-900">Résumé de votre projet</h2>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Pays</p>
                <p className="mt-1 font-medium">{requestData.country || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Type de plan</p>
                <p className="mt-1 font-medium">{requestData.plan_type || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Surface</p>
                <p className="mt-1 font-medium">{requestData.surface || "-"}</p>
              </div>

              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Statut</p>
                <p className="mt-1 font-medium">{requestData.status || "-"}</p>
              </div>
            </div>

            <div className="mt-4 rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Description</p>
              <p className="mt-1 font-medium">{requestData.description || "-"}</p>
            </div>
          </div>
        )}

        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              Basic
            </p>
            <h2 className="mt-3 text-3xl font-bold">49€</h2>
            <p className="mt-3 text-sm text-slate-600">
              Une formule simple pour un besoin rapide et accessible.
            </p>

            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              <li>• 1 proposition de plan</li>
              <li>• Format simple et lisible</li>
              <li>• Idéal pour démarrer vite</li>
            </ul>

            <button
              onClick={() => handleCheckout("basic")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 font-semibold text-white transition hover:bg-slate-800"
            >
              Choisir Basic
            </button>
          </div>

          <div className="rounded-3xl border-2 border-emerald-500 bg-white p-8 shadow-lg">
            <div className="mb-3 inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
              Le plus choisi
            </div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              Standard
            </p>
            <h2 className="mt-3 text-3xl font-bold">79€</h2>
            <p className="mt-3 text-sm text-slate-600">
              Le meilleur équilibre entre prix, détail et qualité.
            </p>

            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              <li>• Plan plus détaillé</li>
              <li>• Meilleure présentation</li>
              <li>• Adapté à la plupart des projets</li>
            </ul>

            <button
              onClick={() => handleCheckout("standard")}
              className="mt-8 w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white transition hover:bg-emerald-700"
            >
              Choisir Standard
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700">
              Premium
            </p>
            <h2 className="mt-3 text-3xl font-bold">100€</h2>
            <p className="mt-3 text-sm text-slate-600">
              Pour un rendu plus poussé et une expérience plus premium.
            </p>

            <ul className="mt-6 space-y-3 text-sm text-slate-700">
              <li>• Niveau de détail supérieur</li>
              <li>• Présentation renforcée</li>
              <li>• Convient aux projets plus exigeants</li>
            </ul>

            <button
              onClick={() => handleCheckout("premium")}
              className="mt-8 w-full rounded-xl bg-slate-900 px-4 py-3 font-semibold text-white transition hover:bg-slate-800"
            >
              Choisir Premium
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}