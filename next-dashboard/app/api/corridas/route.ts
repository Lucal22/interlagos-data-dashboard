import clientPromise from "@/libs/mongodb";

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const pilotoFilter = url.searchParams.get("piloto");

    const client = await clientPromise;
    const db = client.db("f1");
    const corridas = db.collection("corridas");

    // Busca a última corrida criada (maior id_corrida)
    const allRaces = await corridas.find({}).sort({ id_corrida: -1 }).toArray();

    // If piloto filter is provided, filter pilots within each race
    if (pilotoFilter) {
      return Response.json(
        allRaces.map((race) => {
          const filteredPilotos = (race.pilotos || []).filter(
            (p: Record<string, unknown>) => p.piloto === pilotoFilter
          );
          return { ...race, pilotos: filteredPilotos };
        })
      );
    }

    return Response.json(allRaces);
  } catch (error) {
    console.error("Erro ao buscar corridas:", error);
    return Response.json({ error: "Erro interno" }, { status: 500 });
  }
}
