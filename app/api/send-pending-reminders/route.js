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
      return Response.json({ success: false, error: error.message }, { status: 500 });
    }

    let firstReminderCount = 0;
    let secondReminderCount = 0;

    for (const request of requests || []) {
      const createdAt = request.created_at;

      const shouldSendFirstReminder =
        !request.reminder_sent_at &&
        createdAt <= tenMinutesAgo;

      const shouldSendSecondReminder =
        !request.second_reminder_sent_at &&
        createdAt <= fiveDaysAgo;

      if (shouldSendFirstReminder) {
        await resend.emails.send({
          from: "Plan Africa <onboarding@resend.dev>",
          to: [request.email],
          subject: "Finalisez votre demande Plan Africa",
          html: `
            <h2>Bonjour ${request.full_name || ""},</h2>
            <p>Nous avons bien reçu votre demande de plan.</p>
            <p>Vous pouvez maintenant choisir votre formule et finaliser votre paiement :</p>
            <p><a href="https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/offers?requestId=${request.id}">Voir les formules et finaliser</a></p>
            <p>Bien à vous,<br/>Plan Africa</p>
          `,
        });

        await supabase
          .from("requests")
          .update({ reminder_sent_at: new Date().toISOString() })
          .eq("id", request.id);

        firstReminderCount++;
      }

      if (shouldSendSecondReminder) {
        await resend.emails.send({
          from: "Plan Africa <onboarding@resend.dev>",
          to: [request.email],
          subject: "Dernière relance - finalisez votre demande Plan Africa",
          html: `
            <h2>Bonjour ${request.full_name || ""},</h2>
            <p>Votre demande est toujours en attente de paiement.</p>
            <p>Si vous souhaitez recevoir votre plan, vous pouvez finaliser votre commande ici :</p>
            <p><a href="https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/offers?requestId=${request.id}">Choisir une formule et payer</a></p>
            <p>Bien à vous,<br/>Plan Africa</p>
          `,
        });

        await supabase
          .from("requests")
          .update({ second_reminder_sent_at: new Date().toISOString() })
          .eq("id", request.id);

        secondReminderCount++;
      }
    }

    return Response.json({
      success: true,
      firstReminderCount,
      secondReminderCount,
    });
  } catch (error) {
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}
