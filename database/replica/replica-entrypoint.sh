
#!/bin/bash
set -e

echo "Starting PostgreSQL Read Replica..."

mkdir -p "$PGDATA"
chown postgres:postgres "$PGDATA"

if [ ! -s "$PGDATA/PG_VERSION" ]; then

    echo "Waiting for Primary Database..."

    until pg_isready -h postgres-primary -p 5432; do
        sleep 2
    done

    echo "Cloning Primary Database..."

    export PGPASSWORD="$REPLICATION_PASSWORD"

    gosu postgres pg_basebackup \
        -h postgres-primary \
        -p 5432 \
        -D "$PGDATA" \
        -U "$REPLICATION_USER" \
        -Fp -Xs -P -R

    unset PGPASSWORD

    # Simpan password untuk koneksi replikasi berikutnya
    sed -i '/^primary_conninfo =/d' "$PGDATA/postgresql.auto.conf"

    echo "primary_conninfo = 'host=postgres-primary port=5432 user=${REPLICATION_USER} password=${REPLICATION_PASSWORD}'" >> "$PGDATA/postgresql.auto.conf"

    chown -R postgres:postgres "$PGDATA"

fi

echo "Starting Replica PostgreSQL server..."

exec /usr/local/bin/docker-entrypoint.sh postgres
