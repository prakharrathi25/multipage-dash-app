# Import necessary libraries 
import dash
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
from app import app
from urllib.request import urlopen
import json
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
from geopy.geocoders import Nominatim

# define a function to create buffer around a point
proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
def geodesic_point_buffer(lat, lon, miles):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)), 
        proj_wgs84)
    buf = Point(0, 0).buffer(miles * 1000/0.621371)  # distance in miles
    return transform(project, buf).exterior.coords[:]
# import plotly.graph_objects as go



## reading the dataset
pd_2 = pd.read_csv('https://raw.githubusercontent.com/Anmol3015/Plotly_Dash_examples/main/retail_sales.csv', sep=',')
pd_2['Date'] = pd.to_datetime(pd_2['Date'], format='%Y-%m-%d')


################################ total sales Month level  ###################################
monthly_sales_df = pd_2.groupby(['month','Month']).agg({'Weekly_Sales':'sum'}).reset_index()


################################ holiday sales month lvl #####################################
holiday_sales = pd_2[pd_2['IsHoliday'] == 1].groupby(['month'])['Weekly_Sales'].sum().reset_index().rename(columns={'Weekly_Sales':'Holiday_Sales'})

############################# combined #########################
monthly_sales_df  = pd.merge(holiday_sales,monthly_sales_df,on = 'month', how = 'right').fillna(0)

############################## rounding sales to 1 decimal #############################
monthly_sales_df['Weekly_Sales'] = monthly_sales_df['Weekly_Sales'].round(1)
monthly_sales_df['Holiday_Sales'] = monthly_sales_df['Holiday_Sales'].round(1)


###################### weekly sales #########################
weekly_sale = pd_2.groupby(['month','Month','Date']).agg({'Weekly_Sales':'sum'}).reset_index()
weekly_sale['week_no'] = weekly_sale.groupby(['Month'])['Date'].rank(method='min')


########################### store level sales #######################
store_df=pd_2.groupby(['month','Month','Store']).agg({'Weekly_Sales':'sum'}).reset_index()
store_df['Store'] = store_df['Store'].apply(lambda x: 'Store'+" "+str(x))
store_df['Weekly_Sales'] = store_df['Weekly_Sales'].round(1)


######################## dept level sales #########################
dept_df=pd_2.groupby(['month','Month','Dept']).agg({'Weekly_Sales':'sum'}).reset_index()
dept_df['Dept'] = dept_df['Dept'].apply(lambda x: 'Dept'+" "+str(x))
dept_df['Weekly_Sales'] = dept_df['Weekly_Sales'].round(1)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
# Define the page layout

# navbar = dbc.Navbar( id = 'navbar', children = [
#     dbc.Row([
#         dbc.Col(html.Img(src = PLOTLY_LOGO, height = "70px")),
#         dbc.Col(
#             dbc.NavbarBrand("Import Analytics Dashboard", 
#                             style = {'color':'white', 'fontSize':'25px','fontFamily':'Times New Roman'}
#                             )
#             )
#         ],align = "center",
#         # no_gutters = True
#         ),
#     ], color = '#090059')


card_content_dropdwn = [
    dbc.CardBody(
        [
            html.H6('Select Months', style = {'textAlign':'center'}),
            dbc.Row([
                dbc.Col([
                    html.H6('NAICS Industry Description Level 2'),
                    dcc.Dropdown( id = 'dropdown_base',
        options = [
            {'label':i, 'value':i } for i in monthly_sales_df.sort_values('month')['Month']
            ],
        value = 'Feb',
        )
                    ]),
                dbc.Col([
                    html.H6('NAICS Industry Description Level 6'),

                    dcc.Dropdown( id = 'dropdown_comp',
        options = [
            {'label':i, 'value':i } for i in monthly_sales_df.sort_values('month')['Month']

            ],
        value = 'Jan',

        )
                    ]),
                ])
            ]
        )

    ]


body_app = dbc.Container([
   
    html.Br(),
    html.Br(),

    dbc.Row([
        dbc.Col([dbc.Card(card_content_dropdwn,style={'height':'150px'})],width = 4),
        dbc.Col([dbc.Card(id = 'card_num1',style={'height':'150px'})]),
        dbc.Col([dbc.Card(id = 'card_num2',style={'height':'150px'})]),
        dbc.Col([dbc.Card(id = 'card_num3',style={'height':'150px'})]),

        ]),
    html.Br(),
    html.Br(),
        
    dbc.Row([
        dbc.Col([dbc.Card(id = 'card_num7',style={'height':'700px'})]),
        # dbc.Col([dbc.Card(id = 'card_num8',style={'height':'350px'})]),
        # dbc.Col([dbc.Card(id = 'card_num9',style={'height':'350px'})]),

        ]), 
    html.Br(),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([dbc.Card(id = 'card_num4',style={'height':'350px'})]),
        dbc.Col([dbc.Card(id = 'card_num5',style={'height':'350px'})]),
        dbc.Col([dbc.Card(id = 'card_num6',style={'height':'350px'})]),

        ]),

    html.Br(),
    html.Br(),


    ],
    style = {'backgroundColor':'#f7f7f7'},
    fluid = True)


layout = html.Div(id = 'parent', children = [body_app])


@app.callback([Output('card_num1', 'children'),

               Output('card_num2', 'children'),
               Output('card_num3', 'children'),
               Output('card_num4', 'children'),
               Output('card_num7', 'children'),
               Output('card_num5', 'children'),
               Output('card_num6', 'children'),
               ],
              [Input('dropdown_base','value'),
                Input('dropdown_comp','value')])

def update_cards(base, comparison):

    sales_base = monthly_sales_df.loc[monthly_sales_df['Month']==base].reset_index()['Weekly_Sales'][0]
    sales_comp = monthly_sales_df.loc[monthly_sales_df['Month']==comparison].reset_index()['Weekly_Sales'][0]

    diff_1 = np.round(sales_base -sales_comp,1)

    holi_base = monthly_sales_df.loc[monthly_sales_df['Month']==base].reset_index()['Holiday_Sales'][0]
    holi_comp = monthly_sales_df.loc[monthly_sales_df['Month']==comparison].reset_index()['Holiday_Sales'][0]

    diff_holi = np.round(holi_base -holi_comp,1)


    base_st_ct = pd_2.loc[pd_2['Month']==base,'Store'].drop_duplicates().count()
    comp_st_ct = pd_2.loc[pd_2['Month']==comparison,'Store'].drop_duplicates().count()

    diff_store = np.round(base_st_ct-comp_st_ct,1)


    weekly_base = weekly_sale.loc[weekly_sale['Month']==base].reset_index()
    weekly_comp = weekly_sale.loc[weekly_sale['Month']==comparison].reset_index()



    store_base = store_df.loc[store_df['Month']==base].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]
    store_comp = store_df.loc[store_df['Month']==comparison].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]

    dept_base = dept_df.loc[dept_df['Month']==base].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]
    dept_base=dept_base.rename(columns = {'Weekly_Sales':'Weekly_Sales_base'})
    dept_comp = dept_df.loc[dept_df['Month']==comparison].sort_values('Weekly_Sales',ascending = False).reset_index()
    dept_comp=dept_comp.rename(columns = {'Weekly_Sales':'Weekly_Sales_comp'})

    merged_df=pd.merge(dept_base, dept_comp, on = 'Dept', how = 'left')
    merged_df['diff'] = merged_df['Weekly_Sales_base']-merged_df['Weekly_Sales_comp']
    
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})



    fig = go.Figure(data = [go.Scatter(x = weekly_base['week_no'], y = weekly_base['Weekly_Sales'],\
                                   line = dict(color = 'firebrick', width = 4),name = '{}'.format(base)),
                        go.Scatter(x = weekly_comp['week_no'], y = weekly_comp['Weekly_Sales'],\
                                   line = dict(color = '#090059', width = 4),name = '{}'.format(comparison))])


    fig.update_layout(plot_bgcolor = 'white',
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      yaxis_tickprefix = '$',
                      yaxis_ticksuffix = 'M')


    fig2 = go.Figure([go.Bar(x = store_base['Weekly_Sales'], y = store_base['Store'], marker_color = 'indianred',name = '{}'.format(base),\
                             text = store_base['Weekly_Sales'], orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])


    fig3 = go.Figure([go.Bar(x = store_comp['Weekly_Sales'], y = store_comp['Store'], marker_color = '#4863A0',name = '{}'.format(comparison),\
                             text = store_comp['Weekly_Sales'], orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])

    fig2.update_layout(plot_bgcolor = 'white',
                       xaxis = dict(range = [0,'{}'.format(store_base['Weekly_Sales'].max()+3)]),
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M',
                      title = '{}'.format(base),
                      title_x = 0.5)

    fig3.update_layout(plot_bgcolor = 'white',
                       xaxis = dict(range = [0,'{}'.format(store_comp['Weekly_Sales'].max()+3)]),
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M',
                      title = '{}'.format(comparison),
                      title_x = 0.5)

    fig4 = go.Figure([go.Bar(x = merged_df['diff'], y = merged_df['Dept'], marker_color = '#4863A0',\
                              orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])

    fig4.update_layout(plot_bgcolor = 'white',
                       margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M'
                     )
    geolocator = Nominatim(user_agent="bojrick@gmail.com")
    # target = geolocator.geocode('University of California, Los Angeles')
    targetLocs = ['University of Illinois at Chicago','University of California, Los Angeles','NYU']
    kms = [10,15,25]
    def circleLayer(targetLocations:list, kms:list):
        # coords = [(lon, lat)]
        # buffer = Point(coords).buffer(km * 1000)
        layers = []
        features = []
        for target,km in zip(targetLocations,kms):
            targetLoc = geolocator.geocode(target)
            lat, lon = targetLoc.latitude, targetLoc.longitude
# create buffer layer 
            features.append({ "type": "Feature", "geometry": {"type": "LineString","coordinates": geodesic_point_buffer(lat, lon, km)}})
            layers.append(dict(
            sourcetype = 'geojson',
            source={"type": "FeatureCollection", 'features': features},           
            color= 'maroon',
            type = 'fill',   
            opacity=0.2,
            line=dict(width=1.5),
            below = "state-label-sm"
            ))
        return layers
    layers = circleLayer(targetLocs, kms)
    figMap = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df.fips, z=df.unemp,
                                    colorscale="Viridis", zmin=0, zmax=12,
                                    marker_opacity=0.5, marker_line_width=0))
    figMap.add_scattermapbox(lat =  ['45.5017','48.304'],
                      lon = ['-73.5673','72.571'],
                      mode = 'markers+text',
                      text = ['Montreal','Random Place'],  #a list of strings, one  for each geographical position  (lon, lat)              
                    #   below='',                 
                      marker_size=12, marker_color=['rgb(235, 0, 100)','rgb(0, 0, 100)'])

    figMap.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=3, mapbox_center = {"lat": 37.0902, "lon": -95.7129},mapbox_layers=layers)
    figMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    if diff_1 >= 0:
        a =   dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>+{0}{1}{2}</sub>".format('$',diff_1,'M')], style = {'textAlign':'center'})

    elif diff_1 < 0:

        a =    dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>-{0}{1}{2}</sub>".format('$',np.abs(diff_1),'M')], style = {'textAlign':'center'})

    if diff_holi >= 0:
        b =   dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>+{0}{1}{2}</sub>".format('$',diff_holi,'M')], style = {'textAlign':'center'})

    elif diff_holi < 0:

        b =   dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>-{0}{1}{2}</sub>".format('$',np.abs(diff_holi),'M')], style = {'textAlign':'center'})

    if diff_store >= 0:
        c =   dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>+{0}</sub>".format(diff_store)], style = {'textAlign':'center'})

    elif diff_store < 0:

        c =   dcc.Markdown( dangerously_allow_html = True,
                   children = ["<sub>-{0}</sub>".format(np.abs(diff_store))], style = {'textAlign':'center'})



    card_content = [

        dbc.CardBody(
            [
                html.H6('Total Import Value for NA2 Code', style = {'fontWeight':'lighter', 'textAlign':'center'}),

                html.H3('{0}{1}{2}'.format("$", sales_base, "M"), style = {'color':'#090059','textAlign':'center'}),

                a

                ]

            )
        ]

    card_content1 = [

        dbc.CardBody(
            [
                html.H6('Total Import Value for Selected NA6 Code', style = {'fontWeight':'lighter', 'textAlign':'center'}),

                html.H3('{0}{1}{2}'.format("$", holi_base, "M"), style = {'color':'#090059','textAlign':'center'}),

                b

                ]

            )
        ]
    
    card_content7 = [

        dbc.CardBody(
            [
                html.H6('Break down of Import Volume by Air or Vessel', style = {'fontWeight':'bold', 'textAlign':'center'}),

                dcc.Graph(figure = figMap, style = {'height':'700px'})


                ]

            )
        ]

    card_content2 = [

        dbc.CardBody(
            [
                html.H6('Total Line Items for Selected NA6 Codes', style = {'fontWeight':'lighter', 'textAlign':'center'}),

                html.H3('{0}'.format( base_st_ct), style = {'color':'#090059','textAlign':'center'}),

                c

                ]

            )
        ]

    card_content3 = [

        dbc.CardBody(
            [
                html.H6('Top 10 HS items Imported by Dollar Value with in NA6 Code', style = {'fontWeight':'bold', 'textAlign':'center'}),

                dcc.Graph(figure = fig, style = {'height':'250px'})


                ]

            )
        ]


    card_content4 = [

        dbc.CardBody(
            [
                html.H6('Top Import Districts for Selected NAICS Code', style = {'fontWeight':'bold', 'textAlign':'center'}),

                dbc.Row([
                    dbc.Col([dcc.Graph(figure = fig2, style = {'height':'300px'}),
                ]),
                    dbc.Col([dcc.Graph(figure = fig3, style = {'height':'300px'}),
                ])

                    ])



                ]

            )
        ]

    card_content5 = [

        dbc.CardBody(
            [
                html.H6('Total YoY Growth of Import Value', style = {'fontWeight':'bold', 'textAlign':'center'}),

                dcc.Graph(figure = fig4, style = {'height':'300px'})


                ]

            )
        ]



    return card_content, card_content1, card_content2,card_content3,card_content7,card_content4,card_content5,
