import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from pandas.errors import EmptyDataError

st.set_page_config(page_title="Order Processing App", layout="wide")
st.title("Order Processing App (CSV / TSV version)")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)

        # 🔥 الفايل بتاعك TAB separated + UTF-16
        try:
            data = pd.read_csv(
                uploaded_file,
                sep="\t",
                encoding="utf-16"
            )
        except Exception:
            uploaded_file.seek(0)
            data = pd.read_csv(
                uploaded_file,
                sep="\t",
                engine="python",
                encoding_errors="ignore"
            )

    except EmptyDataError:
        st.error("❌ الملف فاضي.")
        st.stop()

    # ---------------- تنظيف أسماء الأعمدة ----------------
    data.columns = (
        data.columns
        .astype(str)
        .str.replace("\x00", "", regex=False)
        .str.strip()
        .str.lower()
    )

    # ---------------- Validation ----------------
    required_cols = [
        "phone_number",
        "customer_name",
        "sku_code",
        "sku_pieces",
        "cod"
    ]

    missing = [c for c in required_cols if c not in data.colu_]()
