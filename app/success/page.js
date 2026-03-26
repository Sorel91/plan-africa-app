"use client";

import { useEffect, useState } from "react";

export default function SuccessPage() {
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    async function confirmPayment() {
      try {
        const sessionId = new URLSearchParams(window.location.search).get("session_id");

        if (!sessionId) {
          setStatus("error");
          return;
        }

        const res = await fetch("/api/confirm-payment", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ sessionId }),
        });

        const data = await res.json();

        if (res.ok && data.success) {
          setStatus("success");
        } else {
          setStatus("error");
        }
      } catch (error) {
        console.error("Confirm payment error:", error);
        setStatus("error");
      }
    }

    confirmPayment();
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-3xl px-6 py-16 lg:px-8">
        <div className="rounded-3xl border bg-white p-8 shadow-sm text-center">
          {status === "loading" && (
            <>
              <h1 className="text-3xl font-bold">Confirmation du paiement...</h1>
              <p className="mt-4 text-slate-600">
                Nous vérifions votre paiement, veuillez patienter quelques instants.
              </p>
            </>
          )}

          {status === "success" && (
            <>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100 text-2xl">
                ✅
              </div>
              <h1 className="mt-4 text-3xl font-bold">Paiement confirmé</h1>
              <p className="mt-4 text-slate-600">
                Merci. Votre commande a bien été prise en compte.
              </p>
              <p className="mt-2 text-slate-600">
                Nous allons traiter votre demande et vous contacter si nécessaire.
              </p>

              <div className="mt-8">
                <a
                  href="/"
                  className="inline-block rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white hover:bg-emerald-700"
                >
                  Retour à l’accueil
                </a>
              </div>
            </>
          )}

          {status === "error" && (
            <>
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-100 text-2xl">
                ⚠️
              </div>
              <h1 className="mt-4 text-3xl font-bold">Impossible de confirmer le paiement</h1>
              <p className="mt-4 text-slate-600">
                Le paiement a peut-être déjà été traité, ou un problème est survenu lors de la confirmation.
              </p>
              <p className="mt-2 text-slate-600">
                Si besoin, contactez-nous via la page contact.
              </p>

              <div className="mt-8 flex flex-wrap justify-center gap-4">
                <a
                  href="/contact"
                  className="rounded-xl bg-slate-900 px-6 py-3 font-semibold text-white hover:bg-slate-800"
                >
                  Contacter le support
                </a>
                <a
                  href="/"
                  className="rounded-xl border border-slate-300 px-6 py-3 font-medium text-slate-700 hover:border-emerald-600 hover:text-emerald-700"
                >
                  Retour à l’accueil
                </a>
              </div>
            </>
          )}
        </div>
      </section>
    </main>
  );
}