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

    const data = await resend.emails.send({
      from: "Plan Africa <onboarding@resend.dev>",
      to: ["TON_EMAIL"],
      subject: "Nouvelle demande Plan Africa",
      html: `
        <h2>Nouvelle demande reçue</h2>

        <p><strong>Nom :</strong> ${fullName || "-"}</p>
        <p><strong>Email :</strong> ${email || "-"}</p>
        <p><strong>Lieu du projet :</strong> ${country || "-"}</p>
        <p><strong>Type de maison :</strong> ${houseType || "-"}</p>
        <p><strong>Nombre de chambres :</strong> ${bedrooms || "-"}</p>
        <p><strong>Surface :</strong> ${surface || "-"}</p>
        <p><strong>Budget :</strong> ${budget || "-"}</p>
        <p><strong>Formule :</strong> ${formulaLabel}</p>

        <p><strong>Description :</strong></p>
        <p>${description || "-"}</p>
      `,
    });

    return Response.json({ success: true, data });
  } catch (error) {
    return Response.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}