import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
from config import DATA_GENERATION

fake = Faker()

def generate_patients(num_patients):
    """生成患者基本信息"""
    patients = []
    for i in range(1, num_patients + 1):
        age = random.randint(18, 90)
        gender = random.choice(['M', 'F'])
        disease = random.choice(DATA_GENERATION["disease_types"])
        join_date = fake.date_between(
            start_date=DATA_GENERATION["start_date"], 
            end_date=DATA_GENERATION["end_date"]
        )
        
        patients.append({
            "patient_id": i,
            "name": fake.name(),
            "age": age,
            "gender": gender,
            "primary_disease": disease,
            "join_date": join_date,
            "phone": fake.phone_number(),
            "address": fake.address().replace('\n', ', ')
        })
    
    return pd.DataFrame(patients)

def generate_transactions(patients_df):
    """生成交易记录"""
    transactions = []
    patient_ids = patients_df["patient_id"].tolist()
    
    for pid in patient_ids:
        # 每个患者有1-12次交易
        num_transactions = random.randint(1, 12)
        disease = patients_df[patients_df["patient_id"] == pid]["primary_disease"].values[0]
        drugs = DATA_GENERATION["drug_categories"][disease]
        
        for _ in range(num_transactions):
            drug = random.choice(drugs)
            quantity = random.randint(1, 4)
            unit_price = round(random.uniform(20, 200), 2)
            amount = round(quantity * unit_price, 2)
            transaction_date = fake.date_between(
                start_date=DATA_GENERATION["start_date"],
                end_date=DATA_GENERATION["end_date"]
            )
            
            transactions.append({
                "transaction_id": len(transactions) + 1,
                "patient_id": pid,
                "drug_name": drug,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount,
                "transaction_date": transaction_date
            })
    
    return pd.DataFrame(transactions)

def generate_prescriptions(transactions_df):
    """生成处方数据"""
    prescriptions = []
    grouped = transactions_df.groupby("patient_id")
    
    for pid, group in grouped:
        # 为每种药物生成处方
        drugs = group["drug_name"].unique()
        for drug in drugs:
            drug_transactions = group[group["drug_name"] == drug]
            first_prescription = drug_transactions["transaction_date"].min()
            
            # 预期用药间隔 (天)
            if drug == "Insulin":
                expected_interval = 30
            elif drug == "Inhalers":
                expected_interval = 60
            else:
                expected_interval = random.choice([30, 60, 90])
            
            # 实际间隔有波动
            actual_interval = max(1, int(expected_interval * random.uniform(0.7, 1.3)))
            
            prescriptions.append({
                "prescription_id": len(prescriptions) + 1,
                "patient_id": pid,
                "drug_name": drug,
                "first_prescription_date": first_prescription,
                "expected_interval_days": expected_interval,
                "actual_interval_days": actual_interval
            })
    
    return pd.DataFrame(prescriptions)

def generate_adherence(patients_df, prescriptions_df):
    """生成用药依从性数据"""
    adherence_data = []
    
    for _, patient in patients_df.iterrows():
        pid = patient["patient_id"]
        age = patient["age"]
        disease = patient["primary_disease"]
        
        # 基础依从率 (年龄越大依从性越好)
        base_adherence = 0.7 + (age - 50) * DATA_GENERATION["adherence_factors"]["age_effect"] / 100
        
        # 疾病类型影响
        disease_effect = DATA_GENERATION["adherence_factors"]["disease_effect"].get(disease, 0)
        adherence_rate = min(0.95, max(0.3, base_adherence + disease_effect))
        
        # 患者自主反馈 (1-5星)
        feedback_score = random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.1, 0.2, 0.3, 0.25, 0.15]
        )[0]
        
        # 计算最终依从性评分
        adherence_score = min(1.0, adherence_rate * (0.9 + (feedback_score - 1) * 0.05))
        
        adherence_data.append({
            "patient_id": pid,
            "adherence_rate": round(adherence_rate, 4),
            "feedback_score": feedback_score,
            "adherence_score": round(adherence_score, 4),
            "last_updated": DATA_GENERATION["end_date"]
        })
    
    return pd.DataFrame(adherence_data)

def generate_all_data():
    """生成所有测试数据"""
    print("Generating patient data...")
    patients_df = generate_patients(DATA_GENERATION["num_patients"])
    
    print("Generating transaction data...")
    transactions_df = generate_transactions(patients_df)
    
    print("Generating prescription data...")
    prescriptions_df = generate_prescriptions(transactions_df)
    
    print("Generating adherence data...")
    adherence_df = generate_adherence(patients_df, prescriptions_df)
    
    # 保存数据
    patients_df.to_csv("../data/patients.csv", index=False)
    transactions_df.to_csv("../data/transactions.csv", index=False)
    prescriptions_df.to_csv("../data/prescriptions.csv", index=False)
    adherence_df.to_csv("../data/adherence.csv", index=False)
    
    print("Data generation complete!")
    
    return patients_df, transactions_df, prescriptions_df, adherence_df

if __name__ == "__main__":
    generate_all_data()
