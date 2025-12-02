#!/bin/bash
set -e

# Espera o mongod inicializar
until mongo --eval 'db.adminCommand("ping")' >/dev/null 2>&1; do
  echo "Aguardando mongod..."
  sleep 1
done

# Inicia o replica set com os três membros
cat <<'EOF' | mongo
rs.initiate({_id: 'rs0', members: [
  {_id: 0, host: 'mongo1:27017'},
  {_id: 1, host: 'mongo2:27017'},
  {_id: 2, host: 'mongo3:27017'}
]})
EOF

# Mostra status
mongo --eval 'rs.status()'
