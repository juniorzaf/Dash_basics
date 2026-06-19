#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# 1. Chargement des données
data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv')

# 2. Initialisation de l'application Dash
app = dash.Dash(__name__)

# Options pour le menu déroulant des statistiques
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# Liste des années (de 1980 à 2023)
year_list = [i for i in range(1980, 2024, 1)]

# 3. Mise en page (Layout) de l'application
app.layout = html.Div([
    # Titre du Dashboard
    html.H1("Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),

    # Premier Dropdown : Choix du type de rapport
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Yearly Statistics',  # Valeur par défaut unique
            placeholder='Select a report type'
        )
    ]),

    # Deuxième Dropdown : Choix de l'année
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value=2020,  # Année par défaut pour éviter un affichage vide au départ
            disabled=False
        )
    ]),

    # Zone d'affichage des graphiques
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexDirection': 'column'}),
    ])
])


# 4. CALLBACKS (Logique interactive)

# Callback 1 : Activer ou désactiver le choix de l'année
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'))
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True


# Callback 2 : Génération et mise à jour des graphiques
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')])
def update_output_container(report_type, input_year):
    # CAS 1 : STATISTIQUES EN PÉRIODE DE RÉCESSION
    if report_type == 'Recession Period Statistics':
        # Filtrer pour garder uniquement les périodes de récession
        recession_data = data[data['Recession'] == 1]

        # Plot 1 : Évolution des ventes moyennes pendant les récessions
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec,
                           x='Year',
                           y='Automobile_Sales',
                           title="Average Automobile Sales Fluctuation over Recession Period"))

        # Plot 2 : Ventes moyennes par type de véhicule
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales',
                          title="Average Sales By Vehicle Type"))

        # Plot 3 : Part des dépenses publicitaires par type de véhicule (Pie chart)
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec,
                          values='Advertising_Expenditure',
                          names='Vehicle_Type',
                          title="Total Advertising Expenditure Share by Vehicle Type"
                          )
        )

        # Plot 4 : Effet du taux de chômage sur les ventes et types de véhicules
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])[
            'Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                          x='unemployment_rate',
                          y='Automobile_Sales',
                          color='Vehicle_Type',
                          labels={'unemployment_rate': 'Unemployment Rate',
                                  'Automobile_Sales': 'Average Automobile Sales'},
                          title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        # Organisation des graphiques en 2 lignes de 2 colonnes
        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[R_chart3, R_chart4], style={'display': 'flex'})
        ]

    # CAS 2 : STATISTIQUES ANNUELLES STANDARDS
    elif report_type == 'Yearly Statistics' and input_year:
        # Filtrer les données pour l'année spécifique sélectionnée
        yearly_data = data[data['Year'] == int(input_year)]

        # Plot 1 : Ventes annuelles globales de voitures (Tendance historique globale)
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile_Sales', title="Historical Yearly Automobile Sales"))

        # Plot 2 : Total des ventes mensuelles pour l'année choisie
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(mas,
                                            x='Month',
                                            y='Automobile_Sales',
                                            title='Total Monthly Automobile Sales in {}'.format(input_year)))

        # Plot 3 : Moyenne des véhicules vendus par type de véhicule pour l'année choisie
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                                           title='Average Vehicles Sold by Vehicle Type in the year {}'.format(
                                               input_year)))

        # Plot 4 : Dépenses publicitaires totales par type de véhicule pour l'année choisie
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                          values='Advertising_Expenditure',
                          names='Vehicle_Type',
                          title='Advertising Expenditure for each Vehicle Type in {}'.format(input_year)))

        # Organisation des graphiques en 2 lignes de 2 colonnes
        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4], style={'display': 'flex'})
        ]

    else:
        return None


# 5. Lancement de l'application (Syntaxe moderne adaptée à Python 3.13)
if __name__ == '__main__':
    app.run(debug=True, port=8050)