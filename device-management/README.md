# Device Management Microservice

Microservice pour la gestion des appareils IoT dans le projet Cloud IoT.

## Architecture

```
device-management/
├── controller/           # Couche contrôleurs (endpoints FastAPI)
├── dal/                  # Data Access Layer (requêtes base de données)
├── dto/                  # Data Transfer Objects (validation des données)
├── entities/             # Modèles de base de données
├── helpers/              # Utilitaires (config, auth, cache, messaging)
├── test/                 # Tests unitaires et d'intégration
├── main.py              # Point d'entrée de l'application
├── requirements.txt      # Dépendances Python
├── Dockerfile           # Configuration Docker
├── docker-compose.yml   # Configuration services (Postgres, Redis, RabbitMQ)
└── README.md           # Documentation
```

## Fonctionnalités

- **CRUD Devices**: Créer, lire, mettre à jour et supprimer des appareils
- **Pagination & Filtrage**: Recherche avancée avec pagination
- **Authentification**: Token JWT pour sécuriser les endpoints
- **Cache Distribué**: Redis pour cache haute performance
- **Event Streaming**: RabbitMQ pour événements asynchrones
- **Health Checks**: Monitoring de santé du service
- **Logging**: Logs détaillés au format structuré

## Configuration

### Variables d'environnement

Copier `.env.example` en `.env`:

```bash
cp .env.example .env
```

Configurer les variables:
- `DATABASE_URL`: Connexion PostgreSQL
- `REDIS_URL`: Connexion Redis
- `RABBITMQ_URL`: Connexion RabbitMQ
- `JWT_SECRET`: Clé secrète pour tokens JWT
- `DEBUG`: Mode debug (True/False)

## Installation

### Avec Docker Compose (recommandé)

```bash
cd device-management
docker-compose up -d
```

### Installation locale

1. Créer un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurer la base de données:
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/device_management
```

4. Démarrer l'application:
```bash
python main.py
```

L'API sera accessible à `http://localhost:8000`

## Utilisation

### Endpoints disponibles

#### Health Check
```bash
GET /health
```

#### Devices - CRUD
```bash
# Créer un device
POST /api/v1/devices
{
  "device_id": "device-001",
  "name": "Capteur Température",
  "device_type": "sensor",
  "location": "Bureau 1"
}

# Lister les devices (avec pagination)
GET /api/v1/devices?page=1&page_size=10&status=online

# Récupérer un device
GET /api/v1/devices/{device_id}

# Mettre à jour un device
PUT /api/v1/devices/{device_id}
{
  "name": "Capteur Température - Bureau 1",
  "battery_level": 85.5
}

# Supprimer un device
DELETE /api/v1/devices/{device_id}

# Mettre à jour le statut
POST /api/v1/devices/{device_id}/status
{
  "status": "online",
  "battery_level": 85.5,
  "signal_strength": -45.2
}

# Résumé de santé
GET /api/v1/devices/health/status
```

### Authentification

Les endpoints nécessitent un header `Authorization`:
```bash
Authorization: Bearer {jwt_token}
```

## Structure des données

### Device Entity
```python
{
  "id": 1,
  "device_id": "device-001",
  "name": "Capteur Température",
  "device_type": "sensor",  # sensor | actuator | gateway
  "status": "online",        # online | offline | error | maintenance
  "location": "Bureau 1",
  "firmware_version": "1.0.0",
  "battery_level": 85.5,
  "signal_strength": -45.2,
  "is_active": true,
  "owner_id": "user-123",
  "config": {},
  "last_seen": "2024-01-29T10:30:00",
  "created_at": "2024-01-20T08:00:00",
  "updated_at": "2024-01-29T10:30:00"
}
```

## Filtrage

Les endpoints de liste supportent les filtres:
- `search`: Recherche par nom, device_id ou location
- `device_type`: Filtre par type (sensor, actuator, gateway)
- `status`: Filtre par statut (online, offline, error, maintenance)
- `is_active`: Filtre par état actif (true/false)
- `owner_id`: Filtre par propriétaire
- `min_battery`, `max_battery`: Plage de batterie
- `sort_by`: Champ de tri (default: created_at)
- `sort_order`: Ordre (asc ou desc)

Exemple:
```bash
GET /api/v1/devices?device_type=sensor&status=online&sort_by=battery_level&sort_order=asc
```

## Événements RabbitMQ

Les événements suivants sont publiés:
- `device.created`: Appareil créé
- `device.updated`: Appareil modifié
- `device.deleted`: Appareil supprimé
- `device.status_updated`: Statut mis à jour

## Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Réponse:
```json
{
  "status": "healthy",
  "service": "Device Management API",
  "version": "1.0.0",
  "timestamp": "2024-01-29T10:30:00",
  "database": "connected",
  "redis": "connected",
  "rabbitmq": "connected"
}
```

### Documentation API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Développement

### Tests
```bash
pytest test/
```

### Linting
```bash
flake8 .
black .
```

## Déploiement

### Kubernetes
Utiliser les fichiers dans `../deploy/k8s/`:
- `deployment.yml`
- `service.yml`

```bash
kubectl apply -f ../deploy/k8s/
```

### Production
- Configurer `JWT_SECRET` avec une clé sécurisée
- Restreindre les origines CORS
- Configurer un reverse proxy (nginx)
- Utiliser des variables d'environnement sécurisées

## Troubleshooting

### La base de données ne se connecte pas
```bash
# Vérifier la connexion
psql postgresql://user:password@localhost:5432/device_management

# Créer la base si nécessaire
createdb device_management
```

### Redis ne répond pas
```bash
redis-cli ping
# Devrait retourner PONG
```

### RabbitMQ n'est pas accessible
```bash
# Interface management
curl http://localhost:15672  # credentials: guest/guest
```

## Support & Documentation

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Redis: https://redis.io/
- RabbitMQ: https://www.rabbitmq.com/

## License

Propriété du projet Cloud IoT
