import pandas as pd


def get_column_summary(df, column):
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist."}

    return df[column].describe().to_dict()


def get_value_counts(df, column, top_n=10):
    if column not in df.columns:
        return {"error": f"Column '{column}' does not exist."}

    return (
        df[column]
        .value_counts()
        .head(top_n)
        .to_dict()
    )


def get_correlation(df, column1, column2):
    if column1 not in df.columns or column2 not in df.columns:
        return {"error": "One or both columns do not exist."}

    return df[[column1, column2]].corr().iloc[0, 1]

def calculate_basic_stat(df, column, operation):

    if column not in df.columns:
        return "Column not found."

    if operation == "mean":
        return df[column].mean()

    elif operation == "sum":
        return df[column].sum()

    elif operation == "min":
        return df[column].min()

    elif operation == "max":
        return df[column].max()

    elif operation == "count":
        return df[column].count()

    else:
        return "Operation not supported."