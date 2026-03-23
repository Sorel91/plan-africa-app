"use client";

import { useState } from "react";
import { supabase } from "../lib/supabase";

export default function Home() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [country, setCountry] = useState("");
  const [planType, setPlanType] = useState("");
  const [surface, setSurface] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    const { error } = await supabase.from("requests").insert([
      {
        full_name: fullName,
        email,
        country,
        plan_type: planType,
        surface,
        description,
        status: "submitted",
      },
    ]);

    if (error) {
      setMessage("Erreur : " + error.message);
      return;
    }

    setMessage("Demande envoyée ✔");
    setFullName("");
    setEmail("");
    setCountry("");
    setPlanType("");
    setSurface("");
    setDescription("");
  }

  return (
    <main style={{ padding: "40px", fontFamily: "Arial", maxWidth: "700px", margin: "0 auto" }}>
      <h1>Plan Africa</h1>
      <p>Demandez votre plan 2D ou 3D.</p>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <input
          type="text"
          placeholder="Nom complet"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
          style={{ padding: "12px" }}
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ padding: "12px" }}
        />

        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          required
          style={{ padding: "12px" }}
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
          style={{ padding: "12px" }}
        >
          <option value="">Choisir un type de plan</option>
          <option value="2D">2D</option>
          <option value="3D">3D</option>
          <option value="2D + 3D">2D + 3D</option>
        </select>

        <input
          type="text"
          placeholder="Surface"
          value={surface}
          onChange={(e) => setSurface(e.target.value)}
          style={{ padding: "12px" }}
        />

        <textarea
          placeholder="Décrivez votre besoin"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
          style={{ padding: "12px" }}
        />

        <button
          type="submit"
          style={{ padding: "12px", background: "#0f766e", color: "white", border: "none" }}
        >
          Envoyer la demande
        </button>
      </form>

      <p style={{ marginTop: "16px" }}>{message}</p>
    </main>
  );
}
