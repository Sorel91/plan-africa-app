"use client";

import { useState } from "react";

export default function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("");
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
  const res = await fetch("/api/contact", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, message }),
    });

    if (res.ok) {
      setSubmitted(true);
      setName("");
      setEmail("");
      setMessage("");
    } else {
      setStatus("Erreur lors de l’envoi");
    }
  }
   return (
  <main className="min-h-screen bg-slate-50 text-slate-900">
    <section className="mx-auto max-w-4xl px-6 py-12 lg:px-8 lg:py-16">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

        {!submitted ? (
          <>
            <h1 className="text-4xl font-bold">Contact</h1>

            <p className="mt-4 text-slate-600">
              Une question ou un problème ? Envoyez-nous un message.
            </p>

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              <input
                type="text"
                placeholder="Votre nom"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3"
              />

              <input
                type="email"
                placeholder="Votre email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3"
              />

              <textarea
                placeholder="Votre message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={5}
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3"
              />

              <button
                type="submit"
                className="w-full rounded-xl bg-emerald-600 px-4 py-3 font-semibold text-white hover:bg-emerald-700"
              >
                Envoyer
              </button>
            </form>
          </>
        ) : (
          <div className="text-center py-10">
            <h1 className="text-3xl font-bold text-emerald-600">
              Message envoyé ✔
            </h1>

            <p className="mt-4 text-slate-600">
              Nous avons bien reçu votre message. Nous vous répondrons rapidement.
            </p>

            <a
              href="/"
              className="inline-block mt-6 rounded-xl bg-slate-900 px-6 py-3 text-white font-semibold hover:bg-slate-800"
            >
              Retour à l’accueil
            </a>
          </div>
        )}

      </div>
    </section>
  </main>
);
}


