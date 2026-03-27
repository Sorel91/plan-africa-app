import { createClient } from "@supabase/supabase-js";
import { Resend } from "resend";

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

const resend = new Resend(process.env.RESEND_API_KEY);

export async function GET() {
  try {
    const now = Date.now();
    const tenMinutesAgo = new Date(now - 10 * 60 * 1000).toISOString();
    const fiveDaysAgo = new Date(now - 5 * 24 * 60 * 60 * 1000).toISOString();

    const { data: requests, error } = await supabase
      .from("requests")
      .select("*")
      .eq("payment_status", "pending");

    if (error) {
      return Response.json(
        { success: false, error: error.message },
        { status: 500 }
      );
    }

    let firstReminderCount = 0;
    let secondReminderCount = 0;

    for (const req of requests || []) {
      if (!req.email) continue;

      const createdAt = req.created_at;

      const shouldSendFirstReminder =
        !req.reminder_sent_at && createdAt <= tenMinutesAgo;

      const shouldSendSecondReminder =
        !req.second_reminder_sent_at && createdAt <= fiveDaysAgo;

      if (shouldSendFirstReminder) {
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
      Nous avons bien reçu votre demande, mais vous n’avez pas encore finalisé votre paiement.
    </p>

    <p style="color:#475569;">
      Vous pouvez reprendre votre projet ici :
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

        await supabase
          .from("requests")
          .update({ reminder_sent_at: new Date().toISOString() })
          .eq("id", req.id);

        firstReminderCount++;
      }

      if (shouldSendSecondReminder) {
        await resend.emails.send({
          from: "Planora <onboarding@resend.dev>",
          to: [req.email],
          subject: "Dernière relance - Finalisez votre projet Planora",
          html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px; text-align:center;">

    <h2 style="color:#059669;">Votre projet est toujours en attente</h2>

    <p style="color:#475569;">
      Bonjour ${req.full_name || ""},
    </p>

    <p style="color:#475569;">
      Votre demande est toujours en attente de paiement.
    </p>

    <p style="color:#475569;">
      Si vous souhaitez recevoir vos plans personnalisés, vous pouvez reprendre votre projet ici :
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

        await supabase
          .from("requests")
          .update({ second_reminder_sent_at: new Date().toISOString() })
          .eq("id", req.id);

        secondReminderCount++;
      }
    }

    return Response.json({
      success: true,
      firstReminderCount,
      secondReminderCount,
    });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}