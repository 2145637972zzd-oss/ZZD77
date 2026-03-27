import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
from app.services.data_service import data_service
# 【修复】使用正确的模型导入路径
from app.models import DishInfo
from app import db


class AprioriService:
    @staticmethod
    def get_dish_association_rules(min_support=0.05, min_threshold=0.3):
        # 降低支持度阈值以适应稀疏的海量数据
        consume_df = data_service.get_consume_dataframe()
        if consume_df.empty or 'dish_ids' not in consume_df.columns:
            return []

        # 获取菜品字典
        dish_list = db.session.query(DishInfo.dish_id, DishInfo.dish_name).all()
        dish_map = {str(d.dish_id): d.dish_name for d in dish_list}

        # 1. 提取订单中的菜品组合（去除单件商品的订单，加速计算）
        transactions = []
        for idx, row in consume_df.iterrows():
            if row['dish_ids']:
                items = str(row['dish_ids']).split(',')
                if len(items) > 1:  # 只分析组合购买的行为
                    transactions.append(items)

        if not transactions:
            return []

        # 2. 使用更高效的 TransactionEncoder 构建稀疏布尔矩阵
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        basket_df = pd.DataFrame(te_ary, columns=te.columns_)

        # 3. 算法升级：替换 Apriori 为 FP-Growth，速度提升 10 倍以上
        frequent_itemsets = fpgrowth(basket_df, min_support=min_support, use_colnames=True)
        if frequent_itemsets.empty:
            return []

        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)
        if rules.empty:
            return []

        # 4. 整理结果，映射菜品名称
        result = []
        for idx, row in rules.iterrows():
            antecedents = [dish_map.get(d, d) for d in list(row['antecedents'])]
            consequents = [dish_map.get(d, d) for d in list(row['consequents'])]
            result.append({
                'antecedents': '、'.join(antecedents),
                'consequents': '、'.join(consequents),
                'support': round(float(row['support']), 4),
                'confidence': round(float(row['confidence']), 4),
                'lift': round(float(row['lift']), 4)
            })

        # 按提升度(Lift)排序，优先展示相关性最强的组合
        return sorted(result, key=lambda x: x['lift'], reverse=True)[:20]


apriori_service = AprioriService()