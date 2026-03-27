import { Resend } from "resend";
import { createClient } from "@supabase/supabase-js";

const resend = new Resend(process.env.RESEND_API_KEY);

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

export async function POST() {
  try {
    const { data: requests } = await supabase
      .from("requests")
      .select("*")
      .eq("payment_status", "pending");

    for (const req of requests || []) {
      if (!req.email) continue;

      await resend.emails.send({
        from: "Planora <onboarding@resend.dev>",
        to: [req.email],
        subject: "Finalisez votre projet - Planora",
        html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px; text-align:center;">

    <h2 style="color:#059669;">Votre projet vous attend</h2>

    <p style="color:#475569;">
      Bonjour ${req.full_name || ""},
    </p>

    <p style="color:#475569;">
      Votre demande est toujours en attente. Finalisez votre choix pour recevoir vos plans personnalisés.
    </p>

    <a
      href="https://planora.immo/offers?requestId=${req.id}"
      style="display:inline-block; margin-top:20px; background:#059669; color:white; padding:10px 20px; border-radius:8px; text-decoration:none;"
    >
      Continuer mon projet
    </a>

    <p style="margin-top:20px; font-size:12px; color:#94a3b8;">
      Planora — Conception de plans personnalisés
    </p>

  </div>
</div>
`,
      });
    }

    return Response.json({ success: true });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}