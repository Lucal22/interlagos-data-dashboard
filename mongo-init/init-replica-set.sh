#!/bin/bash
set -e

echo "Aguardando MongoDB (mongo1) estar pronto..."

# Aguarda até que mongo1 responda ao ping
until mongosh "mongodb://mongo1:27017" --eval "db.adminCommand('ping')" 2>/dev/null | grep -q "ok"; do
  echo "Mongo1 ainda não está pronto... aguardando 2s"
  sleep 2
done

echo "Mongo1 está pronto. Inicializando Replica Set rs0 (se necessário)..."

# Tentativa de iniciar o replset apenas se ainda não houver config
mongosh "mongodb://mongo1:27017" --eval '
try {
  cfg = rs.conf();
  print("Replica set já possui configuração, não iniciando novamente.");
} catch (e) {
  print("Nenhuma config encontrada — iniciando rs.initiate()");
  rs.initiate({
    _id: "rs0",
    members: [
      { _id: 0, host: "mongo1:27017" },
      { _id: 1, host: "mongo2:27017" },
      { _id: 2, host: "mongo3:27017" }
    ]
  });
}
'

echo "Replica Set: comando enviado. Aguardando estabilização..."
sleep 5

echo "Status atual do Replica Set (via mongo1):"
mongosh "mongodb://mongo1:27017" --eval "rs.status()"
