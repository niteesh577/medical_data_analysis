import pandas as pd
from mrjob.job import MRJob
import os
import io
import streamlit as st

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Step 1: Convert .xlsx to .csv
def convert_xlsx_to_csv(xlsx_file, csv_file):
    # Check if the file exists and read the sheet names
    try:
        xlsx = pd.ExcelFile(xlsx_file)
        sheet_names = xlsx.sheet_names
        if 'medical_dataset_vitals' not in sheet_names:
            raise ValueError(f"Worksheet named 'medical_dataset_vitals' not found")
        
        df = pd.read_excel(xlsx_file, sheet_name='medical_dataset_vitals')
        df.to_csv(csv_file, index=False)
    except Exception as e:
        st.error(f"Error converting Excel to CSV: {e}")
        raise

# Step 2: Define MapReduce Job
class MRAverageByAge(MRJob):

    def mapper(self, _, line):
        if line.startswith('Patient_ID'):
            return
        fields = line.split(',')
        if len(fields) >= 14:
            age = fields[2]
            yield (age, 'body_temp'), float(fields[5])
            yield (age, 'pulse_rate'), float(fields[6])
            yield (age, 'respiration_rate'), float(fields[7])
            yield (age, 'blood_pressure'), float(fields[8])
            yield (age, 'blood_oxygen'), float(fields[9])
            yield (age, 'weight'), float(fields[10])
            yield (age, 'blood_glucose'), float(fields[11])

    def reducer(self, key, values):
        total = sum(values)
        count = len(values)
        average = total / count
        yield key, average

# Step 3: Run MapReduce Job and Save Output
def run_mapreduce(csv_file):
    # Ensure output directory exists
    output_dir = 'mapreduce_output'
    os.makedirs(output_dir, exist_ok=True)

    # Run MapReduce job
    mr_job = MRAverageByAge(args=[csv_file, '--output-dir', output_dir])
    with mr_job.make_runner() as runner:
        runner.run()

    # Read the output file
    output_file = os.path.join(output_dir, 'part-00000')
    try:
        return pd.read_csv(output_file, header=None, names=['Key', 'Average'])
    except FileNotFoundError:
        st.error("MapReduce output file not found.")
        raise

# Step 4: Streamlit App
def main():
    ##### DATA VISUALISTION ######## BACK UP PROJECT



    st.set_page_config(page_title="Realtime Medical Dashboard",
                    page_icon='app icon.png',
                    layout='wide')

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

    # Filter options
    cities = st.sidebar.multiselect(
        "Select the City:",
        options=df["City"].unique(),
        default=df["City"].unique()
    )

    genders = st.sidebar.multiselect(
        "Select the Gender:",
        options=df["Gender"].unique(),
        default=df["Gender"].unique()
    )

    diagnoses = st.sidebar.multiselect(
        "Select the Diagnosis:",
        options=df["Diagnosis"].unique(),
        default=df["Diagnosis"].unique()
    )

    # Selection Query
    df_selection = df.query(
        "City == @cities & Gender == @genders & Diagnosis == @diagnoses"
    )

    # Main Page
    st.title(":bar_chart: Realtime Medical Dashboard")

    # Top KPIs
    avg_temp = round(df_selection["Body_Temperature"].mean(), 1)
    avg_pulse = round(df_selection["Pulse_Rate"].mean(), 1)
    avg_respiration = round(df_selection["Respiration_Rate"].mean(), 1)
    avg_bp = round(df_selection["Blood_Pressure"].mean(), 1)
    avg_oxygen = round(df_selection["Blood_Oxygen"].mean(), 1)
    avg_weight = round(df_selection["Weight"].mean(), 1)
    avg_glucose = round(df_selection["Blood_Glucose_Level"].mean(), 1)

    # KPI Graphs
    def create_kpi(title, value, unit):
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=value,
            title={"text": title, "font": {"size": 16}},
            delta={'reference': value - 0.1 * value, 'relative': True, 'valueformat': ".1f"},
            number={'font': {'size': 24}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'visible': False}},
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=150,
            template="plotly_white",
            font=dict(size=18),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    left_col, mid_col1, mid_col2, mid_col3, right_col = st.columns(5)

    with left_col:
        st.subheader("Avg Body Temp:")
        st.plotly_chart(create_kpi("Body Temperature", avg_temp, "°C"), use_container_width=True)

    with mid_col1:
        st.subheader("Avg Pulse Rate:")
        st.plotly_chart(create_kpi("Pulse Rate", avg_pulse, "bpm"), use_container_width=True)

    with mid_col2:
        st.subheader("Avg Respiration Rate:")
        st.plotly_chart(create_kpi("Respiration Rate", avg_respiration, "bpm"), use_container_width=True)

    with mid_col3:
        st.subheader("Avg Blood Pressure:")
        st.plotly_chart(create_kpi("Blood Pressure", avg_bp, "mmHg"), use_container_width=True)

    with right_col:
        st.subheader("Avg Blood Oxygen:")
        st.plotly_chart(create_kpi("Blood Oxygen", avg_oxygen, "%"), use_container_width=True)

    st.markdown("---")

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Avg Weight:")
        st.plotly_chart(create_kpi("Weight", avg_weight, "kg"), use_container_width=True)

    with right_col:
        st.subheader("Avg Blood Glucose:")
        st.plotly_chart(create_kpi("Blood Glucose Level", avg_glucose, "mg/dL"), use_container_width=True)

    st.markdown("---")

    # Body Temperature by Age
    temp_by_age = df_selection.groupby(by=["Age"])[["Body_Temperature"]].mean()
    fig_temp_age = px.line(
        temp_by_age,
        x=temp_by_age.index,
        y="Body_Temperature",
        title="<b>Avg Body Temperature by Age</b>",
        template="plotly_white",
    )

    fig_temp_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Pulse Rate by Age
    pulse_by_age = df_selection.groupby(by=["Age"])[["Pulse_Rate"]].mean()
    fig_pulse_age = px.line(
        pulse_by_age,
        x=pulse_by_age.index,
        y="Pulse_Rate",
        title="<b>Avg Pulse Rate by Age</b>",
        template="plotly_white",
    )

    fig_pulse_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Respiration Rate by Age
    resp_by_age = df_selection.groupby(by=["Age"])[["Respiration_Rate"]].mean()
    fig_resp_age = px.line(
        resp_by_age,
        x=resp_by_age.index,
        y="Respiration_Rate",
        title="<b>Avg Respiration Rate by Age</b>",
        template="plotly_white",
    )

    fig_resp_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Blood Pressure by Age
    bp_by_age = df_selection.groupby(by=["Age"])[["Blood_Pressure"]].mean()
    fig_bp_age = px.line(
        bp_by_age,
        x=bp_by_age.index,
        y="Blood_Pressure",
        title="<b>Avg Blood Pressure by Age</b>",
        template="plotly_white",
    )

    fig_bp_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Blood Oxygen by Age
    oxygen_by_age = df_selection.groupby(by=["Age"])[["Blood_Oxygen"]].mean()
    fig_oxygen_age = px.line(
        oxygen_by_age,
        x=oxygen_by_age.index,
        y="Blood_Oxygen",
        title="<b>Avg Blood Oxygen by Age</b>",
        template="plotly_white",
    )

    fig_oxygen_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Weight by Age
    weight_by_age = df_selection.groupby(by=["Age"])[["Weight"]].mean()
    fig_weight_age = px.line(
        weight_by_age,
        x=weight_by_age.index,
        y="Weight",
        title="<b>Avg Weight by Age</b>",
        template="plotly_white",
    )

    fig_weight_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Blood Glucose Level by Age
    glucose_by_age = df_selection.groupby(by=["Age"])[["Blood_Glucose_Level"]].mean()
    fig_glucose_age = px.line(
        glucose_by_age,
        x=glucose_by_age.index,
        y="Blood_Glucose_Level",
        title="<b>Avg Blood Glucose Level by Age</b>",
        template="plotly_white",
    )

    fig_glucose_age.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
        title=dict(font=dict(size=16))
    )

    # Display the graphs
    st.plotly_chart(fig_temp_age, use_container_width=True)
    st.plotly_chart(fig_pulse_age, use_container_width=True)
    st.plotly_chart(fig_resp_age, use_container_width=True)
    st.plotly_chart(fig_bp_age, use_container_width=True)
    st.plotly_chart(fig_oxygen_age, use_container_width=True)
    st.plotly_chart(fig_weight_age, use_container_width=True)
    st.plotly_chart(fig_glucose_age, use_container_width=True)

if __name__ == '__main__':
    main()
