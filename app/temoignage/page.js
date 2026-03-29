const testimonials = [
  {
    name: "Amina T.",
    photo: "https://randomuser.me/api/portraits/women/58.jpg",
    city: "Dakar, Senegal",
    project: "Maison familiale R+1",
    quote:
      "Le plan reçu nous a aidés a mieux organiser les pieces avant de lancer les travaux. Nous avons gagne du temps et evite des erreurs couteuses.",
  },
  {
    name: "Koffi A.",
    photo: "https://randomuser.me/api/portraits/men/75.jpg",
    city: "Abidjan, Cote d'Ivoire",
    project: "Villa 3 chambres",
    quote:
      "Le rendu etait clair et facile a partager avec le maitre d'oeuvre. J'ai apprecie la rapidite et les ajustements proposes.",
  },
  {
    name: "Nadia B.",
    photo: "https://randomuser.me/api/portraits/women/44.jpg",
    city: "Casablanca, Maroc",
    project: "Extension d'une maison existante",
    quote:
      "Nous avions besoin d'une vision concrete avant d'investir. La formule choisie nous a permis d'avancer avec plus de confiance.",
  },
  {
    name: "Serigne M.",
    photo: "https://randomuser.me/api/portraits/men/53.jpg",
    city: "Bamako, Mali",
    project: "Duplex moderne",
    quote:
      "Excellent accompagnement du debut a la fin. Les propositions etaient adaptees a notre terrain et a notre budget.",
  },
  {
    name: "Ruth N.",
    photo: "https://randomuser.me/api/portraits/women/67.jpg",
    city: "Lome, Togo",
    project: "Maison compacte 2 chambres",
    quote:
      "J'ai pu comparer les options calmement et choisir la plus pertinente. Le resultat final correspond bien a mon besoin.",
  },
  {
    name: "Yassine K.",
    photo: "https://randomuser.me/api/portraits/men/32.jpg",
    city: "Tunis, Tunisie",
    project: "Plan pour investissement locatif",
    quote:
      "Service professionnel, communication fluide et delais respectes. Je recommande pour lancer un projet sereinement.",
  },
];

export default function TemoignagePage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto max-w-6xl px-6 py-12 lg:px-8 lg:py-16">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            Temoignages
          </span>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Ils ont fait confiance à Planora
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            Decouvrez des retours de clients originaires de plusieurs pays africains
            qui ont utilise Planora pour clarifier leur projet avant construction.
          </p>
        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {testimonials.map((item) => (
            <article
              key={`${item.name}-${item.city}`}
              className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <div className="mb-4 flex items-center gap-3">
                <img
                  src={item.photo}
                  alt={`Photo de ${item.name}`}
                  className="h-12 w-12 rounded-full object-cover"
                  loading="lazy"
                />
                <div>
                  <p className="font-semibold text-slate-900">{item.name}</p>
                  <p className="text-sm text-slate-600">{item.city}</p>
                </div>
              </div>

              <p className="text-sm leading-6 text-slate-700">"{item.quote}"</p>

              <div className="mt-5 border-t border-slate-100 pt-4">
                <p className="mt-1 text-sm text-emerald-700">{item.project}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-12 text-center">
          <a
            href="/prix"
            className="inline-block rounded-xl bg-emerald-600 px-6 py-3 font-semibold text-white transition hover:bg-emerald-700"
          >
            Voir les formules
          </a>
        </div>
      </section>
    </main>
  );
}