# database

import firebase_admin
from firebase_admin import firestore


# Use application default credentials instead of explicitly loading JSON
firebase_admin.initialize_app()

# Firestore Client
db = firestore.client()
