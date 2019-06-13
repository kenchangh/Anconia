import pdb
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
service_key = os.path.join(root_dir, 'service-key.json')

cred = credentials.Certificate(service_key)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://anconia-4008c.firebaseio.com'
})

db = firestore.client()
nodes_ref = db.collection('nodes')


def to_peers_string(peers):
    return [host+':'+str(port)for host, port in list(peers)]


def set_nodes(peers):
    peers = to_peers_string(peers)
    node_ref = nodes_ref.document()
    node_ref.set({
        'created_at': firestore.SERVER_TIMESTAMP,
        'peers': peers
    })
    return node_ref.get().id


def update_nodes(document_id, peers):
    peers = to_peers_string(peers)
    node_ref = nodes_ref.document(document_id)
    node_ref.set({
        'peers': peers
    })
