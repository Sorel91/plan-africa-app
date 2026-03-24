"use client";

export default function OffersPage() {
  const requestId =
    typeof window !== "undefined"
      ? new URLSearchParams(window.location.search).get("requestId")
      : null;

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
    <main style={{ padding: "40px", fontFamily: "Arial", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Choisissez votre formule</h1>
      <p>Sélectionnez l’offre qui correspond le mieux à votre besoin.</p>

      <div style={{ display: "grid", gap: "12px", marginTop: "24px" }}>
        <button
          onClick={() => handleCheckout("basic")}
          style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}
        >
          Basic — 49€
        </button>

        <button
          onClick={() => handleCheckout("standard")}
          style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}
        >
          Standard — 79€
        </button>

        <button
          onClick={() => handleCheckout("premium")}
          style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}
        >
          Premium — 100€
        </button>
      </div>
    </main>
  );
}
