import { Resend } from "resend";
import { createClient } from "@supabase/supabase-js";

const resend = new Resend(process.env.RESEND_API_KEY);

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

export async function POST(request) {
  try {
    const { requestId } = await request.json();

    const { data: req } = await supabase
      .from("requests")
      .select("*")
      .eq("id", requestId)
      .single();

    if (!req || !req.email) {
      return Response.json({ success: false });
    }

    await resend.emails.send({
      from: "Planora <contact@planora.immo>",
      to: [req.email],
      subject: "Votre projet avance - Planora",
      html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px; text-align:center;">

    <h2 style="color:#059669;">Votre projet est toujours en attente</h2>

    <p style="color:#475569;">
      Bonjour ${req.full_name || ""},
    </p>

    <p style="color:#475569;">
      Vous avez commencé une demande sur Planora, mais vous n’avez pas encore finalisé votre choix.
    </p>

    <p style="margin-top:10px;">
      Vous pouvez reprendre votre projet à tout moment :
    </p>

    <a
      href="https://planora.immo/offers?requestId=${req.id}"
      style="display:inline-block; margin-top:20px; background:#059669; color:white; padding:10px 20px; border-radius:8px; text-decoration:none;"
    >
      Reprendre mon projet
    </a>

    <p style="margin-top:20px; font-size:12px; color:#94a3b8;">
      Planora — Conception de plans personnalisés
    </p>

  </div>
</div>
`,
    });

    return Response.json({ success: true });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}