import sys,os
current_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(current_dir)
from dash import Dash, html, dcc, callback, Output,Input
import plotly.express as px
import plotly.io as pio
pio.templates
import pandas as pd
from Controllers.sqliteController import SQLiteModel
import datetime
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
load_figure_template("darkly")

ob = SQLiteModel("DataBase/LocalData.db")
ob.connect()
today = datetime.datetime.now()-datetime.timedelta(minutes=60)
query = f"SELECT MACHINE_NAME as Machine, A as mA, V, TEMPERATURE as Celsius, DATE \
    FROM DataSensors WHERE DATE>='{today}' \
    ORDER BY DATE DESC\
    LIMIT 60;"
    
df_sqlite = pd.read_sql_query(query,con=ob.connection)
df_sqlite['Hour'] = pd.to_datetime(df_sqlite['DATE']).dt.strftime("%H:%M:%S")
df_sqlite['DATE'] = pd.to_datetime(df_sqlite['DATE'])
df_sqlite["Machine"].dropna(inplace=True)
ob.disconnect()

def update_dropdown_options():
    new_options = [{'label': machine, 'value': machine} for machine in df_sqlite.Machine.unique()]
    return new_options


app = Dash(__name__,external_stylesheets=[dbc.themes.SUPERHERO])

app.layout = html.Div(
    children=[
    html.H1(children='DataSensors Devices', style={"textAlign": "center","fontSize": "36px", "fontWeight": "bold"},),
    dcc.Dropdown(options=update_dropdown_options(),
        value=df_sqlite.Machine.unique()[0],
        id='dropdown-selection',
        style={"color": "black"}),
    dcc.Graph(id='graph-current'),
    dcc.Graph(id='graph-voltage'),
    dcc.Graph(id='graph-temperature'),
    dcc.Interval(id='interval-component', interval=6000, n_intervals=0) 
])

@callback(
    [Output('dropdown-selection', 'options'),Output('graph-current', 'figure'), Output('graph-voltage', 'figure'), Output('graph-temperature', 'figure')],
    [Input('dropdown-selection', 'value'),Input('interval-component', 'n_intervals')]
)

        
def update_graph(value,n):
    #some default configs to graphics
    def configure_graph(fig):
        fig.update_layout(
            # template="seaborn",
            xaxis_tickangle=-45
        )     
        fig.update_layout(title_font={'size': 26,'family': 'Helvetica, bold'})      
        return fig

    def update_data_frame():
        ob = SQLiteModel("DataBase/LocalData.db")
        ob.connect()
        today = datetime.datetime.now()-datetime.timedelta(minutes=60)
        query = f"SELECT MACHINE_NAME as Machine, A as mA, V, TEMPERATURE as Celsius, DATE FROM DataSensors WHERE DATE>='{today}'"
        df_sqlite = pd.read_sql_query(query,con=ob.connection)
        df_sqlite['Hour'] = pd.to_datetime(df_sqlite['DATE']).dt.strftime("%H:%M:%S")
        df_sqlite['DATE'] = pd.to_datetime(df_sqlite['DATE'])
        ob.disconnect()
        return df_sqlite

        
    df_sqlite = update_data_frame()
    
    dropdown_options = [{'label': Machine, 'value': Machine} for Machine in df_sqlite.Machine.unique()]
    print(dropdown_options)
    dff = df_sqlite[df_sqlite.Machine == value].tail(20)
    # Gráfico de Corrente
    fig_current = px.line(dff, x='Hour', y='mA', title='Current')
    fig_current = configure_graph(fig_current)

    # Gráfico de Tensão
    fig_voltage = px.line(dff, x='Hour', y='V', title='Voltage')
    fig_voltage = configure_graph(fig_voltage)

    # Gráfico de Temperatura
    fig_temperature = px.line(dff, x='Hour', y='Celsius', title='Temperature')
    fig_temperature = configure_graph(fig_temperature)
    print("callback")
    return dropdown_options, fig_current, fig_voltage, fig_temperature


if __name__ == '__main__':
    app.run(debug=True)
