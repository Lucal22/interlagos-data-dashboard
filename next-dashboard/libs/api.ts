/**
 * Funções de request para as APIs de corridas, pilotos e times
 */

export type {
  Piloto,
  Corrida,
  CorridaPiloto,
  CorridaTime,
} from "@/context/interface";

import type { Piloto, Corrida } from "@/context/interface";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000/api";

/**
 * Busca todas as corridas com filtros opcionais
 * @param piloto - Filtrar por piloto
 */

export async function fetchCorridas(piloto?: string): Promise<Corrida[]> {
  const params = new URLSearchParams();
  if (piloto) {
    params.append("piloto", piloto);
  }

  const url = `${API_BASE}/corridas${
    params.toString() ? `?${params.toString()}` : ""
  }`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Erro ao buscar corridas: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchPiloto(piloto: string): Promise<Piloto> {
  const races = await fetchCorridas(piloto);
  const race = races[0];
  if (!race) {
    throw new Error(`Nenhuma corrida encontrada`);
  }

  // A API já filtra pelo piloto, retorna o primeiro
  const pilotoData = race.pilotos[0];

  if (!pilotoData) {
    throw new Error(`Piloto ${piloto} não encontrado na corrida`);
  }
  return pilotoData as Piloto;
}

//export async function fetchPilotoAtual(piloto: string): Promise<Piloto> {}

export function streamPiloto(
  piloto: string,
  onData: (pilotoData: Piloto) => void
) {
  const params = new URLSearchParams();
  params.append("piloto", piloto); // filtro pelo piloto específico

  const url = `${API_BASE}/corridas/realtime?${params.toString()}`;

  const es = new EventSource(url);

  es.onmessage = (event) => {
    const races: Corrida[] = JSON.parse(event.data);

    if (!races.length) return;

    const race = races[0];

    if (!race || !race.pilotos) return;

    const pilotoData = race.pilotos.find((p) => p.piloto === piloto);

    if (pilotoData) {
      onData(pilotoData as Piloto);
    }
  };

  es.onerror = (err) => {
    console.error("SSE error piloto andamento:", err);
    es.close();
  };

  return () => es.close();
}

export function streamCorridas(
  piloto?: string,
  onData?: (corridas: Corrida[]) => void
) {
  const params = new URLSearchParams();
  if (piloto) params.append("piloto", piloto);

  const url = `${API_BASE}/corridas/realtime${
    params.toString() ? `?${params.toString()}` : ""
  }`;

  const es = new EventSource(url);

  es.onmessage = (event) => {
    const data: Corrida[] = JSON.parse(event.data);
    if (onData) onData(data);
  };

  es.onerror = (err) => {
    console.error("SSE error:", err);
    es.close();
  };

  return () => es.close(); // close SSE when component unmounts
}

/**
 * Busca dados de um piloto em corridas em andamento
 */

/**
 * Busca todas as corridas
 */
export async function fetchTodasCorridas(): Promise<Corrida[]> {
  return fetchCorridas();
}

/**
 * Stream de todos os pilotos da última corrida
 */
export function streamTodosPilotos(onData: (pilotos: Piloto[]) => void) {
  const url = `${API_BASE}/corridas/realtime`;
  const es = new EventSource(url);

  es.onmessage = (event) => {
    const races: Corrida[] = JSON.parse(event.data);
    if (races.length && races[0].pilotos) {
      onData(races[0].pilotos);
    }
  };

  es.onerror = (err) => {
    console.error("SSE error todos pilotos:", err);
    es.close();
  };

  return () => es.close();
}
