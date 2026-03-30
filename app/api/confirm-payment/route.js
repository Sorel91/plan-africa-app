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

    if (!sessionId) {
      return Response.json(
        { success: false, error: "Missing sessionId" },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.retrieve(sessionId);

    if (session.payment_status !== "paid") {
      return Response.json(
        { success: false, error: "Payment not completed" },
        { status: 400 }
      );
    }

    const requestId =
      session.client_reference_id || session.metadata?.requestId || null;

    const formula = session.metadata?.formula || null;

    if (!requestId) {
      return Response.json(
        { success: false, error: "Missing requestId in Stripe session" },
        { status: 400 }
      );
    }

    const { data: existingRequest, error: fetchError } = await supabase
      .from("requests")
      .select("*")
      .eq("id", requestId)
      .single();

    if (fetchError || !existingRequest) {
      return Response.json(
        { success: false, error: "Request not found" },
        { status: 404 }
      );
    }

    // Si le paiement a déjà été confirmé, on ne refait rien
    if (existingRequest.payment_status === "paid") {
      return Response.json({
        success: true,
        alreadyConfirmed: true,
      });
    }

    const finalFormula = formula || existingRequest.formula || null;

    const { error: updateError } = await supabase
      .from("requests")
      .update({
        payment_status: "paid",
        formula: finalFormula,
        payment_confirmed_at: new Date().toISOString(),
      })
      .eq("id", requestId);

    if (updateError) {
      return Response.json(
        { success: false, error: updateError.message },
        { status: 500 }
      );
    }

    const formulaLabel =
      finalFormula === "basic"
        ? "Essentiel"
        : finalFormula === "standard"
        ? "Confort"
        : finalFormula === "premium"
        ? "Premium"
        : "Formule sélectionnée";

    if (existingRequest.email) {
      await resend.emails.send({
        from: "Planora <contact@planora.immo>",
        reply_to: "beydi.sangare@gmail.com",
        to: [existingRequest.email],
        subject: "Paiement confirmé - Planora",
        html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px; text-align:center;">

    <h2 style="color:#059669;">✅ Paiement confirmé</h2>

    <p style="color:#475569;">
      Bonjour ${existingRequest.full_name || ""},
    </p>

    <p style="color:#475569;">
      Nous avons bien reçu votre paiement.
    </p>

    <div style="margin:20px 0; padding:15px; background:#ecfdf5; border-radius:8px;">
      <strong>Formule choisie :</strong><br/>
      ${formulaLabel}
    </div>

    <p style="color:#475569;">
      Votre demande est maintenant en cours de traitement.
    </p>

    <p style="margin-top:20px; color:#475569;">
      Nous reviendrons vers vous rapidement.
    </p>

    <a
      href="https://planora.immo"
      style="display:inline-block; margin-top:20px; background:#059669; color:white; padding:10px 20px; border-radius:8px; text-decoration:none;"
    >
      Retour au site
    </a>

    <p style="margin-top:30px; font-size:12px; color:#94a3b8;">
      Planora — Conception de plans personnalisés
    </p>

  </div>
</div>
`,
      });
    }

    return Response.json({
      success: true,
      alreadyConfirmed: false,
    });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}