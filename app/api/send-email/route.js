import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request) {
  try {
    const body = await request.json();

    const { fullName, email, country, planType, surface, description } = body;

    const data = await resend.emails.send({
      from: "Plan Africa <onboarding@resend.dev>",
      to: ["TON_EMAIL"],
      subject: "Nouvelle demande Plan Africa",
      html: `
        <h2>Nouvelle demande reçue</h2>
        <p><strong>Nom :</strong> ${fullName}</p>
        <p><strong>Email :</strong> ${email}</p>
        <p><strong>Pays :</strong> ${country}</p>
        <p><strong>Type de plan :</strong> ${planType}</p>
        <p><strong>Surface :</strong> ${surface}</p>
        <p><strong>Description :</strong> ${description}</p>
      `,
    });

    return Response.json({ success: true, data });
  } catch (error) {
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}
