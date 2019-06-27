echo "Esperando a postgres..."

while ! nc -z pedidos-db 5432; do
    sleep 0.1
done 

echo "PostgresSQL iniciando"

python manage.py run -h 0.0.0.0