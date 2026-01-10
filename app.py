from pandas.errors import EmptyDataError

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # reset pointer (مهم جدًا)
        uploaded_file.seek(0)

        data = pd.read_csv(
            uploaded_file,
            sep=None,              # يحدد الفاصل تلقائي
            engine="python",
            encoding_errors="ignore"
        )

    except EmptyDataError:
        st.error("❌ Pandas لم يتمكن من قراءة الملف رغم أنه غير فارغ.")
        st.stop()

    except Exception as e:
        st.error(f"❌ خطأ أثناء قراءة الملف: {e}")
        st.stop()

    # تحقق نهائي
    if data.empty or data.columns.size == 0:
        st.error("❌ الملف تم قراءته لكن لا يحتوي على بيانات صالحة.")
        st.stop()
