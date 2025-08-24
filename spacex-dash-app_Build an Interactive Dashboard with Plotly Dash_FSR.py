# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Unique launch-site options for the dropdown (plus "All Sites")
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in sorted(spacex_df["Launch Site"].unique())
]



# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
    id='site-dropdown',
    options=site_options,
    value='ALL',  # default to all sites
    placeholder='Select a Launch Site here',
    searchable=True,
    style={'width': '80%', 'margin': '0 auto 10px auto'},
),
html.Br(),




                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

html.P("Payload range (Kg):"),
# TASK 3: Add a slider to select payload range
#dcc.RangeSlider(id='payload-slider',...)
dcc.RangeSlider(
    id='payload-slider',
    min=0, max=10000, step=1000,
    value=[min_payload, max_payload],
    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
),

# TASK 4: Add a scatter chart to show the correlation between payload and launch success
html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Sum of successes (class=1) by site
        return px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    # Success vs Failure for a single site
    df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
    counts = df_site['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
    counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
    return px.pie(
        counts,
        values='Count',
        names='Outcome',
        title=f'Total Launch Outcomes for site {selected_site}'
    )
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    dff = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                    (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Payload vs. Launch Outcome — ' +
               (selected_site if selected_site != 'ALL' else 'All Sites'))
    )
    fig.update_yaxes(tickmode='array', tickvals=[0, 1],
                     ticktext=['Failure (0)', 'Success (1)'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
    