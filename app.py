import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO

st.set_page_config(page_title="Files Converter", layout="wide")

st.markdown("""
    <style>
        .main { background-color:rgb(88, 139, 215); }
        .stButton button { background-color:rgb(36, 129, 39); color: white; border-radius: 8px; }
        .stCheckbox label { font-weight: bold; }
        .stRadio label { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📂 Files Converter & Cleaner")
st.write("Easily convert and clean your files with just a few clicks.")

st.markdown("---")

files = st.file_uploader("📥 Upload CSV files", type=["csv"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1]
        df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)
        
        df.columns = df.columns.str.strip().str.replace(":", "\\:")
        
        with st.expander(f"🔍 File: {file.name} - Preview"):
            st.dataframe(df.head())
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.checkbox(f"🗑 Remove Duplicates - {file.name}"):
                df = df.drop_duplicates()
                st.success("Duplicates Removed")
                st.dataframe(df.head())
        
        with col2:
            if st.checkbox(f"🔄 Fill Missing Values - {file.name}"):
                df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
                st.success("Missing values filled with mean")
                st.dataframe(df.head())
        
        selected_columns = st.multiselect(f"🎯 Select Columns - {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]
        st.dataframe(df.head())

        # Ensure there is at least one numeric column
        numeric_df = df.select_dtypes(include=["number"])
        if numeric_df.empty:
            df["Generated_Numeric_Column"] = range(1, len(df) + 1)
            numeric_df = df[["Generated_Numeric_Column"]]

        if st.checkbox(f"📊 Show Chart - {file.name}"):
            numeric_df = df.select_dtypes(include=["number"]).apply(pd.to_numeric, errors="coerce")
            
            if numeric_df.shape[1] >= 2:  # Agar 2 ya zyada numeric columns hain
                chart = alt.Chart(numeric_df.reset_index()).mark_bar().encode(
                    x=alt.X(numeric_df.columns[0], title="Category"),
                    y=alt.Y(numeric_df.columns[1], title="Value"),
                    tooltip=numeric_df.columns[:2]
                ).properties(width=700, height=400)
                st.altair_chart(chart, use_container_width=True)
            
            elif numeric_df.shape[1] == 1:  # Agar sirf 1 numeric column hai
                df["Index"] = range(1, len(df) + 1)  # Ek Index column add karna
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X("Index", title="Index"),
                    y=alt.Y(numeric_df.columns[0], title="Value"),
                    tooltip=["Index", numeric_df.columns[0]]
                ).properties(width=700, height=400)
                st.altair_chart(chart, use_container_width=True)

            else:
                st.warning("⚠ No numeric columns available for chart.")

        st.markdown("---")
        format_choice = st.radio(f"🔄 Convert {file.name} to:", ("CSV", "Excel"), key=file.name)
        
        if st.button(f"💾 Download {file.name} as {format_choice}"):
            output = BytesIO()
            if format_choice.lower() == "csv":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.replace(ext, "csv")
            else:
                df.to_excel(output, index=False, engine="openpyxl")
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.replace(ext, "xlsx")
            
            output.seek(0)
            st.download_button("⬇ Download File", data=output, file_name=new_name, mime=mime)
            
        st.success("✅ Processing Complete!")
