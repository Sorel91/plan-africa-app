import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request) {
  try {
    const {
      fullName,
      email,
      country,
      houseType,
      bedrooms,
      surface,
      budget,
      description,
      formula,
    } = await request.json();

    const formulaLabel =
      formula === "basic"
        ? "Essentiel"
        : formula === "standard"
        ? "Confort"
        : formula === "premium"
        ? "Premium"
        : "Non sélectionnée";

    await resend.emails.send({
      from: "Planora <contact@planora.immo>",
      to: ["beydi.sangare.gmail.com"], // ← remplace par ton email perso

      subject: "Nouvelle demande client - Planora",

      html: `
<div style="font-family: Arial, sans-serif; background:#f8fafc; padding:20px;">
  <div style="max-width:600px; margin:0 auto; background:white; border-radius:12px; padding:20px;">

    <h2 style="color:#059669; margin-bottom:10px;">
      📩 Nouvelle demande - Planora
    </h2>

    <p style="color:#475569;">
      Un nouveau client a soumis une demande.
    </p>

    <hr style="margin:20px 0;" />

    <h3 style="margin-bottom:10px;">Informations client</h3>

    <p><strong>Nom :</strong> ${fullName}</p>
    <p><strong>Email :</strong> ${email}</p>
    <p><strong>Lieu :</strong> ${country}</p>
    <p><strong>Type de maison :</strong> ${houseType}</p>
    <p><strong>Chambres :</strong> ${bedrooms}</p>
    <p><strong>Surface :</strong> ${surface || "-"}</p>
    <p><strong>Budget :</strong> ${budget || "-"}</p>
    <p><strong>Formule :</strong> ${formulaLabel}</p>

    <hr style="margin:20px 0;" />

    <h3>Description du projet</h3>

    <p style="white-space:pre-line; color:#334155;">
      ${description}
    </p>

    <hr style="margin:20px 0;" />

    <p style="font-size:12px; color:#94a3b8;">
      Planora — Demandes clients
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