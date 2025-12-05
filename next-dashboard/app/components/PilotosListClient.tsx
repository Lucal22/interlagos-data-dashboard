"use client";

import { useEffect, useState } from "react";
import { fetchPiloto, streamPiloto } from "@/libs/api";
import type { Piloto } from "@/context/interface";
import { pilotos } from "@/utils/pilotos";

export default function PilotoClient() {
  const [piloto, setPiloto] = useState<Piloto>();
  const [loading, setLoading] = useState(true);
  const [pilotoSelecionado, setPilotoSelecionado] = useState("Oscar Piastri");

  useEffect(() => {
    let stop: (() => void) | undefined;
    let isMounted = true;

    async function initPiloto() {
      setLoading(true);
      setPiloto(undefined); // Limpa o piloto anterior

      try {
        const dadosIniciais = await fetchPiloto(pilotoSelecionado);
        if (isMounted) {
          setPiloto(dadosIniciais);
        }

        stop = streamPiloto(pilotoSelecionado, (pilotoAtualizado) => {
          if (isMounted) {
            console.log(
              `[PilotoClient] Update ${pilotoSelecionado}:`,
              Object.keys(pilotoAtualizado.voltas || {}).length,
              "voltas"
            );
            setPiloto(pilotoAtualizado);
          }
        });
      } catch (err) {
        console.error(
          `[PilotoClient] Erro ao buscar ${pilotoSelecionado}:`,
          err
        );
        // Tenta fazer stream mesmo sem dados iniciais
        stop = streamPiloto(pilotoSelecionado, (pilotoAtualizado) => {
          if (isMounted) {
            console.log(
              `[PilotoClient] Update ${pilotoSelecionado}:`,
              Object.keys(pilotoAtualizado.voltas || {}).length,
              "voltas"
            );
            setPiloto(pilotoAtualizado);
            setLoading(false);
          }
        });
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    initPiloto();

    return () => {
      isMounted = false;
      if (stop) stop();
    };
  }, [pilotoSelecionado]);

  if (loading) return <div>Carregando piloto {pilotoSelecionado}...</div>;
  if (!piloto) return <div>Aguardando dados de {pilotoSelecionado}...</div>;
  if (!piloto) return <div>Nenhum piloto encontrado</div>;

  return (
    <section className="p-4">
      <div className="flex items-center gap-4 mb-4">
        <h3 className="text-xl font-bold">Piloto:</h3>
        <select
          value={pilotoSelecionado}
          onChange={(e) => setPilotoSelecionado(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     hover:border-gray-400 transition-colors cursor-pointer"
        >
          {pilotos.map((nome) => (
            <option key={nome} value={nome}>
              {nome}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-5 gap-3">
        {piloto &&
          Object.entries(piloto.voltas).map(([numVolta, curvas]) => (
            <div
              key={numVolta}
              className="bg-gray-50 p-2 rounded-lg border border-gray-200 shadow-sm"
            >
              <h4 className="text-center font-semibold text-gray-800 mb-3">
                Volta {numVolta}
              </h4>

              <div className="grid grid-cols-1 gap-2">
                {curvas
                  .sort((a, b) => a.curva - b.curva)
                  .map((curva, index) => (
                    <div
                      key={index}
                      className="group bg-white rounded-md p-3 border border-gray-200 
                shadow-sm transition-all duration-200 cursor-pointer
                hover:shadow-md hover:-translate-y-0.5"
                    >
                      <div className="group-hover:hidden">
                        <p className="text-sm font-medium text-gray-700">
                          Curva {curva.curva}
                        </p>
                        <p className="text-xs text-gray-500">
                          Tempo — {curva.tempo}s
                        </p>
                      </div>

                      <div className="hidden group-hover:block text-[12px] animate-fadeIn">
                        <div className="grid grid-cols-2 gap-1 text-gray-700">
                          <p>
                            DD:{" "}
                            {
                              curva.pneus["temperaturas(°C)"][
                                "Dianteira direita"
                              ]
                            }
                            °C/
                            {curva.pneus["pressao(psi)"]["Dianteira direita"]}
                            psi
                          </p>
                          <p>
                            DE:{" "}
                            {
                              curva.pneus["temperaturas(°C)"][
                                "Dianteira esquerda"
                              ]
                            }
                            °C/
                            {curva.pneus["pressao(psi)"]["Dianteira esquerda"]}
                            psi
                          </p>
                          <p>
                            TD:{" "}
                            {
                              curva.pneus["temperaturas(°C)"][
                                "Traseira direita"
                              ]
                            }
                            °C/
                            {curva.pneus["pressao(psi)"]["Traseira direita"]}psi
                          </p>
                          <p>
                            TE:{" "}
                            {
                              curva.pneus["temperaturas(°C)"][
                                "Traseira esquerda"
                              ]
                            }
                            °C/
                            {curva.pneus["pressao(psi)"]["Traseira esquerda"]}
                            psi
                          </p>
                        </div>
                        <p className="font-medium mt-2">
                          {curva.pneus["rpm"]}RPM
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
      </div>
    </section>
  );
}
