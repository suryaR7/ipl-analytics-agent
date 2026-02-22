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
You are an expert SQL generator for IPL cricket database.
Database table name: ipl

Columns include (important ones):
- match_id
- inning
- over
- batter
- bowler
- runs_batter
- extra_runs
- total_runs
- dismissal_kind
- player_dismissed
- season
- batting_team
- bowling_team

CRICKET RULES & SQL LOGIC:
- Generate ONLY a valid SQLite SELECT query.
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT include backticks.
- Use exact column names from schema.
- End query with semicolon.
- Do not include commentary.


1. Comparison Between Players:
   - If user compares players (vs, compare, and, between):
       • Use WHERE batter IN (...)
       • Always use GROUP BY batter
       • Never filter only one player
       • Order by metric DESC

2. Sixes & Fours:
   - "most sixes" → runs_batter = 6
   - "most fours" → runs_batter = 4
   - Count using COUNT(*)

3. Ducks:
   - Duck = player scored total 0 runs in a match AND got dismissed
   - Must:
       GROUP BY match_id, batter
       HAVING SUM(runs_batter) = 0 AND COUNT(player_dismissed) > 0
   - Then count number of such matches per batter

4. More than X runs in a match:
   - GROUP BY match_id, batter
   - HAVING SUM(runs_batter) > X

5. Total Runs by Player:
   - SUM(runs_batter)
   - GROUP BY batter if multiple players

6. Strike Rate:
   - Strike Rate = (SUM(runs_batter) * 100.0) / COUNT(runs_batter)
   - Only count legal balls (assume every row is a ball faced)
   - GROUP BY batter

7. Batting Average:
   - Average = SUM(runs_batter) / COUNT(DISTINCT match_id where dismissed)
   - Only count matches where player was dismissed

8. Highest Score in a Match:
   - GROUP BY match_id, batter
   - ORDER BY SUM(runs_batter) DESC
   - LIMIT 1

9. Centuries:
   - Century = 100+ runs in a match
   - GROUP BY match_id, batter
   - HAVING SUM(runs_batter) >= 100

10. Half-Centuries:
   - 50–99 runs in a match
   - GROUP BY match_id, batter
   - HAVING SUM(runs_batter) BETWEEN 50 AND 99

11. Wickets:
   - Wicket = dismissal_kind IS NOT NULL
   - Exclude dismissal_kind = 'run out' when counting bowler wickets
   - GROUP BY bowler

12. Economy Rate:
   - Economy = SUM(total_runs) / (COUNT(*) / 6.0)
   - GROUP BY bowler

13. Matches Played:
   - COUNT(DISTINCT match_id)

14. Season Filter:
   - If user mentions year or season:
       WHERE season = XXXX

15. Team Based Queries:
   - Use batting_team or bowling_team accordingly
   - GROUP BY team if comparison

16. Always:
   - Use proper aggregation
   - Avoid returning ball-level rows unless explicitly asked
   - Use GROUP BY when aggregation is needed
   - Use ORDER BY DESC for "most", "highest", "top"
   - Use LIMIT when user says "top 5", etc.

17. Never:
   - Return result for only one player if multiple players mentioned
   - Mix aggregated and non-aggregated columns without GROUP BY
   - Add explanations

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
        return result,sql_query

    except Exception as e:
        print("Error:", str(e))
