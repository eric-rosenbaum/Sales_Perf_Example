# Install necessary packages if you haven't already
# pip install dash plotly pandas

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the fake sales data
df = pd.read_csv('fake_sales_data.csv')

# Data preparation
df['Date'] = pd.to_datetime(df['Date'])

# Get unique months for dropdown
df['Month'] = df['Date'].dt.to_period('M')
available_months = df['Month'].drop_duplicates().astype(str).tolist()

# Initialize the app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Sales Performance Dashboard", style={'textAlign': 'center'}),

    # Dropdown for selecting the date range (month)
    html.Label("Select Date Range"),
    dcc.Dropdown(
        id='date-range',
        options=[{'label': month, 'value': month} for month in available_months],
        value=available_months,  # Select all months by default
        multi=True
    ),
    
    # Div for 4 visualizations (2x2 grid)
    html.Div([
        html.Div([dcc.Graph(id='total-sales')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='profit-margin')], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    
    html.Div([
        html.Div([dcc.Graph(id='top-products')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='sales-region')], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
])

# Callback to update the graphs based on selected date range
@app.callback(
    [Output('total-sales', 'figure'),
     Output('profit-margin', 'figure'),
     Output('top-products', 'figure'),
     Output('sales-region', 'figure')],
    [Input('date-range', 'value')]
)
def update_dashboard(selected_months):
    # Filter data by selected date range
    filtered_df = df[df['Month'].astype(str).isin(selected_months)]

    # KPI 1: Total Sales Over Time
    monthly_sales = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].dt.to_timestamp()
    total_sales_fig = px.line(monthly_sales, x='Date', y='Sales', title='Total Sales Over Time')

    # KPI 2: Profit Margin by Region
    filtered_df['Profit Margin'] = (filtered_df['Profit'] / filtered_df['Sales']) * 100
    profit_margin_by_region = filtered_df.groupby('Region')['Profit Margin'].mean().reset_index()
    profit_margin_fig = px.bar(profit_margin_by_region, x='Region', y='Profit Margin', title='Profit Margin by Region')

    # KPI 3: Top 5 Best-Selling Products
    top_products = filtered_df.groupby('Product')['Sales'].sum().nlargest(5).reset_index()
    top_products_fig = px.bar(top_products, x='Product', y='Sales', title='Top 5 Best-Selling Products')

    # KPI 4: Sales Distribution by Region
    sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    sales_region_fig = px.pie(sales_by_region, names='Region', values='Sales', title='Sales Distribution by Region', hole=.3)

    return total_sales_fig, profit_margin_fig, top_products_fig, sales_region_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
