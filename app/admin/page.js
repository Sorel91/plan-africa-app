"use client";

import { useEffect, useState } from "react";
import { supabase } from "../../lib/supabase";

export default function AdminPage() {
  const [requests, setRequests] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadRequests() {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session) {
        window.location.href = "/login";
        return;
      }

      const { data, error } = await supabase
        .from("requests")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) {
        setMessage("Erreur : " + error.message);
        return;
      }

      setRequests(data || []);
    }

    loadRequests();
  }, []);

  return (
    <main style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Admin - Demandes</h1>
      <p>{message}</p>

      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Nom</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Email</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Pays</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Type</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Surface</th>
            <th style={{ border: "1px solid #ccc", padding: "10px" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>{r.full_name}</td>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>{r.email}</td>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>{r.country}</td>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>{r.plan_type}</td>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>{r.surface}</td>
              <td style={{ border: "1px solid #ccc", padding: "10px" }}>
  <select
    value={r.status}
    onChange={async (e) => {
      const newStatus = e.target.value;

      await supabase
        .from("requests")
        .update({ status: newStatus })
        .eq("id", r.id);

      setRequests((prev) =>
        prev.map((req) =>
          req.id === r.id ? { ...req, status: newStatus } : req
        )
      );
    }}
  >
    <option value="submitted">submitted</option>
    <option value="in_review">in review</option>
    <option value="in_progress">in progress</option>
    <option value="completed">completed</option>
  </select>
</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
