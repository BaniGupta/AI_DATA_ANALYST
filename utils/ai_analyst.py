from unittest import result
from urllib import response

from google import genai
from dotenv import load_dotenv
import os
import json
from utils.analysis_tools import (
    get_column_summary,
    get_value_counts,
    get_correlation,
    calculate_basic_stat,
    group_and_aggregate,
    generate_plot,
    generate_group_plot

)

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def choose_tool(df, question):

    columns = df.columns.tolist()

    prompt = f"""
You are an AI data analyst.

The dataset has these columns:
{columns}

The user asked:
{question}

You have these analysis tools available:

1. column_summary
   Use when the user wants statistics about one column.
   Required argument: column

2. value_counts
   Use when the user wants the most common/frequent values in a column.
   Required argument: column

3. correlation
   Use this tool when the user wants a numerical measure of the relationship between two numerical columns.

    Examples:
    - What is the correlation between price and freight_value?
    - How strongly are review_score and delivery_delay_days related?
    - Is there a correlation between price and freight_value?

    Do NOT use this tool if the user is asking for a graph, plot, chart, visualization, or wants to see the relationship visually.

4. basic_stat
   Use when the user wants basic statistics (mean, sum, min, max, count,nunique) for a specific column.
   Required arguments: column, operation

5. group_and_aggregate

Use this tool when the user wants grouped summaries, comparisons, rankings, or aggregated statistics.

    Examples:
    - Average price by state
    - Total sales by seller
    - Top 10 customers by orders
    - Payment type distribution
    - Monthly sales
    Required arguments:
    - group_column
    - value_column
    - operation

    Optional arguments:
    - sort_order
    - limit
    - display_type

    Supported display types:
    - table
    - bar
    - pie
    - line

Choose the display type based on the result, not only on the wording of the question.

    Use:
    - table for single values or single-row results.
    - bar for comparisons across categories or Top N results.
    - pie for proportions of a few categories.
    - line for trends over time.

    Even if the user simply says "show", choose the display type that best communicates the result.

6. plot_chart

    Use this tool only when no aggregation is required and the user wants a visualization.

    Examples:
    - Show the distribution of price
    - Plot payment_value distribution
    - Show the relationship between price and freight_value
    - Scatter plot of review_score vs delivery_delay_days
    Supported chart types:
    - histogram
    - scatter

    Arguments:
    - chart_type
    - x_column
    - y_column (optional)

    Use histogram for the distribution of a single numerical column.

    Use scatter for visualizing the relationship between two numerical columns.

    Do NOT use this tool for grouped summaries such as:
    - Average by category
    - Count by category
    - Sum by category
    - Top N results
    - Category comparisons
    Use group_and_aggregate for those instead.

Choose the most appropriate tool.

Return ONLY valid JSON.

Examples:

{{
    "tool": "column_summary",
    "column": "price"
}}

or

{{
    "tool": "correlation",
    "column1": "delivery_delay_days",
    "column2": "review_score"
}}

or

{{
    "tool": "basic_stat",
    "column": "price",
    "operation": "mean"
}}

or

{{
    "tool": "group_and_aggregate",
    "group_column": "order_status",
    "value_column": "price",
    "operation": "mean",
    "sort_order": "desc",
    "limit": 1
}}

or

{{
    "tool": "plot_chart",
    "chart_type": "scatter",
    "x_column": "delivery_delay_days",
    "y_column": "review_score"
}}

or

{{
    "tool": "plot_chart",
    "chart_type": "histogram",
    "x_column": "price"
}}

or

{{
    
    "tool": "group_and_aggregate",
    "group_column": "customer_state",
    "value_column": "price",
    "operation": "mean",
    "display_type": "bar"

}}
Use only columns that actually exist in the dataset.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    clean_response = response.text.strip()

    clean_response = clean_response.replace("```json", "")
    clean_response = clean_response.replace("```", "")
    clean_response = clean_response.strip()

    return json.loads(clean_response)

def run_analysis(df, question):

    tool_choice = choose_tool(df, question)
    print(tool_choice)

    tool = tool_choice["tool"]

    if tool == "column_summary":

        column = tool_choice["column"]

        result = get_column_summary(
            df,
            column
        )

    elif tool == "value_counts":

        column = tool_choice["column"]

        result = get_value_counts(
            df,
            column
        )

    elif tool == "correlation":

        column1 = tool_choice["column1"]
        column2 = tool_choice["column2"]

        result = get_correlation(
            df,
            column1,
            column2
        )

    elif tool == "basic_stat":

        column = tool_choice["column"]
        operation = tool_choice["operation"]

        result = calculate_basic_stat(
            df,
            column,
            operation
        )

    elif tool == "group_and_aggregate":

        group_column = tool_choice["group_column"]
        value_column = tool_choice["value_column"]
        operation = tool_choice["operation"]
        sort_order = tool_choice.get("sort_order", "desc")
        limit = tool_choice.get("limit", 10),
        display_type = tool_choice.get("display_type", "table")
    # Fallback rule
        if (
            "highest" in question.lower()
            or "most" in question.lower()
            or "maximum" in question.lower()
        )   and "top" not in question.lower():
                limit = 1

        result = group_and_aggregate(
    df,
    group_column,
    value_column,
    operation,
    sort_order,
    limit
    )

        if display_type != "table":
            return generate_group_plot(
                result,
                display_type
        )

        return result

    elif tool == "plot_chart":

        chart_type = tool_choice["chart_type"]
        x_column = tool_choice["x_column"]

        y_column = tool_choice.get("y_column")
        aggregation = tool_choice.get("aggregation")

        return generate_plot(
            df,
            chart_type,
            x_column,
            y_column,
            aggregation
    )

    else:
        result = {
            "error": "No suitable analysis tool found."
        }

    return result



def analyze_question(df, question):

    instruction = interpret_question(df, question)

    operation = instruction["operation"]
    column = instruction["column"]

    result = calculate_basic_stat(
        df,
        column,
        operation
    )

    return result


def interpret_question(df, question):

    columns = df.columns.tolist()

    prompt = f"""
    You are a data analysis query interpreter.

    Available columns:
    {columns}

    User question:
    {question}

    Convert the user's question into a structured analysis instruction.

    Return ONLY valid JSON in this format:

    {{
        "operation": "mean",
        "column": "price"
    }}

    Supported operations:
    mean, sum, min, max, count.

    Choose only a column that exists in the available columns.
    """

    response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
    )

    instruction = json.loads(response.text)

    return instruction
