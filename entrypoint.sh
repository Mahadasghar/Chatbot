#!/bin/sh

# Wait for the database service to be ready
echo "Waiting for the database..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is ready!"

# Now, start the application
if [ "$FLASK_ENV" = "production" ]; then
    exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    exec python app.py
fi