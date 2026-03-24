"use client";

export default function OffersPage() {
  return (
    <main style={{ padding: "40px", fontFamily: "Arial", maxWidth: "800px", margin: "0 auto" }}>
      <h1>Choisissez votre formule</h1>
      <p>Sélectionnez l’offre qui correspond le mieux à votre besoin.</p>

      <div style={{ display: "grid", gap: "12px", marginTop: "24px" }}>
        <button style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}>
          Basic — 49€
        </button>

        <button style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}>
          Standard — 79€
        </button>

        <button style={{ padding: "16px", border: "1px solid #ccc", background: "white" }}>
          Premium — 100€
        </button>
      </div>
    </main>
  );
}
