db = db.getSiblingDB("n8n_db");
db.createCollection("tokens");
db.createCollection("sleep_data");
db.createCollection("daily_reports");
