import pandas as pd
import numpy as np
from datetime import datetime
from config import AB_TEST_CONFIG, MEDICAL_METRICS

class BusinessReportGenerator:
    def __init__(self, metrics_df, results_df, test_config):
        self.metrics_df = metrics_df
        self.results_df = results_df
        self.config = test_config
    
    def generate_executive_summary(self):
        """生成执行摘要"""
        # 获取主要指标结果
        primary_metric = self.config["metrics"]["primary"]
        primary_result = self.results_df[self.results_df["metric"] == primary_metric].iloc[0]
        
        summary = {
            "experiment_name": self.config["experiment_name"],
            "start_date": self.metrics_df["date"].min(),
            "end_date": self.metrics_df["date"].max(),
            "primary_metric": primary_metric,
            "control_value": primary_result["control_value"],
            "treatment_value": primary_result["treatment_value"],
            "lift": primary_result["lift"],
            "significant": primary_result["significant"],
            "p_value": primary_result["p_value"],
            "recommendation": "Implement" if primary_result["significant"] and primary_result["lift"] > 0 else "Do not implement"
        }
        
        # 计算潜在业务影响
        if "conversions" in self.metrics_df.columns:
            control_conv = self.metrics_df[self.metrics_df["group"] == "control"]["conversions"].sum()
            lift_conv = control_conv * primary_result["lift"]
            summary["potential_lift_conversions"] = lift_conv
        
        if "total_revenue" in self.metrics_df.columns:
            control_rev = self.metrics_df[self.metrics_df["group"] == "control"]["total_revenue"].sum()
            revenue_per_conv = control_rev / control_conv
            summary["potential_revenue_lift"] = lift_conv * revenue_per_conv
        
        return summary
    
    def generate_full_report(self):
        """生成完整业务报告"""
        report = {
            "experiment_overview": {
                "name": self.config["experiment_name"],
                "objective": "测试新版处方药详情页对转化率的影响",
                "test_groups": self.config["groups"],
                "duration": f"{self.config['test_duration']} days",
                "sample_size_control": len(self.metrics_df[self.metrics_df["group"] == "control"]),
                "sample_size_treatment": len(self.metrics_df[self.metrics_df["group"] == "treatment"])
            },
            "key_results": [],
            "detailed_analysis": [],
            "conclusions": [],
            "recommendations": []
        }
        
        # 添加关键结果
        for _, row in self.results_df.iterrows():
            result = {
                "metric": row["metric"],
                "control_value": row["control_value"],
                "treatment_value": row["treatment_value"],
                "lift": row["lift"],
                "p_value": row["p_value"],
                "significant": row["significant"]
            }
            report["key_results"].append(result)
            
            # 添加详细分析
            analysis = {
                "metric": row["metric"],
                "interpretation": self._interpret_result(row)
            }
            report["detailed_analysis"].append(analysis)
        
        # 添加结论和建议
        primary_result = self.results_df[self.results_df["metric"] == self.config["metrics"]["primary"]].iloc[0]
        if primary_result["significant"]:
            if primary_result["lift"] > 0:
                report["conclusions"].append("实验组在主要指标上表现显著优于对照组")
                report["recommendations"].append("全量上线新版详情页")
            else:
                report["conclusions"].append("实验组在主要指标上表现显著差于对照组")
                report["recommendations"].append("停止实验，保持原版详情页")
        else:
            report["conclusions"].append("实验组和对照组在主要指标上无显著差异")
            report["recommendations"].append("考虑延长测试时间或优化实验方案")
        
        # 添加医药行业特定建议
        if "adherence" in self.results_df["metric"].values:
            adherence_result = self.results_df[self.results_df["metric"] == "adherence"].iloc[0]
            if adherence_result["significant"] and adherence_result["lift"] > 0:
                report["recommendations"].append("新版详情页显著提升用药依从性，建议在慢病管理模块推广")
        
        return report
    
    def _interpret_result(self, result):
        """解释统计结果"""
        if result["significant"]:
            if result["lift"] > 0:
                return f"实验组显著优于对照组，提升幅度为{result['lift']:.2%} (p={result['p_value']:.4f})"
            else:
                return f"实验组显著差于对照组，下降幅度为{-result['lift']:.2%} (p={result['p_value']:.4f})"
        else:
            return f"组间差异不显著 (p={result['p_value']:.4f})"
    
    def generate_report_dataframe(self):
        """生成报告数据框"""
        report_df = self.results_df.copy()
        report_df["business_impact"] = report_df.apply(self._calculate_business_impact, axis=1)
        report_df["interpretation"] = report_df.apply(self._interpret_result, axis=1)
        return report_df[["metric", "control_value", "treatment_value", 
                         "lift", "p_value", "significant", "business_impact", "interpretation"]]
    
    def _calculate_business_impact(self, row):
        """估算业务影响"""
        if row["metric"] == "conversion_rate":
            control_users = len(self.metrics_df[self.metrics_df["group"] == "control"])
            conv_lift = control_users * row["lift"] * row["control_value"]
            return f"每月增加{conv_lift:.0f}次转化"
        
        elif row["metric"] == "avg_order_value":
            conv_rate = self.results_df[self.results_df["metric"] == "conversion_rate"].iloc[0]
            if conv_rate["significant"]:
                lift = conv_rate["lift"]
            else:
                lift = 0
                
            control_conv = self.metrics_df[self.metrics_df["group"] == "control"]["conversions"].sum()
            revenue_lift = control_conv * (1 + lift) * row["lift"] * row["control_value"]
            return f"每月增加收入${revenue_lift:.0f}"
        
        elif row["metric"] == "adherence":
            return "提升患者健康结果，减少并发症风险"
        
        return "N/A"
