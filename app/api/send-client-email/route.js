import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request) {
  try {
    const {
      fullName,
      email,
      requestId,
    } = await request.json();

    if (!email || !requestId) {
      return Response.json(
        { success: false, error: "Missing email or requestId" },
        { status: 400 }
      );
    }

    await resend.emails.send({
      from: "Planora <contact@planora.immo>",
      to: [email],
      subject: "Votre projet Planora est prêt",

      html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px; text-align:center;">

    <h2 style="color:#059669;">Votre projet Planora</h2>

    <p style="color:#475569;">
      Bonjour ${fullName || ""},
    </p>

    <p style="color:#475569;">
      Nous avons bien reçu votre demande.
    </p>

    <p style="color:#475569;">
      Vous pouvez maintenant découvrir les offres adaptées à votre projet et finaliser votre demande.
    </p>

    <a
      href="https://planora.immo/offers?requestId=${requestId}"
      style="display:inline-block; margin-top:20px; background:#059669; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:600;"
    >
      Voir les offres
    </a>

    <p style="margin-top:20px; color:#475569;">
      Vous pouvez revenir à tout moment pour reprendre votre projet.
    </p>

    <p style="margin-top:30px; font-size:12px; color:#94a3b8;">
      Planora — Conception de plans personnalisés
    </p>

  </div>
</div>
`,
    });

    return Response.json({ success: true });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}