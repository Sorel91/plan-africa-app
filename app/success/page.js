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
      return Response.json({
        success: false,
        error: "Payment not completed",
      }, { status: 400 });
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

    // 1. Lire la demande existante
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

    // 2. Si déjà payée, on ne refait rien
    if (existingRequest.payment_status === "paid") {
      return Response.json({
        success: true,
        alreadyConfirmed: true,
      });
    }

    // 3. Mettre à jour la demande une seule fois
    const { error: updateError } = await supabase
      .from("requests")
      .update({
        payment_status: "paid",
        formula: formula || existingRequest.formula,
        payment_confirmed_at: new Date().toISOString(),
      })
      .eq("id", requestId);

    if (updateError) {
      return Response.json(
        { success: false, error: updateError.message },
        { status: 500 }
      );
    }

    // 4. Envoyer l'email une seule fois
    if (existingRequest.email) {
      const formulaLabel =
        formula === "basic"
          ? "Essentiel"
          : formula === "standard"
          ? "Confort"
          : formula === "premium"
          ? "Premium"
          : existingRequest.formula || "Formule choisie";

      await resend.emails.send({
        from: "Planora <onboarding@resend.dev>",
        to: [existingRequest.email],
        subject: "Paiement confirmé - Planora",
        html: `
          <h2>Bonjour ${existingRequest.full_name || ""},</h2>
          <p>Nous avons bien reçu votre paiement.</p>
          <p><strong>Formule choisie :</strong> ${formulaLabel}</p>
          <p>Votre demande est maintenant prise en compte et sera traitée dans les meilleurs délais.</p>
          <p>Bien à vous,<br/>Planora</p>
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