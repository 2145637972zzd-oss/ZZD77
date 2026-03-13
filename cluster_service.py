import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.services.data_service import data_service

class ClusterService:
    @staticmethod
    def user_kmeans_cluster(n_clusters=3):
        user_features = data_service.get_user_consume_features()
        if user_features.empty:
            return [], user_features

        # 特征选择与标准化
        feature_cols = ['total_amount', 'consume_count', 'avg_amount', 'consume_days', 'last_consume_days']
        X = user_features[feature_cols].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-Means聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        cluster_labels = kmeans.fit_predict(X_scaled)
        user_features['cluster'] = cluster_labels

        # 聚类结果分析
        cluster_analysis = user_features.groupby('cluster').agg(
            user_count=('user_id', 'count'),
            avg_total_amount=('total_amount', 'mean'),
            avg_consume_count=('consume_count', 'mean'),
            avg_avg_amount=('avg_amount', 'mean'),
            avg_consume_days=('consume_days', 'mean'),
            avg_last_consume_days=('last_consume_days', 'mean')
        ).reset_index()

        # 给用户群体打标签
        cluster_labels_map = []
        for idx, row in cluster_analysis.iterrows():
            if row['avg_total_amount'] > cluster_analysis['avg_total_amount'].mean() and row['avg_consume_count'] > cluster_analysis['avg_consume_count'].mean():
                label = '高价值活跃用户'
            elif row['avg_last_consume_days'] > 7:
                label = '流失风险用户'
            else:
                label = '普通稳定用户'
            cluster_analysis.loc[idx, 'cluster_label'] = label
            cluster_labels_map.append({
                'cluster': int(row['cluster']),
                'cluster_label': label,
                'user_count': int(row['user_count']),
                'avg_total_amount': round(float(row['avg_total_amount']), 2),
                'avg_consume_count': round(float(row['avg_consume_count']), 2)
            })
        return cluster_labels_map, user_features

cluster_service = ClusterService()