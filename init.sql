CREATE DATABASE db_auth

-- Fichier: init.sql
-- Ce fichier sera exécuté automatiquement au démarrage du conteneur

-- Extension pour UUID si nécessaire
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des devices
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'offline',
    location VARCHAR(200),
    firmware_version VARCHAR(50) DEFAULT '1.0.0',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    config TEXT DEFAULT '{}',
    battery_level FLOAT,
    signal_strength FLOAT,
    is_active BOOLEAN DEFAULT true,
    owner_id VARCHAR(100)
);

-- Index pour optimiser les recherches
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_device_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_owner_id ON devices(owner_id);
CREATE INDEX IF NOT EXISTS idx_devices_is_active ON devices(is_active);

-- Table pour les logs d'événements des devices (optionnel)
CREATE TABLE IF NOT EXISTS device_events (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- Index pour la table d'événements
CREATE INDEX IF NOT EXISTS idx_device_events_device_id ON device_events(device_id);
CREATE INDEX IF NOT EXISTS idx_device_events_created_at ON device_events(created_at);

-- Fonction pour mettre à jour automatically le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour mettre à jour automatically updated_at
CREATE TRIGGER update_devices_updated_at 
    BEFORE UPDATE ON devices 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insérer quelques données de test (optionnel)
INSERT INTO devices (device_id, name, device_type, location, status, is_active) 
VALUES 
    ('sensor-001', 'Température Salon', 'sensor', 'Salon', 'online', true),
    ('sensor-002', 'Humidité Cuisine', 'sensor', 'Cuisine', 'online', true),
    ('actuator-001', 'Volet Roulant', 'actuator', 'Chambre', 'offline', true),
    ('gateway-001', 'Gateway Principale', 'gateway', 'Bureau', 'online', true)
ON CONFLICT (device_id) DO NOTHING;

-- Vérification
SELECT 'Tables créées avec succès' as message;