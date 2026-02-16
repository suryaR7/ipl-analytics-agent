import os
import re
from dotenv import load_dotenv
from groq import Groq

from database import get_schema, execute_query
from validator import validate_sql

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise Exception(" GROQ_API_KEY not found in .env file.")

# Model configurable via .env
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

client = Groq(api_key=api_key)


def format_schema(schema_rows):
    formatted = "Table: ipl\nColumns:\n"
    for col in schema_rows:
        formatted += f"- {col[1]} ({col[2]})\n"
    return formatted


def clean_sql_output(raw_output: str) -> str:
    """
    Cleans LLM output to extract pure SQL query.
    Removes markdown formatting and extra text.
    """

    # Remove markdown code blocks
    if "```" in raw_output:
        parts = raw_output.split("```")
        if len(parts) >= 2:
            raw_output = parts[1]

    # Remove leading "sql" if present
    raw_output = raw_output.replace("sql", "").strip()

    # Extract first SELECT statement using regex
    match = re.search(r"(SELECT .*?;)", raw_output, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()

    return raw_output.strip()


def ask_agent(question: str):

    schema = get_schema()
    schema_text = format_schema(schema)

    prompt = f"""
You are an IPL data analytics assistant.

STRICT RULES:
- Generate ONLY a valid SQLite SELECT query.
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT include backticks.
- Use exact column names from schema.
- End query with semicolon.

Database schema:
{schema_text}

User question:
{question}
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_sql = response.choices[0].message.content.strip()

        sql_query = clean_sql_output(raw_sql)

        print("\n Generated SQL:\n")
        print(sql_query)

        # Validate SQL safety
        validate_sql(sql_query)

        result = execute_query(sql_query)
        return result

    except Exception as e:
        print("Error:", str(e))
