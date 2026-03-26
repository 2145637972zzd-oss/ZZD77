import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from app.services.cluster_service import cluster_service

app = create_app()
with app.app_context():
    labels, features = cluster_service.user_kmeans_cluster()
    print("用户分群结果：")
    for l in labels:
        print(l)