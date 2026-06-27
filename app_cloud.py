import streamlit as st
import boto3
import json
import pandas as pd

ENDPOINT_NAME = "credit-score-endpoint"
REGION = "us-east-1"

st.set_page_config(
    page_title="Credit Score Classifier",
    page_icon="💳",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #6366f1;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 0.95rem;
    color: #9ca3af;
    margin-bottom: 2rem;
}
.result-card {
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-top: 1rem;
}
.good-card { background: #ecfdf5; border-left: 5px solid #10b981; }
.standard-card { background: #fffbeb; border-left: 5px solid #f59e0b; }
.poor-card { background: #fef2f2; border-left: 5px solid #ef4444; }
.result-label { font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem; }
.result-desc { font-size: 0.9rem; color: #6b7280; }
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: #6b7280;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💳 Credit Score Classifier</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Prediksi performa kredit nasabah berdasarkan data keuangan. Powered by AWS SageMaker.</div>', unsafe_allow_html=True)

st.divider()

OCCUPATION_OPTIONS = [
    'Architect', 'Developer', 'Doctor', 'Engineer', 'Entrepreneur',
    'Journalist', 'Lawyer', 'Manager', 'Mechanic', 'Media_Manager',
    'Musician', 'Scientist', 'Teacher', 'Writer'
]
PAYMENT_BEHAVIOUR_OPTIONS = [
    'High_spent_Large_value_payments', 'High_spent_Medium_value_payments',
    'High_spent_Small_value_payments', 'Low_spent_Large_value_payments',
    'Low_spent_Medium_value_payments', 'Low_spent_Small_value_payments'
]
OCCUPATION_MAP = {v: i for i, v in enumerate(sorted(OCCUPATION_OPTIONS))}
PAYMENT_BEHAVIOUR_MAP = {v: i for i, v in enumerate(sorted(PAYMENT_BEHAVIOUR_OPTIONS))}

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="section-header">Profil Nasabah</div>', unsafe_allow_html=True)
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    occupation_str = st.selectbox("Occupation", sorted(OCCUPATION_OPTIONS))
    annual_income = st.number_input("Annual Income (USD)", min_value=0.0, value=50000.0, step=1000.0)
    monthly_salary = st.number_input("Monthly Inhand Salary (USD)", min_value=0.0, value=4000.0, step=100.0)
    monthly_balance = st.number_input("Monthly Balance (USD)", min_value=0.0, value=300.0, step=50.0)

    st.markdown('<div class="section-header">Informasi Kredit</div>', unsafe_allow_html=True)
    num_bank_accounts = st.slider("Num Bank Accounts", 0, 20, 3)
    num_credit_card = st.slider("Num Credit Cards", 0, 15, 4)
    num_of_loan = st.slider("Num of Loans", 0, 15, 3)
    outstanding_debt = st.number_input("Outstanding Debt (USD)", min_value=0.0, value=1000.0, step=100.0)
    credit_utilization = st.number_input("Credit Utilization Ratio (%)", min_value=0.0, max_value=100.0, value=30.0)
    credit_history_months = st.number_input("Credit History Age (months)", min_value=0, value=240)

with col_right:
    st.markdown('<div class="section-header">Perilaku Pembayaran</div>', unsafe_allow_html=True)
    interest_rate = st.slider("Interest Rate (%)", 1, 50, 15)
    delay_from_due = st.slider("Delay from Due Date (days)", 0, 90, 10)
    num_delayed_payment = st.slider("Num of Delayed Payments", 0, 30, 5)
    changed_credit_limit = st.number_input("Changed Credit Limit", min_value=-20.0, max_value=50.0, value=5.0)
    num_credit_inquiries = st.slider("Num Credit Inquiries", 0, 20, 4)

    credit_mix_map = {"Bad": 0, "Standard": 1, "Good": 2}
    credit_mix_str = st.selectbox("Credit Mix", list(credit_mix_map.keys()))
    credit_mix = credit_mix_map[credit_mix_str]

    pma_map = {"No": 0, "NM": 1, "Yes": 2}
    pma_str = st.selectbox("Payment of Min Amount", list(pma_map.keys()))
    pma = pma_map[pma_str]

    total_emi = st.number_input("Total EMI per Month (USD)", min_value=0.0, value=100.0, step=10.0)
    amount_invested = st.number_input("Amount Invested Monthly (USD)", min_value=0.0, value=200.0, step=50.0)
    payment_behaviour_str = st.selectbox("Payment Behaviour", sorted(PAYMENT_BEHAVIOUR_OPTIONS))

st.divider()

if st.button("Prediksi Credit Score", use_container_width=True, type="primary"):
    input_data = {
        "Age": age,
        "Annual_Income": annual_income,
        "Monthly_Inhand_Salary": monthly_salary,
        "Num_Bank_Accounts": num_bank_accounts,
        "Num_Credit_Card": num_credit_card,
        "Interest_Rate": interest_rate,
        "Num_of_Loan": num_of_loan,
        "Delay_from_due_date": delay_from_due,
        "Num_of_Delayed_Payment": num_delayed_payment,
        "Changed_Credit_Limit": changed_credit_limit,
        "Num_Credit_Inquiries": num_credit_inquiries,
        "Credit_Mix": credit_mix,
        "Outstanding_Debt": outstanding_debt,
        "Credit_Utilization_Ratio": credit_utilization,
        "Credit_History_Age": credit_history_months,
        "Payment_of_Min_Amount": pma,
        "Total_EMI_per_month": total_emi,
        "Amount_invested_monthly": amount_invested,
        "Payment_Behaviour": PAYMENT_BEHAVIOUR_MAP[payment_behaviour_str],
        "Monthly_Balance": monthly_balance,
        "Occupation": OCCUPATION_MAP[occupation_str],
    }

    try:
        client = boto3.client("sagemaker-runtime", region_name=REGION)
        response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps(input_data),
        )
        result = json.loads(response["Body"].read().decode())
        pred_label = result["label"]
        probabilities = result["probabilities"]

        card_class = {"Good": "good-card", "Standard": "standard-card", "Poor": "poor-card"}
        emoji_map = {"Good": "✅", "Standard": "⚠️", "Poor": "❌"}
        desc_map = {
            "Good": "Nasabah memiliki profil kredit yang baik dan risiko rendah.",
            "Standard": "Nasabah memiliki profil kredit cukup dengan risiko menengah.",
            "Poor": "Nasabah memiliki profil kredit buruk dan risiko tinggi.",
        }

        st.markdown(f"""
        <div class="result-card {card_class[pred_label]}">
            <div class="result-label">{emoji_map[pred_label]} {pred_label}</div>
            <div class="result-desc">{desc_map[pred_label]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Distribusi Probabilitas")
        prob_df = pd.DataFrame({
            "Kelas": list(probabilities.keys()),
            "Probabilitas": [round(v, 4) for v in probabilities.values()]
        })
        st.bar_chart(prob_df.set_index("Kelas"))

    except Exception as e:
        st.error(f"Error memanggil endpoint: {e}")
