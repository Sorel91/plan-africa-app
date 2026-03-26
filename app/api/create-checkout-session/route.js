import Stripe from "stripe";
import { createClient } from "@supabase/supabase-js";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

const supabase = createClient(
  "https://btschxgghvblmohddqcj.supabase.co",
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

export async function POST(request) {
  try {
    const { formula, requestId } = await request.json();

    const baseUrl =
      process.env.NEXT_PUBLIC_BASE_URL || "https://planora.immo";

    const { data: pricing, error: pricingError } = await supabase
      .from("pricing")
      .select("*")
      .eq("formula", formula)
      .single();

    if (pricingError || !pricing) {
      return Response.json(
        { error: "Pricing not found" },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      payment_method_types: ["card"],
      client_reference_id: requestId || "",

      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name: pricing.label,
              description: pricing.description || "",
            },
            unit_amount: pricing.amount,
          },
          quantity: 1,
        },
      ],

      success_url: `${baseUrl}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/prix`,

      metadata: {
        requestId: requestId || "",
        formula: formula || "",
      },
    });

    return Response.json({ url: session.url });
  } catch (error) {
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}