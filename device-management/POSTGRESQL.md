# 🗄️ Guide PostgreSQL - Device Management

## Démarrage Rapide

### Option 1: Docker Compose (Recommandé - 2 min)

```bash
cd device-management

# Démarrer PostgreSQL
docker-compose -f docker-compose-dev.yml up -d

# Initialiser la base de données
python init_db.py

# Lancer l'application
python main.py
```

Puis accédez à: **http://localhost:8000**

---

### Option 2: Installation Locale PostgreSQL

#### Étape 1: Installer PostgreSQL
```bash
# Windows: Télécharger depuis https://www.postgresql.org/download/windows/
# macOS: brew install postgresql@15
# Linux: sudo apt-get install postgresql postgresql-contrib
```

#### Étape 2: Démarrer le service
```bash
# Windows: PostgreSQL s'exécute en tant que service
# macOS/Linux:
sudo service postgresql start
```

#### Étape 3: Créer la base de données
```bash
# Ouvrir un terminal PostgreSQL
psql -U postgres

# Dans le terminal PostgreSQL:
CREATE DATABASE device_management;
CREATE USER device_user WITH PASSWORD 'device_password';
ALTER ROLE device_user SET client_encoding TO 'utf8';
ALTER ROLE device_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE device_user SET default_transaction_deferrable TO on;
ALTER ROLE device_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE device_management TO device_user;
\q
```

#### Étape 4: Configurer .env
```env
DATABASE_URL=postgresql://device_user:device_password@localhost:5432/device_management
```

#### Étape 5: Initialiser les tables
```bash
python init_db.py
```

#### Étape 6: Lancer l'application
```bash
python main.py
```

---

## Configuration PostgreSQL

### Fichier .env - Configuration de base
```env
# Format: postgresql://[user]:[password]@[host]:[port]/[database]
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/device_management
```

### Configuration avancée avec SQLAlchemy
```env
# Activer le logging des requêtes SQL
SQLALCHEMY_ECHO=True

# Timeouts et pool
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
```

---

## Gestion de la Base de Données

### Initialiser les tables
```bash
python init_db.py
```

### Vérifier la connexion
```python
python -c "
from helpers.config import get_engine
engine = get_engine()
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print(result.fetchone())
"
```

### Accéder à pgAdmin (Docker)
```
URL: http://localhost:5050
Email: admin@example.com
Password: admin
```

Ajouter une connexion:
- Host: postgres-device-mgmt
- Port: 5432
- User: postgres
- Password: postgres

---

## Opérations Courantes

### Créer/Récréer les tables
```bash
python init_db.py
```

### Vérifier les données
```bash
psql -U postgres -d device_management -c "SELECT * FROM devices;"
```

### Sauvegarder la base de données
```bash
pg_dump -U postgres device_management > backup.sql
```

### Restaurer depuis une sauvegarde
```bash
psql -U postgres device_management < backup.sql
```

---

## Structure des Tables

### Table: devices
```sql
CREATE TABLE devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'offline',
    location VARCHAR(200),
    firmware_version VARCHAR(50) DEFAULT '1.0.0',
    config TEXT DEFAULT '{}',
    battery_level FLOAT,
    signal_strength FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    owner_id VARCHAR(100),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Troubleshooting

### Erreur: "could not connect to server"
```bash
# Vérifier que PostgreSQL est démarré
# Docker:
docker-compose -f docker-compose-dev.yml ps

# Vérifier la configuration .env
cat .env | grep DATABASE_URL
```

### Erreur: "FATAL: role 'postgres' does not exist"
```bash
# Créer l'utilisateur
createuser postgres
```

### Erreur: "database 'device_management' does not exist"
```bash
# Créer la base
createdb -U postgres device_management
```

### Vérifier les connexions PostgreSQL
```bash
psql -U postgres -c "SELECT datname FROM pg_database;"
```

---

## Sécurité

### Changer le mot de passe PostgreSQL
```bash
psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'new_password';"
```

### Créer un utilisateur avec permissions limitées
```bash
psql -U postgres

CREATE USER device_app WITH ENCRYPTED PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE device_management TO device_app;
GRANT USAGE ON SCHEMA public TO device_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO device_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO device_app;
```

---

## Performance

### Vérifier les index
```sql
\d devices
```

### Analyser les requêtes lentes
```bash
# Activer le query logging
SQLALCHEMY_ECHO=True python main.py
```

### Nettoyer les données anciennes
```sql
-- Supprimer les devices inactifs depuis 30 jours
DELETE FROM devices 
WHERE is_active = FALSE 
AND updated_at < NOW() - INTERVAL '30 days';
```

---

## Migration vers Production

### Sauvegarde avant migration
```bash
pg_dump -U postgres device_management > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Déployer avec credentials sécurisés
```env
# Ne pas utiliser de mot de passe par défaut en production!
DATABASE_URL=postgresql://[secure_user]:[secure_password]@[prod_host]:5432/device_management
```

### Vérifier la santé
```bash
curl http://localhost:8000/health
```

---

## Support

Pour plus d'informations:
- Documentation PostgreSQL: https://www.postgresql.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Voir aussi: README.md
