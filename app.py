
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.data_profiler import profile_data
from utils.ai_analyst import analyze_question
from utils.ai_analyst import run_analysis

st.title("AI Data Analyst 📊")

st.write("Upload a CSV file to start analyzing your data.")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("Dataset loaded successfully!")

    st.write("### Data Preview")
    st.dataframe(df.head())

    profile = profile_data(df)

    st.write("### Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", profile["rows"])
    col2.metric("Columns", profile["columns"])
    col3.metric("Duplicates", profile["duplicate_rows"])


    st.write("### Column Information")

    column_info = pd.DataFrame({
        "Column": profile["column_names"],
        "Data Type": [
            profile["data_types"][col]
            for col in profile["column_names"]
        ],
        "Missing Values": [
            profile["missing_values"][col]
            for col in profile["column_names"]
        ],
        "Unique Values": [
            profile["unique_values"][col]
            for col in profile["column_names"]
        ]
    })

    st.dataframe(column_info)

    st.write("### 📈 Numerical Summary")

    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        st.dataframe(numeric_df.describe().round(2))
    else:
        st.info("No numerical columns found.")

    ### st.write("### 📊 Automatic Visualizations")

   ### numeric_columns = df.select_dtypes(include="number").columns.tolist()

    ###if numeric_columns:
       ### selected_column = st.selectbox(
           ### "Choose a numerical column",
           ### numeric_columns
        ###)
        ###st.write(f"#### Distribution of {selected_column}")
        ###st.bar_chart(
        ###df[selected_column].value_counts().sort_index()
    ###)
    ###else:
        ###st.info("No numerical columns available for visualization.")

    st.write("### Ask the AI Analyst")

    question = st.text_input(
        "Ask a question about your dataset:"
)

    if question:
        with st.spinner("Analyzing your question..."):
            result = run_analysis(df, question)

        st.write("### AI Response")

        if isinstance(result, dict) and "figure" in result:

            st.plotly_chart(
                result["figure"],
                use_container_width=True
            )

            st.write("### Insights")
            st.write(result["insights"])

        elif isinstance(result, go.Figure):

            st.plotly_chart(
            result,
            use_container_width=True
        )

        else:
            st.write(result)