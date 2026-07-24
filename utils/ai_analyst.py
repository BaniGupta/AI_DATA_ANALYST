from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

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
