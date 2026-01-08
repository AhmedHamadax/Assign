import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.title("Order Processing App (Excel version)")
st.write("Upload your Excel file to process the orders.")

# Upload Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        data = pd.read_excel(uploaded_file)
    except ValueError:
        st.error("The uploaded Excel file is empty or invalid.")
        st.stop()

    # Check if dataframe has columns
    if data.empty or data.columns.size == 0:
        st.error("The uploaded Excel file has no columns or data.")
        st.stop()

    # Ensure phone_number is string
    data.phone_number = data.phone_number.astype(str)

    # Remove leading '2' if present
    start_2 = data['phone_number'].apply(lambda x: x[0] == '2')
    data.loc[start_2, 'phone_number'] = data.loc[start_2, 'phone_number'].apply(lambda x: x[2:])

    # Create order_code
    data['order_code'] = "20" + data["phone_number"]

    # Keep only first name
    data.customer_name = data.customer_name.apply(lambda x: x.split(" ")[0])

    # SKU mappings
    mapping_for_face = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":2, "AllureFES2":1,
        "6G7ODORP":2, "Allure15948":1, "BDHSOCZC": np.nan, "Allure12345": np.nan,
        "TNQUOCHL": np.nan, 'EOQDNN83':1
    }

    mapping_for_eye = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":2, "AllureFES2":1,
        "6G7ODORP":np.nan, "Allure15948":np.nan, "BDHSOCZC": 1,
        "Allure12345": 1, "TNQUOCHL": 2, 'EOQDNN83':1
    }

    mapping_for_sun = {
        "L3CEGUOR":1, "AllureFESS3":1, "GOGWEZ84":np.nan, "AllureFES2":np.nan,
        "6G7ODORP":1, "Allure15948":np.nan, "BDHSOCZC": np.nan,
        "Allure12345": np.nan, "TNQUOCHL": 1
    }

    # Compute serum counts
    data['Face Serum Count'] = pd.to_numeric((data.sku_code.map(mapping_for_face)) * data.sku_pieces, errors='coerce').astype("Int64")
    data['Eye Serum Count'] = pd.to_numeric((data.sku_code.map(mapping_for_eye)) * data.sku_pieces, errors='coerce').astype("Int64")
    data['Sunscreen Count'] = pd.to_numeric((data.sku_code.map(mapping_for_sun)) * data.sku_pieces, errors='coerce').astype("Int64")

    # Aggregate by order_code
    data = data.groupby("order_code", as_index=False).agg({
        "order_code": "first",
        'COD': "first",
        'customer_name': 'first',
        "Face Serum Count": "sum",
        "Eye Serum Count": "sum",
        "Sunscreen Count": "sum",
    })

    # Convert counts to string
    data = data.astype({
        "Face Serum Count": str,
        "Eye Serum Count": str,
        "Sunscreen Count": str
    })

    # Create final order description
    data["Final Order"] = (
        (data['Face Serum Count'] > '0') * (data['Face Serum Count'].astype(str) + " سيرم بشرة ") +
        (data['Eye Serum Count'] > '0') * (data['Eye Serum Count'].astype(str) + " سيرم عين ") +
        (data['Sunscreen Count'] > '0') * (data['Sunscreen Count'].astype(str) + " صان اسكرين ")
    )
    data['Face Serum Count']=data['Final Order']
    st.write("Processed Data:")
    st.dataframe(data)
    
    # Convert dataframe to Excel in memory
    def convert_df_to_excel(df):
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return output

    excel_data = convert_df_to_excel(data)

    st.download_button(
        label="Download Processed Excel",
        data=excel_data,
        file_name='Final_Orders.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


