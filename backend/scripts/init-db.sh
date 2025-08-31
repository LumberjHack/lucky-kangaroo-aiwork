#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Activer les extensions nécessaires
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "postgis";
    
    -- Créer les rôles si nécessaire
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'luckykangaroo') THEN
            CREATE ROLE luckykangaroo WITH LOGIN PASSWORD 'luckykangaroo';
        END IF;
    END
    \$\$;
    
    -- Accorder les privilèges
    GRANT ALL PRIVILEGES ON DATABASE luckykangaroo TO luckykangaroo;
    \c luckykangaroo
    GRANT ALL ON SCHEMA public TO luckykangaroo;
    
    -- Activer les extensions dans la base de données
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "postgis";
EOSQL

echo "Initialisation de la base de données terminée avec succès!"
