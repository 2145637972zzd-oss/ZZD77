import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import text

# 导入数据库实例
from app import db


class RecommendService:

    def _get_consume_data(self):
        """
        步骤一：从数据库提取真实的消费记录，并处理逗号分隔的 dish_ids
        """
        # 编写 SQL 语句：只拉取 user_id 和 包含多个菜品ID的 dish_ids 字符串
        sql = text("""
            SELECT user_id, dish_ids
            FROM consume_record
            WHERE dish_ids IS NOT NULL AND dish_ids != ''
        """)

        try:
            # 1. 使用 pandas 直接读取 SQL 结果
            raw_df = pd.read_sql(sql, db.engine)

            if raw_df.empty:
                return pd.DataFrame(columns=['user_id', 'dish_id', 'consume_count'])

            # 2. 数据清洗魔法：将逗号分隔的字符串拆成列表，然后“爆炸”成多行
            # 例如: user_id=1, dish_ids="101,105" 会变成两行: (1, '101') 和 (1, '105')
            raw_df['dish_id'] = raw_df['dish_ids'].astype(str).str.split(',')
            df = raw_df.explode('dish_id')

            # 3. 清除可能存在的空格，并过滤掉空数据
            df['dish_id'] = df['dish_id'].str.strip()
            df = df[df['dish_id'] != '']

            # 4. 类型转换：将拆出来的 dish_id 字符串转回整数，方便后续与 dish_info 表关联
            df['dish_id'] = pd.to_numeric(df['dish_id'], errors='coerce')
            df = df.dropna(subset=['dish_id'])  # 丢弃无法转换的无效数据
            df['dish_id'] = df['dish_id'].astype(int)

            # 5. 按 user_id 和 拆分后的 dish_id 分组，统计真实的消费次数
            df_count = df.groupby(['user_id', 'dish_id']).size().reset_index(name='consume_count')

            return df_count

        except Exception as e:
            print(f"数据处理失败: {e}")
            # 如果数据处理出错，返回一个空的 DataFrame 防止程序崩溃
            return pd.DataFrame(columns=['user_id', 'dish_id', 'consume_count'])

    def get_recommendations(self, target_user_id, top_n=3):
        """
        步骤二：核心协同过滤推荐算法
        """
        df = self._get_consume_data()

        # 如果数据库是空的，或者用户没有任何消费记录，无法推荐
        if df.empty or target_user_id not in df['user_id'].values:
            return []

        # 1. 构建 用户-菜品 矩阵 (User-Item Matrix)
        user_item_matrix = df.pivot(index='user_id', columns='dish_id', values='consume_count').fillna(0)

        # 2. 计算用户之间的余弦相似度
        user_similarity = cosine_similarity(user_item_matrix)
        user_sim_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

        # 3. 找到与目标用户最相似的其他用户 (排除自己)
        similar_users = user_sim_df[target_user_id].drop(target_user_id).sort_values(ascending=False)
        top_neighbors = similar_users.head(3).index.tolist()

        # 4. 获取目标用户已经吃过的菜品
        target_user_consumed = df[df['user_id'] == target_user_id]['dish_id'].tolist()

        # 5. 聚合邻居用户的消费记录，找出目标用户没吃过的菜品
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

        # 6. 对推荐得分进行排序，返回 Top N
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [int(dish_id) for dish_id, score in sorted_recommendations[:top_n]]


# 实例化 service 供外部调用
recommend_service = RecommendService()