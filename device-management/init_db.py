#!/usr/bin/env python
"""
Script d'initialisation de la base de données
Crée les tables et les données initiales
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def init_db():
    """Initialiser la base de données"""
    try:
        print("📝 Initialisation de la base de données...")
        
        from helpers.config import get_engine, get_base
        from entities.device_manager_entity import Device
        
        engine = get_engine()
        Base = get_base()
        
        print("✅ Création des tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Vérification de la connexion...")
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            conn.commit()
        
        print("✅ Base de données initialisée avec succès!")
        print("")
        print("📊 Tables créées:")
        print(f"  - devices")
        print("")
        print("Ready to use!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_db()
