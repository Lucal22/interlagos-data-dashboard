"use client";

import { useRouter, usePathname } from "next/navigation";

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <header className="bg-linear-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-gray-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-2 h-12 bg-linear-to-b from-red-500 to-red-700 rounded-full" />
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Interlagos
            </h1>
            <p className="text-sm text-gray-400 font-light">
              Real-time Dashboard
            </p>
          </div>
        </div>

        {/* Botões de navegação */}
        <div className="flex gap-2 bg-gray-800/50 p-1.5 rounded-lg border border-gray-700">
          <button
            onClick={() => router.push("/")}
            className={`px-5 py-2 rounded-md font-medium text-sm transition-all ${
              pathname === "/"
                ? "bg-white text-gray-900 shadow-md"
                : "text-gray-300 hover:text-white hover:bg-gray-700/50"
            }`}
          >
            Piloto Individual
          </button>
          <button
            onClick={() => router.push("/pilotos")}
            className={`px-5 py-2 rounded-md font-medium text-sm transition-all ${
              pathname === "/pilotos"
                ? "bg-white text-gray-900 shadow-md"
                : "text-gray-300 hover:text-white hover:bg-gray-700/50"
            }`}
          >
            Todos os Pilotos
          </button>
        </div>
      </div>
    </header>
  );
}
