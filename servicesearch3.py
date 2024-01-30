import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import mysql.connector
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the app layout with additional filter components
app.layout = dbc.Container([
   dbc.Row(dbc.Col(html.H1("Service Reports Parts Search", className="text-center text-primary, mb-4", style={'font-weight': 'bold', 'font-family': 'Helvetica'}), width=12, style={'': '2%'})),
   
   dbc.Row([
      dbc.Col(dcc.DatePickerRange(
         id='date-range',
         start_date=datetime(1995, 8, 25),
         end_date=datetime.today(),
         display_format='MMM Do, YY'
      ), width=3),
      
      dbc.Col(dcc.Input(
         id='customer-search', 
         type='text', 
         placeholder='Customer'
      ), width=3),
      dbc.Col(dcc.Input(
         id='service-report-search', 
         type='text', 
         placeholder='SrvRpt No.'
      ), width=3),
      dbc.Col(dcc.Input(
         id='model-search', 
         type='text', 
         placeholder='Model'
      ), width=3),
   ], className="mb-2", style={'text-align': 'center'}),
   
   dbc.Row([
      dbc.Col(html.Button('Search', id='search-button', n_clicks=0, className='btn-md', style={'margin-left': '0%', 'width': '25%', 'justify':'left'}), width=3),
      dbc.Col(dcc.Input(
         id='serial-search', 
         type='text', 
         placeholder='Serial No.'
      ), width=3),
      dbc.Col(dcc.Input(
         id='part-number-search', 
         type='text', 
         placeholder='Part Number'
      ), width=3),
      dbc.Col(dcc.Input(
         id='description-search', 
         type='text', 
         placeholder='Description',
      ), width=3),
   ], className="mb-2", style={'text-align': 'center'}),  # Close the square bracket for dbc.Row

   
   dbc.Row(dbc.Col(dash_table.DataTable(id='table', style_table={'overflowX': 'scroll'}, style_header={
      'fontWeight': 'bold',
      'backgroundColor': 'white',
      'color': 'black',
      'textAlign': 'center'
   }), width=12)),
   
   dbc.Row([
      dbc.Col(dcc.Download(id="download-dataframe-csv"), width=12)
   ]),
], fluid=True)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='properup.com',
        user='properup_masterData_admin',
        passwd='Chippy_3445',
        database='properup_final_masterData'
    )

# Callback for the search button and filters
@app.callback(
    [Output('table', 'data'), Output('table', 'columns')],
    [Input('search-button', 'n_clicks')],
    [State('date-range', 'start_date'),
     State('date-range', 'end_date'),
     State('customer-search', 'value'),
     State('service-report-search', 'value'),
     State('model-search', 'value'),
     State('serial-search', 'value'),
     State('part-number-search', 'value'),
     State('description-search', 'value')]
)
def update_table(n_clicks, start_date, end_date, cust_name, service_report, model, serial_no, part_number, description):
    if n_clicks is None or n_clicks < 1:
        raise dash.exceptions.PreventUpdate
    
    # Create the query based on the filters
    query = "SELECT * FROM final_masterdata WHERE SrvDate BETWEEN %s AND %s"
    params = [start_date, end_date]
    
    
    if cust_name:
        query += " AND Cust_name LIKE %s"
        params.append("%" + cust_name + "%")
    if service_report:
        query += " AND SrvRptNo LIKE %s"
        params.append("%" + service_report + "%")
    if model:
        query += " AND Model LIKE %s"
        params.append("%" + model + "%")
    if serial_no:
        query += " AND SerNo LIKE %s"
        params.append("%" + serial_no + "%")
    if part_number:
        query += " AND PartNo LIKE %s"
        params.append("%" + part_number + "%")
    if description:
        query += " AND Description LIKE %s"
        params.append("%" + description + "%")
        
    # Execute the query
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Convert the results to a DataFrame
    df = pd.DataFrame(rows)
    df = df[[col for col in df.columns if col != 'Cust_id']]
    # Convert DataFrame to the table data and columns format
    data = df.to_dict('records')
    columns = [{"name": col, "id": col} for col in df.columns]
    
    return data, columns

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
