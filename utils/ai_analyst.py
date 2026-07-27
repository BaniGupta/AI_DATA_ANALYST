from urllib import response

from google import genai
from dotenv import load_dotenv
import os
import json
from utils.analysis_tools import (
    get_column_summary,
    get_value_counts,
    get_correlation,
    calculate_basic_stat
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
   Use when the user wants to know the relationship between two numerical columns.
   Required arguments: column1, column2

4. basic_stat
   Use when the user wants basic statistics (mean, sum, min, max, count)
   Required arguments: column, operation

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
