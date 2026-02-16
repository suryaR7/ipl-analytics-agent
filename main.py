import os
from database import load_csv_to_db
from agent import ask_agent

DB_NAME = "ipl.db"

if __name__ == "__main__":

    # Load DB only first time
    if not os.path.exists(DB_NAME):
        load_csv_to_db("ipl.csv")

    print("\n🏏 IPL Analytics Agent Ready!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Ask IPL Stats Question: ")

        if question.lower() == "exit":
            print("👋 Goodbye!")
            break

        try:
            ask_agent(question)
        except Exception as e:
            print("Error:", str(e))
