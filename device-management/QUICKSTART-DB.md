# 🚀 Guide Complet - PostgreSQL + Device Management

## ⚡ Démarrage Ultra-Rapide (5 minutes)

### Prérequis
- Docker installé ([https://www.docker.com/](https://www.docker.com/))
- Python 3.11+ avec venv activé

### Étapes
```bash
# 1. Démarrer PostgreSQL
./postgres.bat start  # ou ./postgres.sh start sur Linux/Mac

# 2. Initialiser la base de données
./postgres.bat init

# 3. Lancer l'application
./postgres.bat run
```

C'est tout! 🎉

---

## 📋 Options de Configuration

### Option A: Docker Compose (Recommandé)
✅ Zéro installation requise  
✅ Facile à démarrer/arrêter  
✅ Données persistantes  

```bash
./postgres.bat start
```

### Option B: PostgreSQL Local
✅ Plus de contrôle  
✅ Meilleure performance  
❌ Installation requise  

[Voir POSTGRESQL.md pour les détails](POSTGRESQL.md)

---

## 🔌 Vérifier la Connexion

### Vérifier que PostgreSQL fonctionne
```bash
# Docker
docker-compose -f docker-compose-dev.yml ps

# Ou accéder à pgAdmin
http://localhost:5050
```

### Vérifier la connexion de l'app
```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "Device Management API",
  "version": "1.0.0",
  "message": "Service is running"
}
```

---

## 📊 Interface pgAdmin (Optional)

Une interface web pour gérer PostgreSQL est incluse:

1. Ouvrir: **http://localhost:5050**
2. Login: `admin@example.com` / `admin`
3. Ajouter une connexion:
   - Host: `postgres-device-mgmt`
   - Port: `5432`
   - User: `postgres`
   - Password: `postgres`
   - Database: `device_management`

---

## 💾 Commandes Utiles

```bash
# Démarrer PostgreSQL
./postgres.bat start

# Initialiser les tables
./postgres.bat init

# Voir les logs
./postgres.bat logs

# Arrêter
./postgres.bat stop

# Nettoyer (supprimer données)
./postgres.bat clean

# Lancer l'app
./postgres.bat run
```

---

## 🧪 Tester l'API

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
```
http://localhost:8000/docs
```

### Créer un Device (exemple)
```bash
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device-001",
    "name": "Capteur Température",
    "device_type": "sensor",
    "location": "Bureau 1"
  }'
```

---

## 🔒 Sécurité

### Changer les credentials par défaut
```bash
# .env
DATABASE_URL=postgresql://my_user:my_secure_password@localhost:5432/device_management
JWT_SECRET=my_very_secure_secret_key_here
```

---

## 🐛 Troubleshooting

### PostgreSQL ne démarre pas
```bash
# Vérifier Docker
docker ps

# Voir les logs
./postgres.bat logs

# Nettoyer et recommencer
./postgres.bat clean
./postgres.bat start
```

### Erreur "connection refused"
```bash
# Attendre 10 secondes le démarrage
# Puis réessayer
```

### Port 5432 déjà utilisé
```bash
# Modifier docker-compose-dev.yml
ports:
  - "5433:5432"  # Utiliser 5433 au lieu de 5432
  
# Puis mettre à jour .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/device_management
```

---

## 📈 Performance

### Optimiser la base de données
```bash
# Voir la taille
docker-compose -f docker-compose-dev.yml exec postgres du -sh /var/lib/postgresql/data

# Vacuum (nettoyer)
docker-compose -f docker-compose-dev.yml exec postgres psql -U postgres -d device_management -c "VACUUM ANALYZE;"
```

---

## 📚 Documentation Complète

- [POSTGRESQL.md](POSTGRESQL.md) - Configuration PostgreSQL détaillée
- [README.md](README.md) - Utilisation de l'API
- [main.py](main.py) - Code source

---

## ✨ Étapes Suivantes

1. **Vérifier l'API** → http://localhost:8000/docs
2. **Créer des devices** → Utiliser Swagger UI
3. **Consulter la documentation** → Lire README.md
4. **Configurer la sécurité** → Lire POSTGRESQL.md

---

## 🎯 Résumé

| Élément | Details |
|---------|---------|
| **Port API** | 8000 |
| **Port PostgreSQL** | 5432 |
| **Port pgAdmin** | 5050 |
| **Base de données** | device_management |
| **User PostgreSQL** | postgres |
| **Password PostgreSQL** | postgres |
| **Documentation API** | http://localhost:8000/docs |

Bon coding! 🚀
