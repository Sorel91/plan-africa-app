import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST(request) {
  try {
    const { formula, requestId } = await request.json();

    let amount = 2900;
    let name = "Essentiel";
    let description = "2 propositions de plans personnalisés";

    if (formula === "standard") {
      amount = 5900;
      name = "Confort";
      description =
        "3 propositions de plans personnalisés + 1 modification incluse";
    }

    if (formula === "premium") {
      amount = 8900;
      name = "Premium";
      description =
        "3 propositions optimisées + visualisation 3D simple + 2 modifications";
    }

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ["card"],

      line_items: [
        {
          price_data: {
            currency: "eur",
            product_data: {
              name,
              description,
            },
            unit_amount: amount,
          },
          quantity: 1,
        },
      ],

      mode: "payment",

      success_url: "https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/success?session_id={CHECKOUT_SESSION_ID}",
      cancel_url: "https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/offers?requestId=${requestId}",

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
