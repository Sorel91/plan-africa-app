import { createClient } from "@supabase/supabase-js";
import { Resend } from "resend";

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

const resend = new Resend(process.env.RESEND_API_KEY);

export async function GET() {
  try {
    const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000).toISOString();

    const { data: requests, error } = await supabase
      .from("requests")
      .select("*")
      .eq("payment_status", "pending")
      .is("reminder_sent_at", null)
      .lte("created_at", tenMinutesAgo);

    if (error) {
      return Response.json({ success: false, error: error.message }, { status: 500 });
    }

    for (const request of requests || []) {
      await resend.emails.send({
        from: "Plan Africa <onboarding@resend.dev>",
        to: [request.email],
        subject: "Finalisez votre demande Plan Africa",
        html: `
          <h2>Bonjour ${request.full_name || ""},</h2>
          <p>Nous avons bien reçu votre demande de plan.</p>
          <p>Vous pouvez maintenant choisir votre formule et finaliser votre paiement :</p>
          <p><a href="https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/">Voir les formules et finaliser</a></p>
          <p>Bien à vous,<br/>Plan Africa</p>
        `,
      });

      await supabase
        .from("requests")
        .update({ reminder_sent_at: new Date().toISOString() })
        .eq("id", request.id);
    }

    return Response.json({ success: true, count: requests?.length || 0 });
  } catch (error) {
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}
