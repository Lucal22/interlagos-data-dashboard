import clientPromise from "@/libs/mongodb";

export async function GET(req: Request) {
  const encoder = new TextEncoder();

  const client = await clientPromise;
  const db = client.db("f1");
  const corridas = db.collection("corridas");

  const url = new URL(req.url);
  const pilotoFilter = url.searchParams.get("piloto");

  return new Response(
    new ReadableStream({
      async start(controller) {
        async function sendUpdate() {
          try {
            // Busca a última corrida criada
            const allRaces = await corridas
              .find({})
              .sort({ id_corrida: -1 })
              .limit(1)
              .toArray();

            let races = allRaces;

            // Log para debug
            if (allRaces.length > 0) {
              console.log(
                `[Realtime API] Corrida ${allRaces[0].id_corrida} tem ${
                  allRaces[0].pilotos?.length || 0
                } pilotos`
              );
            }

            if (pilotoFilter) {
              races = allRaces.map((race) => {
                const filteredPilotos = (race.pilotos || []).filter(
                  (p: Record<string, unknown>) => p.piloto === pilotoFilter
                );
                return { ...race, pilotos: filteredPilotos };
              });
            }

            const payload = JSON.stringify(races);
            controller.enqueue(encoder.encode(`data: ${payload}\n\n`));
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
          } catch (err) {
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ error: true })}\n\n`)
            );
          }
        }

        // Envia imediatamente
        await sendUpdate();

        // Continua enviando a cada X ms
        const interval = setInterval(sendUpdate, 100);

        return () => clearInterval(interval);
      },
    }),
    {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    }
  );
}
