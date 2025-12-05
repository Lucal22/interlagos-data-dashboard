export interface Curva {
  curva: number;
  tempo: number;
  pneus: {
    "temperaturas(°C)": Record<string, number>;
    "pressao(psi)": Record<string, number>;
    rpm: number;
  };
}

interface Voltas {
  [volta: string]: Curva[];
}

export interface Piloto {
  piloto: string;
  equipe: string;
  voltas: Voltas;
}

export interface Corrida {
  _id: string;
  id_corrida: number;
  inicio: number;
  pilotos: Piloto[];
}

export interface CorridaPiloto {
  id_corrida: number;
  inicio: number;
  piloto: Piloto;
}

export interface CorridaTime {
  id_corrida: number;
  inicio: number;
  pilotos: Piloto[];
}

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

export interface PilotoComUltimaCurva {
  piloto: string;
  equipe: string;
  ultimaCurva: Curva | null;
  volta: string;
}
