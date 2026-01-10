import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from pandas.errors import EmptyDataError

# -------------------- UI --------------------
st.set_page_config(page_title="Order Processing App", layout="wide")
st.title("Order Processing App (CSV / TSV)")

uploaded_file = st.file_uploader("Choose your file", type=["csv"])

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)

        # قراءة الملف (UTF-16 + TAB separated)
        data = pd.read_csv(
            uploaded_file,
            sep="\t",
            encoding="utf-16"
        )

    except EmptyDataError:
        st.error("❌ الملف فاضي.")
        st.stop()
    except Exception as e:
        st.error(f"❌ خطأ أثناء قراءة الملف: {e}")
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

    missing_cols = [c for c in required_cols if c not in data.columns]
    if missing_cols:
        st.error(f"❌ الأعمدة التالية غير موجودة: {missing_cols}")
        st.write("الأعمدة الموجودة:", data.columns.tolist())
        st.stop()

    # ---------------- Processing ----------------
    data["phone_number"] = data["phone_number"].astype(str)

    # إزالة 2 من أول الرقم
    mask = data["phone_number"].str.startswith("2")
    data.loc[mask, "phone_number"] = data.loc[mask, "phone_number"].str[2:]

    # order_code
    data["order_code"] = "20" + data["phone_number"]

    # الاسم الأول فقط
    data["customer_name"] = data["customer_name"].astype(str).str.split().str[0]

    # ---------------- SKU mappings ----------------
    mapping_for_face = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":2, "AllureFES2":1,
        "6G7ODORP":2, "Allure15948":1, "BDHSOCZC": np.nan,
        "Allure12345": np.nan, "TNQUOCHL": np.nan, "EOQDNN83":1
    }

    mapping_for_eye = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":2, "AllureFES2":1,
        "6G7ODORP":np.nan, "Allure15948":np.nan, "BDHSOCZC": 1,
        "Allure12345": 1, "TNQUOCHL": 2, "EOQDNN83":1
    }

    mapping_for_sun = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":np.nan, "AllureFES2":np.nan,
        "6G7ODORP":1, "Allure15948":np.nan, "BDHSOCZC": np.nan,
        "Allure12345": np.nan, "TNQUOCHL": 1
    }

    # ---------------- Counts ----------------
    data["face serum count"] = (
        data["sku_code"].map(mapping_for_face) * data["sku_pieces"]
    ).fillna(0).astype(int)

    data["eye serum count"] = (
        data["sku_code"].map(mapping_for_eye) * data["sku_pieces"]
    ).fillna(0).astype(int)

    data["sunscreen count"] = (
        data["sku_code"].map(mapping_for_sun) * data["sku_pieces"]
    ).fillna(0).astype(int)

    # ---------------- Group ----------------
    data = data.groupby("order_code", as_index=False).agg({
        "order_code": "first",
        "cod": "first",
        "customer_name": "first",
        "face serum count": "sum",
        "eye serum count": "sum",
        "sunscreen count": "sum",
    })

    # ---------------- Final Order ----------------
    data["final order"] = (
        (data["face serum count"] > 0) * (data["face serum count"].astype(str) + " سيرم بشرة ") +
        (data["eye serum count"] > 0) * (data["eye serum count"].astype(str) + " سيرم عين ") +
        (data["sunscreen count"] > 0) * (data["sunscreen count"].astype(str) + " صان اسكرين ")
    )

    # ---------------- Preview ----------------
    st.subheader("Processed Data")
    st.dataframe(data, use_container_width=True)

    # ---------------- Download Excel ----------------
    def convert_to_excel(df):
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output

    st.download_button(
        "⬇️ Download Processed Excel",
        convert_to_excel(data),
        file_name="Final_Orders.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
