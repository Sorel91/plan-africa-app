import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST() {
  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      payment_method_types: ["card"],
      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name: "Plan Express 2D",
              description: "Plan low-cost avec livraison rapide",
            },
            unit_amount: 4900,
          },
          quantity: 1,
        },
      ],
      success_url: "https://TON-DOMAINE/success",
      cancel_url: "https://TON-DOMAINE/cancel",
    });

    return Response.json({ url: session.url });
  } catch (error) {
    return Response.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
