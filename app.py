import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from pandas.errors import EmptyDataError

# -------------------- UI --------------------
st.set_page_config(page_title="Order Processing App", layout="wide")
st.title("Order Processing App (CSV version)")
st.write("ارفع ملف CSV لمعالجة الأوردرات")

# -------------------- Upload CSV --------------------
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # مهم جدًا مع Streamlit
        uploaded_file.seek(0)

        data = pd.read_csv(
            uploaded_file,
            sep=None,                # يحدد الفاصل تلقائي (, ;)
            engine="python",
            encoding_errors="ignore"
        )

    except EmptyDataError:
        st.error("❌ الملف لا يحتوي على بيانات صالحة.")
        st.stop()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
        st.stop()

    # -------------------- Validation --------------------
    if data.empty or len(data.columns) == 0:
        st.error("❌ الملف فاضي أو بدون أعمدة.")
        st.stop()

    required_cols = [
        "phone_number",
        "customer_name",
        "sku_code",
        "sku_pieces",
        "COD"
    ]

    missing_cols = [c for c in required_cols if c not in data.columns]
    if missing_cols:
        st.error(f"❌ الأعمدة التالية مفقودة: {missing_cols}")
        st.stop()

    # -------------------- Processing --------------------
    data["phone_number"] = data["phone_number"].astype(str)

    # إزالة 2 في أول الرقم
    mask = data["phone_number"].str.startswith("2")
    data.loc[mask, "phone_number"] = data.loc[mask, "phone_number"].str[2:]

    # order_code
    data["order_code"] = "20" + data["phone_number"]

    # الاسم الأول فقط
    data["customer_name"] = data["customer_name"].astype(str).str.split().str[0]

    # -------------------- SKU Mappings --------------------
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

    # -------------------- Counts --------------------
    data["Face Serum Count"] = (
        data["sku_code"].map(mapping_for_face) * data["sku_pieces"]
    ).fillna(0).astype(int)

    data["Eye Serum Count"] = (
        data["sku_code"].map(mapping_for_eye) * data["sku_pieces"]
    ).fillna(0).astype(int)

    data["Sunscreen Count"] = (
        data["sku_code"].map(mapping_for_sun) * data["sku_pieces"]
    ).fillna(0).astype(int)

    # -------------------- Grouping --------------------
    data = data.groupby("order_code", as_index=False).agg({
        "order_code": "first",
        "COD": "first",
        "customer_name": "first",
        "Face Serum Count": "sum",
        "Eye Serum Count": "sum",
        "Sunscreen Count": "sum",
    })

    # -------------------- Final Order Text --------------------
    data["Final Order"] = (
        (data["Face Serum Count"] > 0) * (data["Face Serum Count"].astype(str) + " سيرم بشرة ") +
        (data["Eye Serum Count"] > 0) * (data["Eye Serum Count"].astype(str) + " سيرم عين ") +
        (data["Sunscreen Count"] > 0) * (data["Sunscreen Count"].astype(str) + " صان اسكرين ")
    )

    # -------------------- Preview --------------------
    st.subheader("Processed Data")
    st.dataframe(data, use_container_width=True)

    # -------------------- Download Excel --------------------
    def convert_df_to_excel(df):
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return output

    st.download_button(
        label="⬇️ Download Processed Excel",
        data=convert_df_to_excel(data),
        file_name="Final_Orders.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
