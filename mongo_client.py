from pymongo import MongoClient

# Conexión a MongoDB local
client = MongoClient('mongodb://localhost:27017/')
db_mongo = client['buen_taco_logs']

# Colección de logs de auditoría
logs_col = db_mongo['logs_auditoria']