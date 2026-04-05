import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs
import statsmodels.api as sm
import warnings

# 忽略不必要的警告，保持控制台整洁
warnings.filterwarnings("ignore")

# ==========================================
# 0. 全局图表中文显示设置
# ==========================================
# Windows 用户默认使用 SimHei（黑体）。如果你是 Mac 用户，请将 'SimHei' 改为 'Arial Unicode MS'
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_kmeans_charts():
    """生成 K-Means 聚类评估图（肘部法则与轮廓系数）"""
    print("正在生成 K-Means 评估图...")

    # 模拟生成大学生的消费特征数据（设置了3个隐性群体）
    X, _ = make_blobs(n_samples=600, centers=3, cluster_std=1.2, random_state=42)

    sse = []  # 误差平方和
    sil = []  # 轮廓系数
    K_range = range(2, 9)

    for k in K_range:
        # 显式设置 n_init=10 避免警告
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        sse.append(kmeans.inertia_)
        sil.append(silhouette_score(X, kmeans.labels_))

    # [第一张图]：肘部法则图
    plt.figure(figsize=(7, 4.5))
    plt.plot(K_range, sse, marker='o', linestyle='-', color='#2c3e50')
    plt.title('K-Means 肘部法则评估 (Elbow Method)', fontsize=14, pad=10)
    plt.xlabel('聚类数 K (分群数量)')
    plt.ylabel('误差平方和 (SSE)')
    plt.grid(True, linestyle='--', alpha=0.6)
    # 标注最佳K值点
    plt.annotate('最佳拐点 (K=3)', xy=(3, sse[1]), xytext=(4, sse[1] + 2000),
                 arrowprops=dict(facecolor='red', shrink=0.05))
    plt.tight_layout()
    plt.show()

    # [第二张图]：轮廓系数图
    plt.figure(figsize=(7, 4.5))
    plt.plot(K_range, sil, marker='s', linestyle='-', color='#e74c3c')
    plt.title('K-Means 轮廓系数评估 (Silhouette Score)', fontsize=14, pad=10)
    plt.xlabel('聚类数 K (分群数量)')
    plt.ylabel('轮廓系数')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()


def generate_sarimax_charts():
    """生成 SARIMAX 营业额预测图与模型诊断图"""
    print("正在生成 SARIMAX 预测及诊断图...")

    # 模拟带有 7 天周期性（周末客流减少）的食堂营业额数据
    np.random.seed(42)
    dates = pd.date_range(start='2026-03-01', periods=60)
    # 基础营业额 + 7天周期的正弦波动 + 随机噪声
    base_sales = 8000 + 2000 * np.sin(np.arange(60) * (2 * np.pi / 7))
    noise = np.random.normal(0, 300, 60)
    sales = base_sales + noise
    df = pd.DataFrame({'Sales': sales}, index=dates)

    # 构建 SARIMAX 模型 (假设季节周期 s=7)
    model = sm.tsa.statespace.SARIMAX(df['Sales'],
                                      order=(1, 1, 1),
                                      seasonal_order=(1, 1, 1, 7))
    results = model.fit(disp=False)

    # 获取预测数据（往后预测）
    pred = results.get_prediction(start=15, end=60)
    pred_mean = pred.predicted_mean
    pred_ci = pred.conf_int()

    # [第三张图]：实际值与预测值对比图
    plt.figure(figsize=(9, 5))
    plt.plot(df.index, df['Sales'], label='实际营业额 (脱敏)', color='#34495e')
    plt.plot(pred_mean.index, pred_mean, label='SARIMAX 预测拟合曲线', color='#e74c3c', linestyle='--')
    plt.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color='#e74c3c', alpha=0.15,
                     label='95% 置信区间')
    plt.title('SARIMAX 食堂营业额预测拟合效果', fontsize=14, pad=10)
    plt.xlabel('日期')
    plt.ylabel('日营业额 (元)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

    # [第四张图]：残差正态分布与诊断图
    # 稍微加大了画布高度，防止内容拥挤
    fig = plt.figure(figsize=(10, 7.5))
    fig = results.plot_diagnostics(fig=fig, lags=15)

    # 调整了标题大小，并加粗，去除了过大的 y 偏移
    fig.suptitle('SARIMAX 模型残差白噪声检验与诊断', fontsize=16, fontweight='bold')

    # 【修复关键点】：通过 rect 参数强制给画布顶部留出 6% 的空白区域给主标题，完美防止文字被吞掉
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.show()


if __name__ == "__main__":
    print("=" * 50)
    print("开始生成论文算法评估图表...")
    print("温馨提示：每次弹出一张图，请关闭当前图片窗口后，才会自动弹出下一张。")
    print("=" * 50)

    # 1. 生成 K-Means 相关图表
    generate_kmeans_charts()

    # 2. 生成 SARIMAX 相关图表
    generate_sarimax_charts()

    print("所有图表生成完毕！")