"use client";

import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";

export default function Home() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [country, setCountry] = useState("");
  const [planType, setPlanType] = useState("");
  const [surface, setSurface] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");
  const [selectedFormula, setSelectedFormula] = useState("");

  useEffect(() => {
    const formula =
      typeof window !== "undefined"
        ? new URLSearchParams(window.location.search).get("formula")
        : null;

    if (formula) {
      setSelectedFormula(formula);
    }
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    const { data, error } = await supabase
      .from("requests")
      .insert([
        {
          full_name: fullName,
          email,
          country,
          plan_type: planType,
          surface,
          description,
          formula: selectedFormula || null,
          status: "submitted",
          payment_status: "pending",
        },
      ])
      .select()
      .single();

    if (error) {
      setMessage("Erreur : " + error.message);
      return;
    }

    await fetch("/api/send-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fullName,
        email,
        country,
        planType,
        surface,
        description,
      }),
    });

    if (selectedFormula) {
      const res = await fetch("/api/create-checkout-session", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          formula: selectedFormula,
          requestId: data.id,
        }),
      });

      const checkout = await res.json();

      if (checkout.url) {
        window.location.href = checkout.url;
        return;
      }
    }

    window.location.href = `/offers?requestId=${data.id}`;
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">
          <div>
            <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
              Plan Africa
            </span>

            <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Obtenez rapidement un plan 2D ou 3D adapté à votre besoin à partir 29 euros
            </h1>

            <p className="mt-5 text-lg leading-8 text-slate-600">
              Décrivez votre projet, choisissez votre formule, puis recevez un plan
              low-cost de manière simple et rapide.
            </p>

            <div className="mt-6">
              <a
                href="/comment-ca-marche"
                className="text-emerald-600 font-semibold hover:underline"
              >
                Voir comment ça marche →
              </a>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold text-slate-900">Rapide</p>
                <p className="mt-1 text-sm text-slate-600">Process simple et fluide</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold text-slate-900">Accessible</p>
                <p className="mt-1 text-sm text-slate-600">Formules à petit budget</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold text-slate-900">Professionnel</p>
                <p className="mt-1 text-sm text-slate-600">Suivi admin et relances</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xl sm:p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-slate-900">
                Décrivez votre projet
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Remplissez le formulaire puis choisissez la formule adaptée.
              </p>
            </div>

            {selectedFormula && (
              <div className="mb-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                Formule sélectionnée : <strong>{selectedFormula}</strong>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Nom complet"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />

              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              >
                <option value="">Choisir un pays</option>
                <option value="Mali">Mali</option>
                <option value="Sénégal">Sénégal</option>
                <option value="Côte d'Ivoire">Côte d'Ivoire</option>
                <option value="Burkina Faso">Burkina Faso</option>
                <option value="Mauritanie">Mauritanie</option>
              </select>

              <select
                value={planType}
                onChange={(e) => setPlanType(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              >
                <option value="">Choisir un type de plan</option>
                <option value="2D">2D</option>
                <option value="3D">3D</option>
                <option value="2D + 3D">2D + 3D</option>
              </select>

              <input
                type="text"
                placeholder="Surface du projet"
                value={surface}
                onChange={(e) => setSurface(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />

              <textarea
                placeholder="Décrivez votre besoin"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={5}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200"
              />

              <button
                type="submit"
                className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white transition hover:bg-emerald-700"
              >
                {selectedFormula ? "Continuer vers le paiement" : "Continuer vers les offres"}
              </button>
            </form>

            {message && (
              <p className="mt-4 rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
                {message}
              </p>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}