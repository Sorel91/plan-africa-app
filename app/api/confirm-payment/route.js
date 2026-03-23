import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

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
      })
      .eq("id", requestId);

    return Response.json({ success: true });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
