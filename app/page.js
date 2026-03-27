"use client";

import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";
import { trackEvent } from "../lib/trackEvent";

export default function Home() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [country, setCountry] = useState("");
  const [houseType, setHouseType] = useState("");
  const [bedrooms, setBedrooms] = useState("");
  const [surface, setSurface] = useState("");
  const [budget, setBudget] = useState("");
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
          house_type: houseType,
          bedrooms: bedrooms ? Number(bedrooms) : null,
          surface,
          budget,
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
    // EMAIL CLIENT (immédiat)
await fetch("/api/send-client-email", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    fullName,
    email,
    requestId: data.id,
  }),
});

    // TRACKING (sécurisé)
    try {
      await trackEvent({
        eventName: "submit_form",
        page: "/",
        requestId: data.id,
        formula: selectedFormula || null,
      });
    } catch (e) {
      console.error("Tracking error", e);
    }

    // EMAIL
    await fetch("/api/send-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fullName,
        email,
        country,
        houseType,
        bedrooms,
        surface,
        budget,
        description,
        formula: selectedFormula || null,
      }),
    });

    // SI FORMULE → STRIPE
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

    // SINON → OFFERS
    window.location.href = `/offers?requestId=${data.id}`;
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-20">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-center">

          {/* TEXTE */}
          <div>
            <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
              Planora
            </span>

            <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl leading-tight">
              Visualisez votre future maison
              <br />
              avant de construire
            </h1>

            <div className="mt-4 inline-block rounded-xl bg-emerald-100 px-4 py-2">
              <span className="text-lg font-semibold text-emerald-700">
                À partir de 29€
              </span>
            </div>

            <p className="mt-5 text-lg text-slate-600">
              Recevez plusieurs propositions de plans personnalisés adaptées à votre projet.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <a
                href="/prix"
                className="rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-emerald-700"
              >
                Voir les prix
              </a>

              <a
                href="/comment-ca-marche"
                className="rounded-xl border border-slate-300 px-6 py-3 font-medium text-slate-700 hover:border-emerald-600 hover:text-emerald-700"
              >
                Comment ça marche
              </a>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold">Rapide</p>
                <p className="mt-1 text-sm text-slate-600">Livraison en 24h à 48h</p>
              </div>

              <div className="rounded-2xl border bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold">Personnalisé</p>
                <p className="mt-1 text-sm text-slate-600">Adapté à votre projet</p>
              </div>

              <div className="rounded-2xl border bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold">Accessible</p>
                <p className="mt-1 text-sm text-slate-600">À partir de 29€</p>
              </div>
            </div>
          </div>

          {/* FORMULAIRE */}
          <div className="rounded-3xl border bg-white p-6 shadow-xl sm:p-8">
            <h2 className="text-2xl font-semibold">Décrivez votre projet</h2>

            {selectedFormula && (
              <div className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                Formule sélectionnée : <strong>{selectedFormula}</strong>
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">

              <input
                type="text"
                placeholder="Nom complet"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full rounded-xl border px-4 py-3"
              />

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-xl border px-4 py-3"
              />

              <input
                type="text"
                placeholder="Lieu du projet (ville, pays)"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
                className="w-full rounded-xl border px-4 py-3"
              />

              <select
                value={houseType}
                onChange={(e) => setHouseType(e.target.value)}
                required
                className="w-full rounded-xl border px-4 py-3"
              >
                <option value="">Type de maison</option>
                <option value="Maison familiale">Maison familiale</option>
                <option value="Villa">Villa</option>
                <option value="Immeuble">Immeuble</option>
                <option value="Autre">Autre</option>
              </select>

              <input
                type="number"
                placeholder="Nombre de chambres"
                value={bedrooms}
                onChange={(e) => setBedrooms(e.target.value)}
                required
                className="w-full rounded-xl border px-4 py-3"
              />

              <input
                type="text"
                placeholder="Surface (optionnel)"
                value={surface}
                onChange={(e) => setSurface(e.target.value)}
                className="w-full rounded-xl border px-4 py-3"
              />

              <input
                type="text"
                placeholder="Budget approximatif (optionnel)"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full rounded-xl border px-4 py-3"
              />

              <textarea
                placeholder="Décrivez votre besoin"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full rounded-xl border px-4 py-3"
              />

              <button
                type="submit"
                className="w-full rounded-xl bg-emerald-600 px-4 py-3 text-white font-semibold"
              >
                {selectedFormula ? "Continuer vers le paiement" : "Voir les offres"}
              </button>

            </form>

            {message && <p className="mt-4 text-sm">{message}</p>}
          </div>

        </div>
      </section>
    </main>
  );
}