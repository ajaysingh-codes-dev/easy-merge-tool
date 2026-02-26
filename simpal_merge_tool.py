import pandas as pd
import streamlit as st
from io import BytesIO

def read_df(file):
    try:
        file_ex = {
            "csv": pd.read_csv,
            "json": pd.read_json,
            "xlsx": pd.read_excel,
            "xls": pd.read_excel
        }

        if file is None:
            return None

        extension = file.name.split(".")[-1].lower()

        if extension in file_ex:
            return file_ex[extension](file)
        else:
            st.error("Unsupported file extension")
            return None

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


def clean_columns(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def get_common_columns(df1, df2):
    common_col = list(df1.columns.intersection(df2.columns))

    if len(common_col) == 0:
        st.error("No common columns found. Cannot merge.")
        st.stop()

    return common_col


def get_merge_type():
    return st.selectbox(
        "Available merge types:",
        ["inner", "outer", "left", "right"]
    )


def perform_merge(df1, df2, column, merge_type):
    return pd.merge(df1, df2, on=column, how=merge_type)


def save_df(df):
    option = st.radio("Choose file format:", ("csv", "excel", "json"))

    if option == "csv":
        data = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data, "merged.csv", "text/csv")

    elif option == "excel":
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            "Download Excel",
            output.getvalue(),
            "merged.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif option == "json":
        data = df.to_json(orient="records", indent=4).encode("utf-8")
        st.download_button("Download JSON", data, "merged.json", "application/json")


def main():
    st.set_page_config(page_title="Smart File Merger", layout="wide")
    st.markdown("<h1 style='text-align: center;'>Smart File Merger</h1>", unsafe_allow_html=True)

    # 1. Sidebar for Uploads
    with st.sidebar:
        st.header("Upload Data")
        file1 = st.file_uploader("First file", type=["csv", "json", "xlsx"])
        file2 = st.file_uploader("Second file", type=["csv", "json", "xlsx"])

    if file1 and file2:
        df1 = clean_columns(read_df(file1))
        df2 = clean_columns(read_df(file2))

        # 2. Configuration Section (Outside of a button!)

        tab1, tab2 = st.tabs(["📄 File 1 Preview", "📄 File 2 Preview"])
        with tab1:
            st.subheader("Your File_1 Data Before Mergeing Preview")
            st.dataframe(df1.head())
        with tab2:
            st.subheader("Your File_2 Data Before Mergeing Preview")
            st.dataframe(df2.head())

        col3, col4 = st.columns(2)
        
        common_cols = get_common_columns(df1, df2)
        
        if not common_cols:
            st.error("No common columns found to merge on!")
            return

        with col3:
            merge_col = st.selectbox("Select join column", common_cols)
        with col4:
            merge_type = st.selectbox("Select join type", ["inner", "outer", "left", "right"])

        # 3. Perform Merge
        merged_df = pd.merge(df1, df2, on=merge_col, how=merge_type)

        # 4. Display Results
        st.divider()
        

        st.subheader("Merged Data Preview")
        st.write(f"Shape: {merged_df.shape[0]} rows, {merged_df.shape[1]} columns")
        st.dataframe(merged_df.head(10), use_container_width=True)

        # 5. Export Section
        st.subheader("Export Result")
        save_df(merged_df)

    else:
        st.info("Please upload two files in the sidebar to begin.")

if __name__ == "__main__":
    main()