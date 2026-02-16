import streamlit as st
from agent import ask_agent
from database import load_csv_to_db

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="IPL Analytics Agent",
    page_icon="🏏",
    layout="centered"
)

st.title("🏏 IPL Analytics Agent")
st.markdown("Ask questions about IPL data using natural language.")

# ----------------------------
# Load Database (Run Once)
# ----------------------------
@st.cache_resource
def initialize_database():
    load_csv_to_db("ipl.csv")

initialize_database()

# ----------------------------
# User Input
# ----------------------------
user_question = st.text_input(
    "Ask IPL Stats Question:",
    placeholder="Example: Most runs by batsman in 2011"
)

# ----------------------------
# Submit Button
# ----------------------------
if st.button("Submit") and user_question:

    with st.spinner("Analyzing your question..."):

        try:
            result = ask_agent(user_question)

            if not result:
                st.warning("No results found.")
            else:
                st.success("Query Result:")
                st.dataframe(result)

        except Exception as e:
            st.error(f"Error: {str(e)}")
