import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

plt.style.use('seaborn-whitegrid')

class ABTestVisualizer:
    def __init__(self, metrics_df, results_df):
        self.metrics_df = metrics_df
        self.results_df = results_df
    
    def plot_metric_comparison(self, metric='conversion_rate'):
        """绘制指标对比图"""
        # 筛选指定指标数据
        metric_data = self.metrics_df[['group', metric]]
        
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x='group', y=metric, data=metric_data, palette=['#1f77b4', '#ff7f0e'])
        
        # 添加统计显著性标记
        result_row = self.results_df[self.results_df['metric'] == metric].iloc[0]
        if result_row['significant']:
            plt.text(0.5, max(metric_data[metric]) * 1.05, "** Significant **", 
                    ha='center', fontsize=12, color='red')
        
        plt.title(f'{metric.upper()} Comparison', fontsize=14)
        plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
        plt.xlabel('')
        plt.tight_layout()
        return ax
    
    def plot_lift_with_ci(self, metric='conversion_rate'):
        """绘制提升幅度与置信区间"""
        fig = make_subplots(rows=1, cols=1)
        
        # 添加提升幅度点
        result_row = self.results_df[self.results_df['metric'] == metric].iloc[0]
        lift = result_row['lift']
        pval = result_row['p_value']
        
        fig.add_trace(go.Scatter(
            x=[lift],
            y=['Lift'],
            mode='markers',
            marker=dict(size=14, color='red' if pval < 0.05 else 'blue'),
            name='Observed Lift'
        ))
        
        # 添加置信区间
        ci_lower = lift - 1.96 * np.sqrt((lift * (1 - lift)) / len(self.metrics_df))
        ci_upper = lift + 1.96 * np.sqrt((lift * (1 - lift)) / len(self.metrics_df))
        
        fig.add_trace(go.Scatter(
            x=[ci_lower, ci_upper],
            y=['Lift', 'Lift'],
            mode='lines',
            line=dict(color='black', width=2),
            name='95% CI'
        ))
        
        # 添加零线
        fig.add_vline(x=0, line_dash="dash", line_color="green")
        
        fig.update_layout(
            title=f"Lift in {metric.replace('_', ' ').title()} with Confidence Interval",
            xaxis_title="Lift",
            yaxis_title="",
            showlegend=False,
            height=400
        )
        
        return fig
    
    def plot_timeseries(self, df, metric='conversion_rate'):
        """绘制指标时间序列"""
        # 按日期和组计算指标
        daily_metrics = df.groupby(['date', 'group'])[metric].mean().reset_index()
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=daily_metrics, x='date', y=metric, hue='group', 
                    palette=['#1f77b4', '#ff7f0e'], linewidth=2.5)
        
        plt.title(f'Daily {metric.upper()} Trend', fontsize=14)
        plt.ylabel(metric.replace('_', ' ').title(), fontsize=12)
        plt.xlabel('Date', fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title='Group')
        plt.tight_layout()
        return plt
    
    def plot_segmented_results(self, df, segment_col='chronic_type'):
        """绘制细分群体结果"""
        # 计算细分群体的转化率
        segmented = df.groupby(['group', segment_col])['converted'].mean().reset_index()
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x=segment_col, y='converted', hue='group', 
                         data=segmented, palette=['#1f77b4', '#ff7f0e'])
        
        plt.title(f'Conversion Rate by {segment_col.title()}', fontsize=14)
        plt.ylabel('Conversion Rate', fontsize=12)
        plt.xlabel(segment_col.replace('_', ' ').title(), fontsize=12)
        plt.legend(title='Group')
        plt.tight_layout()
        return ax
