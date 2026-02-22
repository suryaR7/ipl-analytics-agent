import streamlit as st
import pandas as pd
import plotly.express as px
import time
import base64

from agent import ask_agent
from database import load_csv_to_db
from auth import create_user_table, authentication_ui, logout


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="IPL Analytics AI",
    page_icon="🏏",
    layout="wide"
)

# --------------------------------------------------
# PREMIUM GRADIENT BACKGROUND
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

.glass-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
    from {opacity:0; transform: translateY(10px);}
    to {opacity:1; transform: translateY(0);}
}

.big-title {
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg,#ff9966,#ff5e62);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stButton>button {
    background: linear-gradient(90deg,#ff9966,#ff5e62);
    color:white;
    border:none;
    border-radius:10px;
    font-weight:600;
    height:3em;
    transition:0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------
create_user_table()
is_authenticated = authentication_ui()

if not is_authenticated:
    st.stop()


# --------------------------------------------------
# DATABASE LOAD
# --------------------------------------------------
@st.cache_resource
def initialize_database():
    load_csv_to_db()

initialize_database()


# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "latest_df" not in st.session_state:
    st.session_state.latest_df = None

if "latest_sql" not in st.session_state:
    st.session_state.latest_sql = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.success(f"Logged in as {st.session_state.username}")
logout()

st.sidebar.title("🏏 IPL Analytics")

page = st.sidebar.radio(
    "Navigate",
    ["💬 Chat Assistant", "📊 Dashboard", "📜 Query History"]
)


# ==================================================
# 💬 CHAT PAGE
# ==================================================
if page == "💬 Chat Assistant":

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='big-title'>IPL Analytics AI</div>", unsafe_allow_html=True)
    st.caption("Natural Language → SQL → Interactive Insights")

    user_question = st.text_input(
        "Ask anything about IPL:",
        placeholder="Example: Compare Dhoni and Rohit for most sixes"
    )

    submit = st.button("🚀 Analyze")

    if submit and user_question:

        with st.spinner("Analyzing with AI..."):
            time.sleep(0.8)

            response = ask_agent(user_question)

        # SAFE UNPACK
        if not response:
            st.error("Agent failed to respond.")
            st.stop()

        result, generated_sql = response

        # If SQL error returned
        if isinstance(generated_sql, str) and generated_sql.startswith("ERROR"):
            st.error(generated_sql)
            st.stop()

        if not result:
            st.warning("No results found.")
            st.stop()

        # Convert to DataFrame
        df = pd.DataFrame(result)
        df.columns = df.columns.map(str)

        # Save for dashboard
        st.session_state.latest_df = df
        st.session_state.latest_sql = generated_sql
        st.session_state.history.append(user_question)

        # IPL Logo Splash
        try:
            logo_placeholder = st.empty()
            with open("ipl_logo.png", "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()

            logo_html = f"""
            <div style="text-align:center;">
                <img src="data:image/png;base64,{logo_base64}" width="320">
            </div>
            """

            logo_placeholder.markdown(logo_html, unsafe_allow_html=True)
            time.sleep(1.2)
            logo_placeholder.empty()
        except:
            pass

        # SQL EXPANDER
        with st.expander("🧠 View Generated SQL"):
            st.code(generated_sql, language="sql")

        # METRICS
        col1, col2 = st.columns(2)
        col1.metric("Rows Returned", len(df))
        col2.metric("Columns", len(df.columns))

        st.markdown("---")

        # VISUALIZATION
        st.subheader("📊 Interactive Visualization")

        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=["int64", "float64"]).columns.tolist()

        if len(df) == 1 and len(numeric_cols) == 1:
            st.metric("Result", df[numeric_cols[0]].iloc[0])

        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            fig = px.bar(
                df,
                x=categorical_cols[0],
                y=numeric_cols[0],
                text=numeric_cols[0],
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif len(numeric_cols) >= 2:
            fig = px.line(
                df,
                y=numeric_cols,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.dataframe(df, use_container_width=True)

        st.subheader("📋 Data Table")
        st.dataframe(df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 📊 DASHBOARD PAGE
# ==================================================
elif page == "📊 Dashboard":

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("## 📊 Dynamic Dashboard")

    df = st.session_state.latest_df

    if df is None:
        st.info("Run a query first in Chat Assistant.")
        st.stop()

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["int64", "float64"]).columns.tolist()

    if len(df) == 1 and len(numeric_cols) == 1:

        value = df[numeric_cols[0]].iloc[0]
        st.metric("Key Insight", value)

        gauge_df = pd.DataFrame({
            "Metric": ["Value"],
            "Amount": [value]
        })

        fig = px.bar(
            gauge_df,
            x="Metric",
            y="Amount",
            text="Amount",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:

        fig = px.bar(
            df,
            x=categorical_cols[0],
            y=numeric_cols[0],
            text=numeric_cols[0],
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif len(numeric_cols) >= 2:

        fig = px.line(
            df,
            y=numeric_cols,
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==================================================
# 📜 QUERY HISTORY
# ==================================================
elif page == "📜 Query History":

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("## 🕒 Recent Queries")

    if st.session_state.history:
        for q in reversed(st.session_state.history[-10:]):
            st.markdown(f"• {q}")
    else:
        st.info("No queries yet.")

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + SQLite + Groq LLM")
