from pathlib import Path

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Loan Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    path = Path(__file__).parent / "loan_clean.csv"
    return pd.read_csv(path)

df = load_data()

st.title("📊 لوحة تحكم القروض")
st.write(
    "استكشاف طلبات القروض ومؤشرات الموافقة "
    "حسب المنطقة والمستوى التعليمي والدخل."
)

st.sidebar.header("فلاتر البيانات")

regions = st.sidebar.multiselect(
    "المنطقة",
    options=sorted(df["Property_Area"].dropna().unique()),
    default=sorted(df["Property_Area"].dropna().unique())
)

education = st.sidebar.radio(
    "المستوى التعليمي",
    ["الكل"] + sorted(df["Education"].dropna().unique())
)

income_min = int(df["ApplicantIncome"].min())
income_max = int(df["ApplicantIncome"].max())

if income_min < income_max:
    max_income = st.sidebar.slider(
        "الحد الأعلى لدخل المتقدم",
        min_value=income_min,
        max_value=income_max,
        value=income_max
    )
else:
    max_income = income_max
    st.sidebar.info("جميع المتقدمين لديهم الدخل نفسه.")

filtered = df[
    df["Property_Area"].isin(regions)
    & (df["ApplicantIncome"] <= max_income)
].copy()

if education != "الكل":
    filtered = filtered[filtered["Education"] == education]

if filtered.empty:
    st.warning("لا توجد طلبات تطابق الفلاتر. جرّبي تعديل الاختيارات.")
    st.stop()

total = len(filtered)
approval_rate = filtered["Loan_Status"].mean() * 100
median_loan = filtered["LoanAmount"].median()

m1, m2, m3 = st.columns(3)

m1.metric("عدد الطلبات", f"{total:,}")
m2.metric("نسبة الموافقة", f"{approval_rate:.1f}%")
m3.metric("وسيط مبلغ القرض", f"{median_loan:,.1f}")

st.caption(
    "مبالغ القروض معروضة بوحدة البيانات الأصلية. "
    "حالة القرض: 1 = موافقة، 0 = رفض."
)

st.subheader("الرسومات التفاعلية")

numeric_columns = filtered.select_dtypes(include="number").columns.tolist()

selected_column = st.selectbox(
    "اختاري عمودًا رقميًا لعرض توزيعه",
    numeric_columns,
    index=numeric_columns.index("ApplicantIncome")
)

sns.set_theme(style="whitegrid")
left, right = st.columns(2)

with left:
    st.write("**حالة القروض حسب المنطقة**")

    fig1, ax1 = plt.subplots(figsize=(7, 4))

    sns.countplot(
        data=filtered,
        x="Property_Area",
        hue="Loan_Status",
        palette={0: "#E59177", 1: "#43A6AC"},
        ax=ax1
    )

    ax1.set_xlabel("Property area")
    ax1.set_ylabel("Number of applications")
    ax1.legend(title="Status: 0=Rejected, 1=Approved")

    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with right:
    st.write(f"**توزيع {selected_column}**")

    values = filtered[selected_column].dropna()
    fig2, ax2 = plt.subplots(figsize=(7, 4))

    if values.empty:
        ax2.text(
            0.5, 0.5, "No numeric values",
            ha="center", va="center",
            transform=ax2.transAxes
        )
    else:
        sns.histplot(
            x=values,
            bins=20,
            color="#43A6AC",
            ax=ax2
        )

    ax2.set_xlabel(selected_column)
    ax2.set_ylabel("Frequency")

    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

with st.expander("عرض البيانات بعد تطبيق الفلاتر"):
    st.dataframe(filtered, use_container_width=True)
