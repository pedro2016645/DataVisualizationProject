import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go

#Data Preprocessing

df_indexes = pd.read_excel('DataSet_Correto.xlsx')
df_indexes = df_indexes.sort_values(by=['country_name', 'year'])

df_indexes.rename(columns={"En_Superior": "Higher Education",
                   "En_Renovavel": "Renewable Energy",
                   "IeD": "R&D",
                   "Divida": "Debt",
                   "EMV": "Life Expectancy",
                   "PIBpc": "PIB per capita",
                   "Pobreza": "Poverty",
                   "Abandono_escolar": "Dropout",
                   "Desemprego": "Unemployment",
                   "Homicidio": "Homicides",
                   "Agressao": "Assaults",
                   "V_Sexual": "Sexual Violence",
                   "Roubo": "Thefts",
                   "Salarios": "Salary"}, inplace=True)

df_indexes = df_indexes.drop(['BandaLarga'], axis=1)
df_indexes = df_indexes.drop(['Medicos'], axis=1)
df_indexes = df_indexes.drop(['Gases_Pol'], axis=1)
df_indexes = df_indexes.drop(['Computador'], axis=1)
df_indexes = df_indexes.drop(['Internet'], axis=1)


social_indexes = ["Higher Education", "Life Expectancy", 'PIB per capita', "Salary", "Dropout"]

economic_indexes = ["Renewable Energy", "R&D", "Debt", "Poverty", "Unemployment", 'Homicides',
                    "Assaults", "Sexual Violence", "Thefts"]

#

country_options = [dict(label=country, value=country) for country in df_indexes['country_name'].unique()]

social_options = [dict(label=social, value=social) for social in social_indexes]

economic_options = [dict(label=economic, value=economic) for economic in economic_indexes]

#APP

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.H1('Country Indicators')
    ], className='Title'),

    html.Div([

        html.Div([
            html.Label('Country Choice'),
            dcc.Dropdown(
                id='country_drop',
                options=country_options,
                value=['Portugal'],
                multi=True
            ),

            html.Br(),

            html.Label('Social Index Choice'),
            dcc.Dropdown(
                id='social_drop',
                options=social_options,
                value='Higher Education',
            ),

            html.Br(),

            html.Label('Economic Index Choice'),
            dcc.Dropdown(
                id='economic_drop',
                options=economic_options,
                value=['Debt'],
                multi=True
            ),

            html.Br(),

            html.Label('Year Slider'),
            dcc.Slider(
                id='year_slider',
                min=df_indexes['year'].min(),
                max=df_indexes['year'].max(),
                marks={str(i): '{}'.format(str(i)) for i in [2005, 2010, 2015]},
                value=df_indexes['year'].min(),
                step=None
            ),

            html.Br(),

            html.Label('Linear Log'),
            dcc.RadioItems(
                id='lin_log',
                options=[dict(label='Linear', value=0), dict(label='log', value=1)],
                value=0
            ),

            html.Br(),

            html.Label('Projection'),
            dcc.RadioItems(
                id='projection',
                options=[dict(label='Equirectangular', value=0), dict(label='Orthographic', value=1)],
                value=0
            )
        ], className='column1 pretty'),

        html.Div([

            html.Div([

                html.Div([html.Label(id='social_1')], className='mini pretty'),
                html.Div([html.Label(id='social_2')], className='mini pretty'),
                html.Div([html.Label(id='social_3')], className='mini pretty'),
                html.Div([html.Label(id='social_4')], className='mini pretty'),
                html.Div([html.Label(id='social_5')], className='mini pretty')
            ], className='social boxes row'),

            html.Div([dcc.Graph(id='first_graph')], className='bar_plot pretty')

        ], className='column2')

    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='second_graph')], className='column3 pretty'),

        html.Div([dcc.Graph(id='third_graph')], className='column3 pretty')

    ], className='row')

])

#Callbacks

@app.callback(
    [
        Output("first_graph", "figure"),
        Output("second_graph", "figure"),
        Output("third_graph", "figure"),
    ],
    [
        Input("year_slider", "value"),
        Input("country_drop", "value"),
        Input("social_drop", "value"),
        Input("lin_log", "value"),
        Input("projection", "value"),
        Input("economic_drop", "value")
    ]
)
def plots(year, countries, social, scale, projection, economic):


#Bar Plot
    data_barchart = []
    for country in countries:
        df_barchart = df_indexes.loc[(df_indexes['country_name'] == country)]

        x_bar = ['2005', '2010', '2015']
        y_bar = df_barchart[social]
        data_barchart.append(dict(type='bar', x=x_bar, y=y_bar, name=country))

    layout_barchart = dict(title=dict(text=str(social) + ' Comparison between 2005, 2010 and 2015'),
                  yaxis=dict(title=str(social), type=['linear', 'log'][scale]),
                  paper_bgcolor='#f9f9f9'
                  )


#Choropleth

    df_2 = df_indexes.loc[df_indexes['year'] == year]

    z = np.log(df_2[social])

    data_choropleth = dict(type='choropleth',
                           locations=df_2['country_name'],
                           locationmode='country names',
                           z=z,
                           text=df_2['country_name'],
                           colorscale='inferno',
                           colorbar=dict(title=str(social) + ' (log scaled)'),

                           hovertemplate='Country: %{text} <br>' + str(social) + ': %{z}',
                           name=''
                           )

    layout_choropleth = dict(geo=dict(scope='europe',
                                      projection=dict(type=['equirectangular', 'orthographic'][projection]
                                                      ),
                                      landcolor='black',
                                      lakecolor='white',
                                      showocean=True,
                                      oceancolor='azure',
                                      bgcolor='#f9f9f9'
                                      ),

                             title=dict(text='European ' + str(social) + ' Choropleth Map on the year ' + str(year),
                                        x=.5
                                        ),
                             paper_bgcolor='#f9f9f9'
                             )


#Scatter Plot

    df_3 = df_indexes.loc[df_indexes['country_name'].isin(countries)].groupby('year').sum().reset_index()

    data_scatter= []

    for economic in economic:
        data_scatter.append(dict(type='scatter',
                         x=df_3['year'].unique(),
                         y=df_3[economic],
                         name=economic,
                         mode='lines+markers',
                         marker=dict(size=15, color='rgb(0,0,0)',
                                         line=dict(color='rgb(0,0,0)', width=5)
                         )
                    ))

    layout_scatter = dict(title=dict(text=str(economic) + " Evolution"),
                     yaxis=dict(title=[str(economic), 'Economic (log scaled)'][scale],
                                type=['linear', 'log'][scale]),
                     xaxis=dict(title='Year'),
                     paper_bgcolor='#f9f9f9'
                     )

    return go.Figure(data=data_barchart, layout=layout_barchart), \
           go.Figure(data=data_choropleth, layout=layout_choropleth),\
           go.Figure(data=data_scatter, layout=layout_scatter)


@app.callback(
    [
        Output("social_1", "children"),
        Output("social_2", "children"),
        Output("social_3", "children"),
        Output("social_4", "children"),
        Output("social_5", "children"),

    ],
    [
        Input("country_drop", "value"),
        Input("year_slider", "value"),
    ]
)
def indicator(countries, year):
    df_3 = df_indexes.loc[df_indexes['country_name'].isin(countries)].groupby('year').sum().reset_index()

    value_1 = round(df_3.loc[df_3['year'] == year][social_indexes[0]].values[0], 2)
    value_2 = round(df_3.loc[df_3['year'] == year][social_indexes[1]].values[0], 2)
    value_3 = round(df_3.loc[df_3['year'] == year][social_indexes[2]].values[0], 2)
    value_4 = round(df_3.loc[df_3['year'] == year][social_indexes[3]].values[0], 2)
    value_5 = round(df_3.loc[df_3['year'] == year][social_indexes[4]].values[0], 2)



    return str(social_indexes[0]) + ': ' + str(value_1),\
           str(social_indexes[1]) + ': ' + str(value_2), \
           str(social_indexes[2]) + ': ' + str(value_3), \
           str(social_indexes[3]) + ': ' + str(value_4), \
           str(social_indexes[4]) + ': ' + str(value_5), \



if __name__ == '__main__':
    app.run_server(debug=True)