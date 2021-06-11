import psycopg2

conn = psycopg2.connect("dbname='techconfdb' user='hkadmin@azuredevprj3db' host='azuredevprj3db.postgres.database.azure.com' password='{your_password}' port='5432' sslmode='true'"
)
cursor = conn.cursor()

print(cursor)