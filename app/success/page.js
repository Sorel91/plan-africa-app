"use client";

import { useEffect } from "react";
import { supabase } from "../../lib/supabase";

export default function SuccessPage() {
  useEffect(() => {
    async function updatePayment() {
      const urlParams = new URLSearchParams(window.location.search);
      const sessionId = urlParams.get("session_id");

      if (!sessionId) return;

      await fetch("/api/confirm-payment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sessionId }),
      });
    }

    updatePayment();
  }, []);

  return (
    <main style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Paiement réussi ✅</h1>
      <p>Votre demande est en cours de traitement.</p>
    </main>
  );
}
