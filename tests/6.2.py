import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体，防止乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # Mac 用户请改成 'Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False

# 模拟高大上的压测数据
concurrency = np.array([50, 100, 200, 300, 400, 500]) # 并发用户数
tps = np.array([480, 950, 1850, 2700, 3100, 3250])    # 吞吐量 (逐步达到系统瓶颈)
avg_rt = np.array([12, 18, 35, 80, 150, 280])         # 平均响应时间(ms)
p99_rt = np.array([25, 40, 85, 160, 290, 510])        # P99响应时间(ms)

fig, ax1 = plt.subplots(figsize=(8, 5.5))

# 绘制柱状图：TPS 吞吐量 (绑定到右侧Y轴)
ax2 = ax1.twinx()
bar_plot = ax2.bar(concurrency, tps, width=35, alpha=0.25, color='#3498db', label='TPS (每秒处理事务数)')
ax2.set_ylabel('系统吞吐量 (Transactions / sec)', color='#2980b9', fontweight='bold')
ax2.tick_params(axis='y', labelcolor='#2980b9')

# 绘制折线图：响应时间 (绑定到左侧Y轴)
line1, = ax1.plot(concurrency, avg_rt, marker='o', color='#2ecc71', linewidth=2.5, markersize=8, label='平均响应时间 (Avg RT)')
line2, = ax1.plot(concurrency, p99_rt, marker='s', color='#e74c3c', linewidth=2.5, markersize=8, label='99% 响应时间 (P99 RT)')
ax1.set_xlabel('并发用户数 (Concurrent Users)', fontweight='bold')
ax1.set_ylabel('响应时间 (毫秒 / ms)', fontweight='bold')

# 图表美化
plt.title('大屏核心接口高并发性能压力测试分析图', fontsize=14, pad=15, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)

# 合并图例
lines = [bar_plot, line1, line2]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=True, shadow=True)

plt.tight_layout()
plt.show() # 保存生成的图片！