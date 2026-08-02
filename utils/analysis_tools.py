import pandas as pd
import plotly.express as px

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
    """
    Calculate the correlation coefficient between two columns.
    """
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


def group_and_aggregate(
    df,
    group_column,
    value_column,
    operation="mean",
    sort_order="desc",
    limit=10
):
    if group_column not in df.columns:
        return {"error": f"Column '{group_column}' not found."}

    if value_column not in df.columns:
        return {"error": f"Column '{value_column}' not found."}

    grouped = df.groupby(group_column)[value_column]

    if operation == "mean":
        result = grouped.mean()

    elif operation == "sum":
        result = grouped.sum()

    elif operation == "count":
        result = grouped.count()

    elif operation == "max":
        result = grouped.max()

    elif operation == "min":
        result = grouped.min()

    elif operation == "nunique":
        result = grouped.nunique()

    else:
        return {"error": "Unsupported aggregation operation."}

    

    result = result.sort_values(
    ascending=(sort_order == "asc")
)
    
    # Take only required rows
    result = result.head(limit)

    # Convert Series to DataFrame
    result = result.reset_index()

    # Rename nunique column
    if operation == "nunique":
        result = result.rename(
            columns={
                value_column: f"unique_{value_column}_count"
        }
    )

    return result


def generate_plot(
    df,
    chart_type,
    x_column,
    y_column=None,
    aggregation=None
):
    if isinstance(df, dict):
        return df

    if df is None :
        return {"error": "No data available for plotting."}

    if chart_type == "histogram":

        if x_column not in df.columns:
            return {"error": f"Column '{x_column}' not found."}

        fig = px.histogram(
            df,
            x=x_column,
            title=f"Distribution of {x_column}"
        )

        return fig

    elif chart_type == "scatter":

        if x_column not in df.columns or y_column not in df.columns:
            return {"error": "Invalid columns."}

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}"
        )

        return fig

    else:
        return {"error": "Chart type not supported."}


def generate_group_plot(df, display_type):

    if isinstance(df, dict):
        return df

    if df is None or len(df.columns) < 2:
        return {"error": "Not enough columns to generate a plot."}

    x_column = df.columns[0]
    y_column = df.columns[1]

    if display_type == "bar":

        fig = px.bar(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}"
        )

        return fig

    elif display_type == "pie":

        fig = px.pie(
            df,
            names=x_column,
            values=y_column,
            title=f"{y_column} by {x_column}"
        )

        return fig

    elif display_type == "line":

        fig = px.line(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}"
        )

    elif display_type == "table":
        return df
    

    return df

def generate_insights(df):

    if df is None or len(df.columns) < 2:
        return ""

    x_column = df.columns[0]
    y_column = df.columns[1]

    highest_row = df.loc[df[y_column].idxmax()]
    lowest_row = df.loc[df[y_column].idxmin()]

    average_value = round(df[y_column].mean(), 2)

    top_three = df.nlargest(3, y_column)

    top_values = []

    for _, row in top_three.iterrows():
        top_values.append(
            f"{row[x_column]} ({round(row[y_column], 2)})"
        )

    insight = f"""
Highest value:
{highest_row[x_column]} ({round(highest_row[y_column], 2)})

Lowest value:
{lowest_row[x_column]} ({round(lowest_row[y_column], 2)})

Average value:
{average_value}

Top 3 values:
{", ".join(top_values)}
"""

    return insight