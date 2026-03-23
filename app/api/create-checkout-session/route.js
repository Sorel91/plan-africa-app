import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST(request) {
  try {
    const { formula, requestId } = await request.json();

    let amount = 4900;
    let name = "Plan Express Basic";

    if (formula === "standard") {
      amount = 7900;
      name = "Plan Express Standard";
    }

    if (formula === "premium") {
      amount = 10000;
      name = "Plan Express Premium";
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      payment_method_types: ["card"],
      client_reference_id: requestId,
      metadata: {
        formula: formula,
      },
      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name,
            },
            unit_amount: amount,
          },
          quantity: 1,
        },
      ],
      success_url: `https://TON-DOMAINE/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: "https://TON-DOMAINE/cancel",
    });

    return Response.json({ url: session.url });
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
