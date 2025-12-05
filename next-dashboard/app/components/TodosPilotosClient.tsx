"use client";

import { useEffect, useState } from "react";
import { streamTodosPilotos } from "@/libs/api";
import type { Piloto, Curva, PilotoComUltimaCurva } from "@/context/interface";
import { pilotos as listaPilotos } from "@/utils/pilotos";

export default function TodosPilotosClient() {
  // Inicializa com todos os 24 pilotos sem dados
  const [pilotos, setPilotos] = useState<PilotoComUltimaCurva[]>(
    listaPilotos.map((nome) => ({
      piloto: nome,
      equipe: "",
      ultimaCurva: null,
      volta: "",
    }))
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stop = streamTodosPilotos((pilotosData: Piloto[]) => {
      console.log(
        `[TodosPilotos] Recebidos ${pilotosData.length} pilotos:`,
        pilotosData.map((p) => p.piloto)
      );

      // Ignora updates vazios
      if (pilotosData.length === 0) {
        return;
      }

      // Para cada piloto, pega a última curva da última volta
      const pilotosComUltimaCurva = pilotosData.map((p) => {
        const voltas = p.voltas || {};
        const voltasOrdenadas = Object.keys(voltas).sort(
          (a, b) => parseInt(b) - parseInt(a)
        );

        let ultimaCurva: Curva | null = null;
        let voltaAtual = "";

        if (voltasOrdenadas.length > 0) {
          voltaAtual = voltasOrdenadas[0];
          const curvas = voltas[voltaAtual];
          if (curvas && curvas.length > 0) {
            ultimaCurva = curvas[curvas.length - 1]; // última curva da última volta
          }
        }

        return {
          piloto: p.piloto,
          equipe: p.equipe,
          ultimaCurva,
          volta: voltaAtual,
        };
      });

      // Atualiza apenas os pilotos que receberam dados
      setPilotos((prev) => {
        const pilotosMap = new Map(prev.map((p) => [p.piloto, p]));

        pilotosComUltimaCurva.forEach((p) => {
          pilotosMap.set(p.piloto, p);
        });

        return Array.from(pilotosMap.values());
      });

      setLoading(false);
    });

    return () => {
      if (stop) stop();
    };
  }, []);

  if (loading) return <div className="p-4">Carregando pilotos...</div>;

  return (
    <section className="p-4">
      <h3 className="text-xl font-bold mb-4">
        Todos os Pilotos - Última Curva
      </h3>

      <div className="grid grid-cols-5 gap-3">
        {pilotos.map((p) => (
          <div
            key={p.piloto}
            className="group bg-white rounded-md p-3 border border-gray-200 
                shadow-sm transition-all duration-200 cursor-pointer
                hover:shadow-md hover:-translate-y-0.5"
          >
            {/* Prévia */}
            <div className="group-hover:hidden">
              <p className="text-sm font-bold text-gray-800">{p.piloto}</p>
              <p className="text-xs text-gray-500 mb-2">{p.equipe}</p>
              {p.ultimaCurva ? (
                <>
                  <p className="text-sm font-medium text-gray-700">
                    Volta {p.volta} - Curva {p.ultimaCurva.curva}
                  </p>
                  <p className="text-xs text-gray-500">
                    Tempo: {p.ultimaCurva.tempo}s
                  </p>
                </>
              ) : (
                <p className="text-xs text-gray-400">Aguardando dados...</p>
              )}
            </div>

            {/* Detalhes no hover */}
            {p.ultimaCurva && (
              <div className="hidden group-hover:block text-[12px] animate-fadeIn">
                <p className="font-bold text-gray-800 mb-1">{p.piloto}</p>
                <p className="text-[10px] text-gray-500 mb-2">
                  Volta {p.volta} - Curva {p.ultimaCurva.curva}
                </p>
                <div className="grid grid-cols-2 gap-1 text-gray-700">
                  <p>
                    DD:{" "}
                    {
                      p.ultimaCurva.pneus["temperaturas(°C)"][
                        "Dianteira direita"
                      ]
                    }
                    °C/
                    {p.ultimaCurva.pneus["pressao(psi)"]["Dianteira direita"]}
                    psi
                  </p>
                  <p>
                    DE:{" "}
                    {
                      p.ultimaCurva.pneus["temperaturas(°C)"][
                        "Dianteira esquerda"
                      ]
                    }
                    °C/
                    {p.ultimaCurva.pneus["pressao(psi)"]["Dianteira esquerda"]}
                    psi
                  </p>
                  <p>
                    TD:{" "}
                    {
                      p.ultimaCurva.pneus["temperaturas(°C)"][
                        "Traseira direita"
                      ]
                    }
                    °C/
                    {p.ultimaCurva.pneus["pressao(psi)"]["Traseira direita"]}psi
                  </p>
                  <p>
                    TE:{" "}
                    {
                      p.ultimaCurva.pneus["temperaturas(°C)"][
                        "Traseira esquerda"
                      ]
                    }
                    °C/
                    {p.ultimaCurva.pneus["pressao(psi)"]["Traseira esquerda"]}
                    psi
                  </p>
                </div>
                <p className="font-medium mt-2">
                  {p.ultimaCurva.pneus.rpm} RPM
                </p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
