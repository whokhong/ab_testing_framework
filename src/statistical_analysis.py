import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from config import AB_TEST_CONFIG

class StatisticalAnalyzer:
    def __init__(self, metrics_df, user_df):
        self.metrics_df = metrics_df
        self.user_df = user_df
        self.config = AB_TEST_CONFIG
        self.alpha = self.config["significance_level"]
        
    def analyze_conversion_rate(self):
        """分析转化率差异"""
        control_data = self.user_df[self.user_df["group"] == "control"]
        treatment_data = self.user_df[self.user_df["group"] == "treatment"]
        
        n_control = len(control_data)
        n_treatment = len(treatment_data)
        
        conversions_control = control_data["converted_user"].sum()
        conversions_treatment = treatment_data["converted_user"].sum()
        
        # 执行比例检验
        count = np.array([conversions_control, conversions_treatment])
        nobs = np.array([n_control, n_treatment])
        
        zstat, pval = proportions_ztest(count, nobs)
        
        # 计算提升幅度
        cr_control = conversions_control / n_control
        cr_treatment = conversions_treatment / n_treatment
        lift = (cr_treatment - cr_control) / cr_control
        
        return {
            "metric": "conversion_rate",
            "control_value": cr_control,
            "treatment_value": cr_treatment,
            "lift": lift,
            "p_value": pval,
            "significant": pval < self.alpha,
            "test_type": "proportions_ztest"
        }
    
    def analyze_continuous_metric(self, metric_col):
        """分析连续变量指标"""
        control_data = self.user_df[self.user_df["group"] == "control"][metric_col]
        treatment_data = self.user_df[self.user_df["group"] == "treatment"][metric_col]
        
        # 执行t检验
        tstat, pval = stats.ttest_ind(treatment_data, control_data, equal_var=False)
        
        # 计算提升幅度
        mean_control = control_data.mean()
        mean_treatment = treatment_data.mean()
        lift = (mean_treatment - mean_control) / mean_control
        
        return {
            "metric": metric_col,
            "control_value": mean_control,
            "treatment_value": mean_treatment,
            "lift": lift,
            "p_value": pval,
            "significant": pval < self.alpha,
            "test_type": "t-test_ind"
        }
    
    def analyze_all_metrics(self):
        """分析所有指标"""
        results = []
        
        # 分析主要指标
        results.append(self.analyze_conversion_rate())
        
        # 分析次要指标
        secondary_metrics = self.config["metrics"]["secondary"]
        for metric in secondary_metrics:
            if metric in self.user_df.columns:
                results.append(self.analyze_continuous_metric(metric))
        
        # 分析医药特定指标
        if "is_chronic" in self.user_df.columns:
            chronic_users = self.user_df[self.user_df["is_chronic"] == True]
            if not chronic_users.empty:
                self.user_df = chronic_users
                results.append(self.analyze_continuous_metric("adherence"))
                results.append(self.analyze_conversion_rate())  # 复购率分析
        
        return pd.DataFrame(results)
    
    def calculate_confidence_intervals(self, metric_col="converted_user"):
        """计算置信区间"""
        control_data = self.user_df[self.user_df["group"] == "control"][metric_col]
        treatment_data = self.user_df[self.user_df["group"] == "treatment"][metric_col]
        
        # 计算均值和标准误
        mean_control = control_data.mean()
        mean_treatment = treatment_data.mean()
        
        se_control = control_data.sem()
        se_treatment = treatment_data.sem()
        
        # 计算95%置信区间
        ci_control = stats.norm.interval(0.95, loc=mean_control, scale=se_control)
        ci_treatment = stats.norm.interval(0.95, loc=mean_treatment, scale=se_treatment)
        
        return {
            "control": {"mean": mean_control, "ci_lower": ci_control[0], "ci_upper": ci_control[1]},
            "treatment": {"mean": mean_treatment, "ci_lower": ci_treatment[0], "ci_upper": ci_treatment[1]}
        }
