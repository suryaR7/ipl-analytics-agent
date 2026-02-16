FORBIDDEN_KEYWORDS = ["drop", "delete", "update", "alter", "insert"]

def validate_sql(query: str):

    lower_query = query.lower()

    for word in FORBIDDEN_KEYWORDS:
        if word in lower_query:
            raise Exception(f"Unsafe SQL detected: {word}")

    if not lower_query.strip().startswith("select"):
        raise Exception("Only SELECT statements are allowed.")

    return True
