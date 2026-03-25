import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request) {
  try {
    const body = await request.json();
    const { fullName, email, formula, requestId } = body;

    const offerText =
      formula === "basic"
        ? "Basic — 49€"
        : formula === "standard"
        ? "Standard — 79€"
        : formula === "premium"
        ? "Premium — 100€"
        : "une formule adaptée à votre besoin";

    const data = await resend.emails.send({
      from: "Plan Africa <onboarding@resend.dev>",
      to: [email],
      subject: "Relance concernant votre demande Plan Africa",
      html: `
        <h2>Bonjour ${fullName || ""},</h2>
        <p>Nous avons bien reçu votre demande sur Plan Africa.</p>
        <p>Vous pouvez finaliser votre projet en choisissant votre formule ${
          formula ? `<strong>${offerText}</strong>` : ""
        }.</p>
        <p>Si vous avez déjà commencé, il vous suffit de revenir sur le site pour poursuivre.</p>
        <p><a href="https://plan-africa-app-git-v2-nextjs-beydis-projects.vercel.app/offers?requestId=${requestId}">Voir les formules et finaliser</a></p>
        <p>Bien à vous,<br/>Plan Africa</p>
      `,
    });

    return Response.json({ success: true, data });
  } catch (error) {
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}
