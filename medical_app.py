import pandas as pd
import plotly.express as px
import streamlit as st
import sqlite3
import google.generativeai as genai
import os

# Set Gemini API key
genai.configure(api_key="AIzaSyCSyVFb_Njud9aS6BpuNz-8CitZ8ogolYI")

st.set_page_config(page_title="Realtime Medical Dashboard",
                   page_icon='app icon.png',
                   layout='wide')


# Query input
st.subheader("Query the Medical Dataset")
user_query = st.text_input("Enter your query:")
st.sidebar.header("Select Filters:")

# Load medical data
@st.cache_data
def get_excel_data():
    df = pd.read_excel(
        io='medical_dataset_vitals.xlsx',
        engine='openpyxl',
        sheet_name='MedicalData'
    )
    return df

df = get_excel_data()

# Create an SQLite database in-memory
conn = sqlite3.connect(':memory:')
df.to_sql('medical_data', conn, index=False, if_exists='replace')

def query_to_sql(query):
    prompt = (
        f"Convert this natural language query into an SQL query:\n"
        f"Query: {query}\n"
        f"SQL Query:"
    )
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)   
    sql_query = response.choices[0].text.strip()
    return sql_query

def execute_sql_query(sql_query):
    try:
        result_df = pd.read_sql_query(sql_query, conn)
        return result_df
    except Exception as e:
        return str(e)

# Main Page
st.title(":bar_chart: Realtime Medical Dashboard")

# Top KPIs
avg_temp = round(df["Body_Temperature"].mean(), 1)
avg_pulse = round(df["Pulse_Rate"].mean(), 1)
avg_respiration = round(df["Respiration_Rate"].mean(), 1)
avg_bp = round(df["Blood_Pressure"].mean(), 1)
avg_oxygen = round(df["Blood_Oxygen"].mean(), 1)
avg_weight = round(df["Weight"].mean(), 1)
avg_glucose = round(df["Blood_Glucose_Level"].mean(), 1)

left_col, mid_col1, mid_col2, mid_col3, right_col = st.columns(5)

with left_col:
    st.subheader("Avg Body Temp:")
    st.subheader(f"{avg_temp} °C")

with mid_col1:
    st.subheader("Avg Pulse Rate:")
    st.subheader(f"{avg_pulse} bpm")

with mid_col2:
    st.subheader("Avg Respiration Rate:")
    st.subheader(f"{avg_respiration} bpm")

with mid_col3:
    st.subheader("Avg Blood Pressure:")
    st.subheader(f"{avg_bp} mmHg")

with right_col:
    st.subheader("Avg Blood Oxygen:")
    st.subheader(f"{avg_oxygen} %")

st.markdown("---")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Avg Weight:")
    st.subheader(f"{avg_weight} kg")

with right_col:
    st.subheader("Avg Blood Glucose:")
    st.subheader(f"{avg_glucose} mg/dL")

st.markdown("---")

if user_query:
    sql_query = query_to_sql(user_query)
    st.write(f"SQL Query: {sql_query}")
    
    result_df = execute_sql_query(sql_query)
    if isinstance(result_df, str):
        st.error(f"Error: {result_df}")
    else:
        st.dataframe(result_df)

        # Example visualizations for specific queries
        if "blood oxygen" in user_query.lower() and "bangalore" in user_query.lower() and "40" in user_query.lower():
            fig = px.bar(result_df, x="Name", y="Blood_Oxygen", title="Blood Oxygen Levels for Patients in Bangalore Older Than 40")
            st.plotly_chart(fig)

        # Pie chart for gender distribution in the dataset
        if "gender distribution" in user_query.lower():
            fig = px.pie(result_df, names='Gender', title='Gender Distribution in Medical Data')
            st.plotly_chart(fig)

        # Bar graph for average blood pressure by city
        if "average blood pressure" in user_query.lower() and "city" in user_query.lower():
            fig = px.bar(result_df, x="City", y="Blood_Pressure", title="Average Blood Pressure by City", color='City')
            st.plotly_chart(fig)

# Custom CSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
