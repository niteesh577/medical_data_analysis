import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Realtime Sales Dashboard", page_icon='📈', layout='wide')

@st.cache_data
def load_data():
    try:
        # Load the entire sheet to inspect its content
        df = pd.read_excel(
            io='sales_data.xlsx',
            engine='openpyxl',
            sheet_name='Sales',  # Ensure this is the correct sheet name
            skiprows=0,  # Adjust if necessary
            nrows=1000
        )
        # Print column names to debug
        # st.write("Columns in Excel file:", df.columns)
        
        # Ensure these columns exist in the DataFrame
        required_columns = [
            'Invoice ID', 'Branch', 'City', 'Customer_type', 'Gender', 'Product line',
            'Unit price', 'Quantity', 'Tax 5%', 'Total', 'Date', 'Time', 'Payment',
            'cogs', 'gross margin percentage', 'gross income', 'Rating'
        ]
        
        # Check if all required columns are present
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Column '{col}' not found in the Excel file.")
                return pd.DataFrame()  # Return empty DataFrame if any column is missing
        
        # Filter out the necessary columns
        df = df[required_columns]
        df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
        
        return df
    except ValueError as e:
        st.error(f"Error reading the Excel file: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs
    except FileNotFoundError:
        st.error("Sales data file not found.")
        return pd.DataFrame()  # Return empty DataFrame if file is not found
    except KeyError as e:
        st.error(f"Column or sheet not found: {e}")
        return pd.DataFrame()  # Return empty DataFrame if column or sheet is missing
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return empty DataFrame for unexpected errors

# Load KPI data from product_sales.txt
@st.cache_data
def load_kpi_data():
    product_sales = {}
    hour_sales = {}

    try:
        # Read product sales data
        with open("product_sales.txt", "r") as file:
            for line in file:
                product_line, sales = line.strip().split(": ")
                product_sales[product_line] = float(sales)
    except FileNotFoundError:
        st.error("Product sales data file not found.")
    
    return {
        "product_sales": product_sales,
        "hour_sales": hour_sales
    }

# Load KPI data
kpi_data = load_kpi_data()

# Read the dataset for filtering
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
city_filter = st.sidebar.multiselect(
    "Select City:",
    options=df["City"].unique(),
    default=df["City"].unique() if not df.empty else []
)
customer_type_filter = st.sidebar.multiselect(
    "Select Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique() if not df.empty else []
)
gender_filter = st.sidebar.multiselect(
    "Select Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique() if not df.empty else []
)

# Filter data based on user input
filtered_df = df[
    (df["City"].isin(city_filter)) &
    (df["Customer_type"].isin(customer_type_filter)) &
    (df["Gender"].isin(gender_filter))
]

# Recalculate KPIs for filtered data
def calculate_kpis(df):
    total_sales = round(df["Total"].sum(), 2)
    total_transactions = len(df)
    avg_sale_per_transaction = round(total_sales / total_transactions, 2) if total_transactions > 0 else 0
    avg_rating = round(df["Rating"].mean(), 1)
    total_customers = len(df["Invoice ID"].unique())

    product_sales = df.groupby("Product line")["Total"].sum().round(2).to_dict()
    hour_sales = df.groupby("hour")["Total"].sum().round(2).to_dict()

    return {
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "avg_sale_per_transaction": avg_sale_per_transaction,
        "avg_rating": avg_rating,
        "total_customers": total_customers,
        "product_sales": product_sales,
        "hour_sales": hour_sales
    }

filtered_kpi_data = calculate_kpis(filtered_df)

# Streamlit Dashboard
st.title("📊 Realtime Sales Dashboard")

# Display KPIs
st.markdown("## Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Sales", f"$ {filtered_kpi_data['total_sales']:,}")
col2.metric("Total Transactions", filtered_kpi_data['total_transactions'])
col3.metric("Avg Sale/Transaction", f"$ {filtered_kpi_data['avg_sale_per_transaction']}")
col4.metric("Avg Rating", filtered_kpi_data['avg_rating'])
col5.metric("Total Customers", filtered_kpi_data['total_customers'])

st.markdown("---")

# Sales by Product Line
st.markdown("## Sales by Product Line")
fig, ax = plt.subplots()
product_lines = list(filtered_kpi_data["product_sales"].keys())
sales = list(filtered_kpi_data["product_sales"].values())
ax.pie(sales, labels=product_lines, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
ax.axis('equal')
st.pyplot(fig)

# Sales by Hour
st.markdown("## Sales by Hour")
fig, ax = plt.subplots()
hours = list(filtered_kpi_data["hour_sales"].keys())
sales_by_hour = list(filtered_kpi_data["hour_sales"].values())
ax.plot(hours, sales_by_hour, marker='o', linestyle='-', color='b')
ax.set_xticks(hours)
ax.set_xlabel("Hour of the Day")
ax.set_ylabel("Sales")
ax.set_title("Sales by Hour")
st.pyplot(fig)

# Custom CSS for hiding Streamlit elements
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
