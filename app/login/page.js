"use client";

import { useState } from "react";
import { supabase } from "../../../lib/supabase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  async function handleLogin(e) {
    e.preventDefault();

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setMessage("Erreur : " + error.message);
      return;
    }

    setMessage("Connexion réussie");
    window.location.href = "/admin";
  }

  return (
    <main style={{ padding: "40px", fontFamily: "Arial", maxWidth: "400px", margin: "0 auto" }}>
      <h1>Connexion admin</h1>

      <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ padding: "12px" }}
        />

        <input
          type="password"
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ padding: "12px" }}
        />

        <button type="submit" style={{ padding: "12px", background: "#0f766e", color: "white", border: "none" }}>
          Se connecter
        </button>
      </form>

      <p style={{ marginTop: "16px" }}>{message}</p>
    </main>
  );
}
