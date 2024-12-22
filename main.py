from db import DatabaseHandler
from index import Index
import dash
import pandas as pd
from datetime import datetime
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_table

if __name__ == '__main__':
    db = DatabaseHandler('./data/INDEX.db')
    index = Index(db)
    data = index.createIndex()
    marketCapData = data['marketCapData']
    marketCapData['date'] = pd.to_datetime(marketCapData['date'], format='%Y-%m-%d')
    indexPerformance = data['indexPerformance']
    db.databaseConnection.close()
    
    app = dash.Dash(__name__)

    # Create initial figures for stock market capitalization
    stock_fig = px.line(marketCapData, x='date', y='marketCap', color='ticker', title='Stock Market Capitalization Over Time')
    
    # Calculate the average cumulative return
    average_return = indexPerformance['cumulative_index_return'].mean()

    # Add a line to the index performance graph for average returns
    indexPerformance['average_return'] = average_return  # Adding a new column for the average return line

    # Create the initial figure for index performance with the average return line
    index_fig = px.line(indexPerformance, x='date', y='cumulative_index_return', title='Index Performance Over the Past Month')
    index_fig.add_scatter(x=indexPerformance['date'], y=indexPerformance['average_return'], mode='lines', name='Average Return', line=dict(dash='dash', color='red'))

    app.layout = html.Div(children=[
        html.H1(children='Market Dashboard'),
        
        # Date Picker for range
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=marketCapData['date'].min().date(),
            end_date=marketCapData['date'].max().date(),
            display_format='YYYY-MM-DD'
        ),
        html.Div([
            html.Button('Show Last 30 Days', id='show-30-days', n_clicks=0),
            html.Button('Reset Date Range', id='reset-range', n_clicks=0),
            html.Button('Update Graphs', id='update-graphs', n_clicks=0),
            html.Button('Export CSV', id='export_csv', n_clicks=0)
        ]),
        # Graph for stock market capitalization
        dcc.Graph(
            id='stock-market-cap',
            figure=stock_fig
        ),
        
        # Graph for index performance
        dcc.Graph(
            id='index-performance',
            figure=index_fig
        ),
        
        # Single Date Picker for selecting a date to filter stocks
        dcc.DatePickerSingle(
            id='date-picker-single',
            date=marketCapData['date'].max().date(),  # Default to latest date
            display_format='YYYY-MM-DD'
        ),
        
        # Table to show stocks for the selected date
        dash_table.DataTable(
            id='stocks-table',
            columns=[
                {'name': 'Ticker', 'id': 'ticker'},
                {'name': 'Market Cap', 'id': 'marketCap'},
                {'name': 'Date', 'id': 'date'}
            ],
            style_table={'height': '400px', 'overflowY': 'auto'},  # Make the table scrollable
        ),
        
    ])

    @app.callback(
        Input('export_csv', 'n_clicks')
    )
    def export_csv(export_csv):
        if export_csv > 0:
            marketCapData.to_csv('./data/marketCap.csv')
            indexPerformance.to_csv('./data/indexPerformance.csv')

    @app.callback(
        Output('stock-market-cap', 'figure'),
        Output('index-performance', 'figure'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('show-30-days', 'n_clicks'),
        Input('reset-range', 'n_clicks'),
        Input('update-graphs', 'n_clicks')
    )
    def update_graph(start_date, end_date, show_30_days, reset_range, update_graphs):
        # Handle "Show Last 30 Days" button click
        if show_30_days > 0:
            end_date = pd.to_datetime(marketCapData['date'].max()).date()
            start_date = end_date - pd.Timedelta(days=30)
        
        # Handle "Reset Date Range" button click
        if reset_range > 0:
            start_date = marketCapData['date'].min().date()
            end_date = marketCapData['date'].max().date()
        
        # Convert to datetime if needed
        start_date = pd.to_datetime(start_date).date() if start_date else marketCapData['date'].min().date()
        end_date = pd.to_datetime(end_date).date() if end_date else marketCapData['date'].max().date()
        
        # Filter the data based on the selected date range
        filtered_data = marketCapData[
            (marketCapData['date'].dt.date >= start_date) &
            (marketCapData['date'].dt.date <= end_date)
        ]
        
        # Create updated figures based on the date range
        stock_fig = px.line(filtered_data, x='date', y='marketCap', color='ticker',
                            title=f'Stock Market Capitalization from {start_date} to {end_date}')
        
        # Add average return line to index performance graph
        indexPerformance['average_return'] = average_return
        index_fig = px.line(indexPerformance, x='date', y='cumulative_index_return', title='Index Performance Over the Past Month')
        index_fig.add_scatter(x=indexPerformance['date'], y=indexPerformance['avg_change'], mode='lines', name='Average Return', line=dict(dash='dash', color='red'))
        
        return stock_fig, index_fig

    @app.callback(
        Output('stocks-table', 'data'),
        Input('date-picker-single', 'date')
    )
    def update_table(selected_date):
        # Convert the selected date to a datetime object
        selected_date = pd.to_datetime(selected_date).date() if selected_date else marketCapData['date'].max().date()
        
        # Filter the data based on the selected date
        filtered_data = marketCapData[marketCapData['date'].dt.date == selected_date]
        
        # Return filtered data as the table data
        table_data = filtered_data[['ticker', 'marketCap', 'date']].to_dict('records')
        
        return table_data

    app.run_server(debug=True)
