
import streamlit as st
import pdfplumber
import torch
import pandas as pd
import matplotlib.pyplot as plt
import os

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from inference_preprocessing import pdf_text_to_atomic_sentences

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Greenwashing Risk – Portfolio View",
    page_icon="🌱",
    layout="wide"
)

# -------------------------------------------------
# Load model
# -------------------------------------------------
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("model/bert_greenwashing")
    model = AutoModelForSequenceClassification.from_pretrained("model/bert_greenwashing")
    model.eval()
    return tokenizer, model

tokenizer, model = load_model()

# -------------------------------------------------
# Risk threshold
# -------------------------------------------------
HIGH_RISK_THRESHOLD = 0.65

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def predict_claims(sentences):
    rows = []

    for s in sentences:
        inputs = tokenizer(
            s,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )

        with torch.no_grad():
            probs = torch.softmax(model(**inputs).logits, dim=1)

        score = probs[0][1].item()

        rows.append({
            "sentence": s,
            "probability": round(score, 3),
            "high_risk": score >= HIGH_RISK_THRESHOLD
        })

    return pd.DataFrame(rows)


def company_name_from_file(file):
    return os.path.splitext(file.name)[0]


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🌱 Greenwashing Risk Assessment")
st.caption("Portfolio-Level ESG Risk Analysis for Investors & Auditors")

uploaded_files = st.file_uploader(
    "Can Upload Multiple ESG / Sustainability Reports (PDF)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    portfolio = []

    with st.spinner("Analyzing reports..."):
        for file in uploaded_files:
            company = company_name_from_file(file)

            raw_text = read_pdf(file)
            sentences = pdf_text_to_atomic_sentences(raw_text)
            df = predict_claims(sentences)

            total = len(df)
            high_risk = df["high_risk"].sum()
            risk = high_risk / total if total else 0

            portfolio.append({
                "company": company,
                "risk_exposure": risk,
                "total_claims": total,
                "high_risk_claims": high_risk,
                "details": df[df["high_risk"]]
            })

    portfolio_df = pd.DataFrame(portfolio).sort_values(
        by="risk_exposure",
        ascending=False
    )

    # -------------------------------------------------
    # Portfolio Bar Chart
    # -------------------------------------------------
    st.subheader("📊 Company-wise Greenwashing Risk")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(
        portfolio_df["company"],
        portfolio_df["risk_exposure"] * 100
    )
    ax.set_ylabel("Greenwashing Risk (%)")
    ax.set_xlabel("Company")
    ax.set_title("Greenwashing Risk Exposure by Company")
    plt.xticks(rotation=45, ha="right")

    st.pyplot(fig)

    # -------------------------------------------------
    # Company Ranking Table
    # -------------------------------------------------
    st.subheader("🏢 Company Risk Ranking")

    ranking_df = portfolio_df[[
        "company",
        "risk_exposure",
        "high_risk_claims",
        "total_claims"
    ]].copy()

    ranking_df["risk_exposure"] = (
        ranking_df["risk_exposure"] * 100
    ).round(1)

    ranking_df.rename(columns={
        "risk_exposure": "Greenwashing Risk (%)",
        "high_risk_claims": "High-Risk Claims",
        "total_claims": "Total ESG Claims"
    }, inplace=True)

    st.dataframe(ranking_df, width="stretch")

    # -------------------------------------------------
    # High-Risk Evidence (Expandable)
    # -------------------------------------------------
    st.subheader("🔍 High-Risk Claims by Company")

    for _, row in portfolio_df.iterrows():
        with st.expander(f"{row['company']} – High-Risk Claims"):
            if row["details"].empty:
                st.write("No high-risk claims detected.")
            else:
                st.dataframe(
                    row["details"][["sentence", "probability"]],
                    width="stretch"
                )

