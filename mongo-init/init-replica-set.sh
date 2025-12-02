#!/bin/bash

# Aguarda o MongoDB estar pronto
echo "Aguardando MongoDB estar pronto..."
until mongosh --eval "db.adminCommand('ping')" 2>/dev/null | grep -q "ok"; do
  echo "MongoDB ainda não está pronto... aguardando 2s"
  sleep 2
done

echo "MongoDB está pronto!"

# Inicializa o Replica Set
echo "Inicializando Replica Set rs0..."
mongosh --eval "rs.initiate({
  _id: 'rs0',
  members: [
    {_id: 0, host: 'mongo1:27017'},
    {_id: 1, host: 'mongo2:27017'},
    {_id: 2, host: 'mongo3:27017'}
  ]
})"

echo "Replica Set inicializado com sucesso!"
