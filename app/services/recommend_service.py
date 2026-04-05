import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import text
from app import db


class RecommendService:

    def _get_consume_data(self):
        sql = text("""
            SELECT user_id, dish_ids
            FROM consume_record
            WHERE dish_ids IS NOT NULL AND dish_ids != ''
        """)

        try:
            raw_df = pd.read_sql(sql, db.engine)

            if raw_df.empty:
                return pd.DataFrame(columns=['user_id', 'dish_id', 'consume_count'])

            # 【修复1】对拆解和数据转型的顺序进行了安全重构
            df = raw_df.assign(dish_id=raw_df['dish_ids'].astype(str).str.split(',')).explode('dish_id')

            # 清除空格并转为数字（非数字转为 NaN）
            df['dish_id'] = pd.to_numeric(df['dish_id'].str.strip(), errors='coerce')

            # 丢弃 NaN 数据
            df = df.dropna(subset=['dish_id'])
            # 放心转为整型
            df['dish_id'] = df['dish_id'].astype(int)

            df_count = df.groupby(['user_id', 'dish_id']).size().reset_index(name='consume_count')

            return df_count

        except Exception as e:
            print(f"数据处理失败: {e}")
            return pd.DataFrame(columns=['user_id', 'dish_id', 'consume_count'])

    def get_recommendations(self, target_user_id, top_n=3):
        df = self._get_consume_data()

        if df.empty or target_user_id not in df['user_id'].values:
            return []

        user_item_matrix = df.pivot(index='user_id', columns='dish_id', values='consume_count').fillna(0)

        user_similarity = cosine_similarity(user_item_matrix)
        user_sim_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

        similar_users = user_sim_df[target_user_id].drop(target_user_id).sort_values(ascending=False)
        top_neighbors = similar_users.head(3).index.tolist()

        target_user_consumed = df[df['user_id'] == target_user_id]['dish_id'].tolist()

        recommendations = {}
        for neighbor in top_neighbors:
            neighbor_consumed = df[df['user_id'] == neighbor]
            for _, row in neighbor_consumed.iterrows():
                dish = row['dish_id']
                count = row['consume_count']

                if dish not in target_user_consumed:
                    if dish not in recommendations:
                        recommendations[dish] = 0
                    similarity_score = user_sim_df.loc[target_user_id, neighbor]
                    recommendations[dish] += count * similarity_score

        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [int(dish_id) for dish_id, score in sorted_recommendations[:top_n]]


recommend_service = RecommendService()