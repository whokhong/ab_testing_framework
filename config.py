# A/B测试参数配置
AB_TEST_CONFIG = {
    "experiment_name": "处方药详情页改版",
    "metrics": {
        "primary": "conversion_rate",  # 主要指标：转化率
        "secondary": ["avg_order_value", "bounce_rate"]  # 次要指标
    },
    "groups": {
        "control": "A组(原版)",
        "treatment": "B组(新版)"
    },
    "traffic_allocation": 0.5,  # 每组流量分配比例
    "significance_level": 0.05,  # 显著性水平
    "min_sample_size": 1000,  # 每组最小样本量
    "expected_effect": 0.15,  # 预期提升效果(15%)
    "test_duration": 14  # 测试天数
}

# 医药行业特定指标
MEDICAL_METRICS = {
    "prescription_submission_rate": "处方提交率",
    "medication_adherence": "用药依从性",
    "repurchase_rate_chronic": "慢病复购率"
}
