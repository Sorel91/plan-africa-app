"use client";

import { useEffect, useRef, useState } from "react";

const links = [
  {
    href: "/prix",
    label: "Voir les prix",
    className: "rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white",
  },
  {
    href: "/",
    label: "Accueil",
    className:
      "rounded-xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50",
  },
  {
    href: "/comment-ca-marche",
    label: "Comment ça marche",
    className:
      "rounded-xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50",
  },
  {
    href: "/exemples",
    label: "Exemples",
    className:
      "rounded-xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50",
  },
  {
    href: "/temoignage",
    label: "Temoignages",
    className:
      "rounded-xl px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50",
  },
  {
    href: "/contact",
    label: "Contact",
    className:
      "rounded-xl border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50",
  },
];

export default function MobileMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    function handlePointerDown(event) {
      if (!containerRef.current?.contains(event.target)) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div className="relative md:hidden" ref={containerRef}>
      <button
        type="button"
        aria-expanded={isOpen}
        aria-label={isOpen ? "Fermer le menu" : "Ouvrir le menu"}
        onClick={() => setIsOpen((open) => !open)}
        className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-900 shadow-sm"
      >
        <span className="flex flex-col gap-1">
          <span className="block h-0.5 w-4 rounded-full bg-slate-700" />
          <span className="block h-0.5 w-4 rounded-full bg-slate-700" />
          <span className="block h-0.5 w-4 rounded-full bg-slate-700" />
        </span>
      </button>

      {isOpen ? (
        <nav className="absolute left-0 top-full z-50 mt-2 flex w-72 max-w-[calc(100vw-3rem)] flex-col gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-lg">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={link.className}
              onClick={() => setIsOpen(false)}
            >
              {link.label}
            </a>
          ))}
        </nav>
      ) : null}
    </div>
  );
}