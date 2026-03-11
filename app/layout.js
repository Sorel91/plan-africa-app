export const metadata = {
  title: "Plan Africa",
  description: "Application de demande de plans 2D et 3D",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
