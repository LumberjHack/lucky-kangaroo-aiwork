#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
if [ "$DATABASE_URL" != "" ]; then
  until psql -d "$DATABASE_URL" -c 'SELECT 1' >/dev/null 2>&1; do
    echo "Waiting for PostgreSQL to start..."
    sleep 2
  done
  echo "PostgreSQL is ready!"
fi

# Run database migrations
if [ "$FLASK_ENV" = "production" ] || [ "$FLASK_ENV" = "staging" ]; then
  echo "Running database migrations..."
  flask db upgrade
  echo "Migrations completed!"
fi

# Initialize search index
if [ "$SEARCH_URL" != "" ]; then
  echo "Initializing search index..."
  flask init-search
  echo "Search index initialized!"
fi

# Create default admin user if it doesn't exist
if [ "$DEFAULT_ADMIN_EMAIL" != "" ] && [ "$DEFAULT_ADMIN_PASSWORD" != "" ]; then
  echo "Creating default admin user..."
  flask create-admin "$DEFAULT_ADMIN_EMAIL" "$DEFAULT_ADMIN_PASSWORD"
  echo "Default admin user created!"
fi

# Execute the command passed to the container
exec "$@"
