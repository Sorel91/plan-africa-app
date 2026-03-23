import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";
import { Resend } from "resend";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const resend = new Resend(process.env.RESEND_API_KEY);

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

export async function POST(request) {
  try {
    const { sessionId } = await request.json();

    const session = await stripe.checkout.sessions.retrieve(sessionId);

    const requestId = session.client_reference_id;
    const formula = session.metadata.formula;

    await supabase
      .from("requests")
     .update({
  payment_status: "paid",
  formula: formula,
  payment_confirmed_at: new Date().toISOString(),
})
      .eq("id", requestId);
    const { data: requestData } = await supabase
  .from("requests")
  .select("*")
  .eq("id", requestId)
  .single();

if (requestData?.email) {
  await resend.emails.send({
    from: "Plan Africa <onboarding@resend.dev>",
    to: [requestData.email],
    subject: "Paiement confirmé - Plan Africa",
    html: `
      <h2>Bonjour ${requestData.full_name || ""},</h2>
      <p>Nous avons bien reçu votre paiement.</p>
      <p><strong>Formule choisie :</strong> ${formula}</p>
      <p>Votre demande est maintenant prise en compte et sera traitée dans les meilleurs délais.</p>
      <p>Bien à vous,<br/>Plan Africa</p>
    `,
  });
}

    return Response.json({ success: true });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
