import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from urllib.request import urlopen
from mplsoccer import Pitch, add_image
from scipy.ndimage import gaussian_filter
import base64
import io
from PIL import Image


game_options = {
    'ARG-AUS': 'ARG-AUS-round16.csv',
    'ARG-CRO': 'ARG-CRO-semi-final.csv',
    'ARG_FRA': 'the-final.csv',
    'BRA-KOR': 'BRA-KOR-round16.csv',
    'CRO-JPN': 'CRO-JPN-round16.csv',
    'ENG-SEN': 'ENG-SEN-round16.csv',
    'FRA-POL': 'FRA-POL-round16.csv',
    'MAR-ESP': 'MAR-ESP-round16.csv',
    'MAR-FRA': 'MAR-FRA-semi-final.csv',
    'NED-USA': 'NED-USA-round16.csv',
    'POR-SUI': 'POR-SUI-round16.csv',
}

player_images = {
    'Messi': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
             '/Lionel_Messi_12066-63f4ed9919dc5.png',
    'Modric': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
              '/Luka_Modric_13117-637ff9595f715.png',
    'Mbappe': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
              '/Kylian_Mbappe_67592-5b3924d373c70.jpeg',
    'Ziyech': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
              '/Hakim_Ziyech_60795-63a7d6b1807d0.png',
    'Ronaldo': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
               '/Cristiano_Ronaldo_5279-5f53c678df28d.jpeg',
    'Kane': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
            '/Harry_Kane_58737-5b37bf00d95c1.jpeg',
    'Neymar': 'https://www.national-football-teams.com/media/cache/players_page/uploads/person_photos'
              '/Neymar_39625-5b4be3cd9a349.jpeg',
    # Add other players here
}

player_data = pd.read_csv('player-stats.csv', encoding='unicode_escape')
exp_data = pd.read_csv('Expanded_Dataset_with_Additional_Players.csv')


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # , suppress_callback_exceptions=True)
server = app.server


def process_csv_data(filename):
    df = pd.read_csv(filename)
    x_values = df.iloc[:, 4]
    y_values = df.iloc[:, 5]

    min_x, max_x = x_values.min(), x_values.max()
    min_y, max_y = y_values.min(), y_values.max()

    x_scaled = (x_values - min_x) / (max_x - min_x)
    y_scaled = 0.1 + 0.8 * (y_values - min_y) / (max_y - min_y)

    return x_scaled, y_scaled


def create_heatmap(selected_game):
    if selected_game in game_options:
        filename = game_options[selected_game]
        df = pd.read_csv(filename)
        x_values = df.iloc[:, 5]
        y_values = df.iloc[:, 4]

        #  min_y, max_y = y_values.min(), y_values.max()
        #  y_values = (y_values - min_y) / (max_y - min_y)
        #  y_values = 1 - y_values
    else:
        df = pd.read_csv('ARG-AUS-round16.csv')
        x_values = df.iloc[:, 5]
        y_values = df.iloc[:, 4]

    # Create the pitch
    pitch = Pitch(pitch_type='wyscout',  # orientation='vertical',
                  pitch_color='#22312b', line_color='#c7d5cc',
                  stripe_color='#22312b', stripe_zorder=1)
    fig, ax = pitch.draw(figsize=(10, 6))

    # Calculate bin statistics
    bin_statistic = pitch.bin_statistic(x_values, y_values, statistic='count', bins=(20, 10))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)

    # Plot the heatmap
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')

    # Add the colorbar
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    cbar.outline.set_edgecolor('#efefef')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#efefef')

    # Save the figure to a BytesIO object
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    img = Image.open(buf)

    # Flip the image vertically
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Encode the flipped image
    buf = io.BytesIO()
    img.save(buf, format='png')
    buf.seek(0)

    encoded_image = base64.b64encode(buf.read()).decode('utf-8')

    return f'data:image/png;base64,{encoded_image}'


def create_soccer_pitch(selected_game):
    if selected_game in game_options:
        filename = game_options[selected_game]
        x_scaled, y_scaled = process_csv_data(filename)
    else:
        x_scaled, y_scaled = process_csv_data('ARG-AUS-round16.csv')

    fig = go.Figure(
        layout=dict(
            shapes=[
                # Main rectangle
                dict(
                    type="rect",
                    x0=0.1,
                    y0=0,
                    x1=0.9,
                    y1=1,
                    line=dict(color="black", width=2),
                    fillcolor="rgba(0, 191, 255, 0.5)"  # Semi-transparent fill
                ),
                # middle line
                dict(
                    type="line",
                    x0=0.5,
                    y0=0,
                    x1=0.5,
                    y1=1,
                    line=dict(color="black", width=2)
                ),
                # Left goal box
                dict(
                    type="rect",
                    x0=0.1,
                    y0=.2,
                    x1=0.22,
                    y1=.8,
                    line=dict(color="black", width=2)
                ),
                # Nested left rect
                dict(
                    type="rect",
                    x0=0.1,
                    y0=.35,
                    x1=0.15,
                    y1=.65,
                    line=dict(color="black", width=2)
                ),
                # Right goal box
                dict(
                    type="rect",
                    x0=0.9,
                    y0=.2,
                    x1=0.78,
                    y1=.8,
                    line=dict(color="black", width=2)
                ),
                # Nested right rect
                dict(
                    type="rect",
                    x0=0.9,
                    y0=.35,
                    x1=0.85,
                    y1=.65,
                    line=dict(color="black", width=2)
                ),
                # Center circle
                dict(
                    type="circle",
                    xref="x",
                    yref="y",
                    x0=0.45,
                    y0=0.40,
                    x1=0.55,
                    y1=0.60,
                    line=dict(color="black", width=2)
                )
            ],
            xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, fixedrange=True),
            yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, fixedrange=True),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
    ).add_trace(
        go.Scatter(
            x=y_scaled,
            y=x_scaled,
            mode='markers',
            marker=dict(
                size=27,  # Adjust the size as needed
                color='gray',  # Choose a contrasting color
                symbol='hexagon2-open-dot'
            ),
            showlegend=False
        )
    )

    return fig


def create_player_stats_chart():
    fig = go.Figure()  # Create a new figure object

    # Add bars to the figure
    fig.add_trace(go.Bar(
        x=player_data['player'],
        y=player_data['goals'],
        name='Goals',
        text=player_data['goals'],  # Set text for each bar
        textposition='auto'  # Automatically position text
    ))
    fig.add_trace(go.Bar(
        x=player_data['player'],
        y=player_data['assists'],
        name='Assists',
        text=player_data['assists'],  # Set text for each bar
        textposition='auto'  # Automatically position text
    ))

    # Set title and update layout
    fig.update_layout(
        yaxis={'title': 'Stat Count', 'categoryorder': 'total ascending', 'showticklabels': False},
        xaxis={'title': 'Player'},  # Label x-axis
        plot_bgcolor='white',  # Set background color (optional)
        height=800,  # Increase figure height
        title='Goals & Assists',
    )

    # Update text size
    fig.update_traces(textfont_size=10)  # Set text size for all bars

    return fig


def create_team_stats_chart():
    team_data = pd.read_csv('fifa-team-stats.csv')

    fig = go.Figure()

    # Add bars for wins with green color
    fig.add_trace(go.Bar(
        x=team_data['Team'],
        y=team_data['Wins'],
        name='Wins',
        marker_color='green',
        text=team_data['Wins'],
        textposition='auto'
    ))

    # Add downward bars for losses with red color
    fig.add_trace(go.Bar(
        x=team_data['Team'],
        y=-team_data['Losses'],
        name='Losses',
        marker_color='red',
        text=team_data['Losses'],
        textposition='auto'
    ))

    # Update layout with correct y-axis range
    fig.update_layout(
        yaxis={'title': 'Count', 'range': [-1, max(team_data['Wins'])]},
        xaxis={'title': 'Team'},
        plot_bgcolor='white',
        height=800,
        barmode='group',
        title='Team Performance - Wins/Losses',
        bargroupgap=0.55,
        shapes=[
            dict(
                type='line',
                x0=-0.5, x1=-0.5,  # Leftmost line
                y0=-max(team_data['Losses']), y1=max(team_data['Wins']),
                line=dict(color='black', width=1, dash='dot')
            ),
            dict(
                type='line',
                x0=len(team_data) - 0.5, x1=len(team_data) - 0.5,  # Rightmost line
                y0=-max(team_data['Losses']), y1=max(team_data['Wins']),
                line=dict(color='black', width=1, dash='dot')
            ),
            *[(dict(
                type='line',
                x0=i - 0.5, x1=i - 0.5,
                y0=-max(team_data['Losses']), y1=max(team_data['Wins']),
                line=dict(color='black', width=1, dash='dot')
            )) for i in range(1, len(team_data))]
        ]
    )

    # Update text size
    fig.update_traces(textfont_size=10)

    return fig


def create_second_heatmap(data, title, player_image):
    pitch = Pitch(pitch_type='wyscout', line_zorder=2, pitch_color='grass', line_color='white')
    fig, ax = pitch.draw(figsize=(6.6, 4.125))
    fig.set_facecolor('#22312b')
    bin_statistic = pitch.bin_statistic(data['X'], data['Y'], statistic='count', bins=(25, 25))
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b')
    # Add the colorbar
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.5)
    cbar.outline.set_edgecolor('white')
    cbar.ax.yaxis.set_tick_params(color='#efefef')
    ticks = plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    player_image = Image.open(urlopen(player_image))
    player_image = player_image.resize((100, 100))
    add_image(player_image, fig, left=0.034, bottom=0.90, width=0.17, interpolation='hanning')
    title = ax.set_title(title, color='white', fontsize=20)
    return fig_to_html(fig)


def create_line_breaking_passes_chart(data, title, player_image):
    pitch = Pitch(pitch_type='wyscout', pitch_color='grass', line_color='black', goal_type='box')
    fig, ax = pitch.draw(figsize=(12, 8))
    pitch.arrows(data['X'], data['Y'], data['X2'], data['Y2'], ax=ax, color='red', width=2, headwidth=3)
    pitch.scatter(data['X2'], data['Y2'], s=70, facecolors='none', edgecolor='red', ax=ax)
    player_image = Image.open(urlopen(player_image))
    player_image = player_image.resize((100, 100))
    add_image(player_image, fig, left=0.034, bottom=0.90, width=0.17, interpolation='hanning')
    title = ax.set_title(title, color='black', fontsize=20)
    return fig_to_html(fig)


def fig_to_html(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    encoded_image = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_image}"


player_stats_fig = create_player_stats_chart()
team_stats_fig = create_team_stats_chart()
player_stats_fig.update_layout(
    plot_bgcolor='lightgray',
    paper_bgcolor='lightgray'
)
team_stats_fig.update_layout(
    plot_bgcolor='lightgray',
    paper_bgcolor='lightgray'
)


app.layout = html.Div([
    html.H1("World Cup Qatar 2022 - Data-Driven Explorer", style={'textAlign': 'center'}),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Nav([
                    dbc.NavLink("Games", href="/visualization", active="exact"),
                    dbc.NavLink("Top Players", href="/page-2", active="exact"),
                    dbc.NavLink("Team Performance", href="/page-3", active="exact"),
                    dbc.NavLink("Specific Visualizations", href="/page-4", active="exact")
                ],
                    vertical=True,
                    pills=True,
                    style={"height": "100vh", "padding-top": "20px"},
                )
            ],
                md=2,
                className="border-end border-2 border-secondary"),
            dbc.Col([
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content', children=[
                    dcc.Dropdown(
                        id='game-dropdown',
                        options=[{'label': i, 'value': i} for i in game_options.keys()],
                        value='ARG-AUS'
                    ),
                    dcc.Dropdown(
                        id='plot-type-dropdown',
                        options=[{'label': 'Event Positions', 'value': 'positions'},
                                 {'label': 'Density Heatmap', 'value': 'heatmap'}],
                        value='positions'
                    ),
                    # Add the new components here:
                    dcc.Dropdown(
                        id='team_dropdown',
                        options=[{'label': team, 'value': team} for team in exp_data['Team'].unique()],
                        placeholder="Select a Team"
                    ),
                    dcc.Dropdown(
                        id='player_dropdown',
                        placeholder="Select a Player"
                    ),
                    dcc.Dropdown(
                        id='visualization_dropdown',
                        options=[
                            {'label': 'Heatmap', 'value': 'heatmap'},
                            {'label': 'Chances Created', 'value': 'chances_created'},
                        ],
                        placeholder="Select Visualization Type"
                    ),
                    html.Img(id='visualization_img', style={'width': '100%', 'height': '100%'}),
                    dcc.Graph(id='graph-container')  # If you need a separate graph for heatmap
                ])
            ], md=10)
        ])
    ])
])

with open('Mbappe.png', 'rb') as f:
    top_player_image = base64.b64encode(f.read()).decode('utf-8')

image_source = f'data:image/png;base64,{top_player_image}'


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def render_page_content(pathname):
    if pathname == '/':
        return html.Div([
            html.H4('Welcome to the App!', style={'textAlign': 'center'}),
            html.H6('Please select a view', style={'textAlign': 'center'})
        ])
    elif pathname == '/visualization':
        return html.Div(children=[
            html.H4('Please select a tournament game', style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='game-dropdown',
                options=[{'label': i, 'value': i} for i in game_options.keys()],
                value='ARG-AUS'
            ),
            dcc.Dropdown(
                id='plot-type-dropdown',
                options=[{'label': 'Event Positions', 'value': 'positions'},
                         {'label': 'Density Heatmap', 'value': 'heatmap'}],
                value='positions'
            ),
            dcc.Graph(id='graph-container')
        ])
    elif pathname == "/page-2":
        return html.Div([
            dcc.Graph(figure=player_stats_fig, style={'height': '82vh'}),
            html.Hr(),
            html.Img(src=image_source, style={'width': '700px', 'height': '365px',
                                              'display': 'block', 'margin': '0 auto'})
        ])
    elif pathname == "/page-3":
        return html.Div([
            dcc.Graph(
                figure=team_stats_fig,
                style={'height': '550px'}  # Set the height to 800 pixels
            )
        ])
    elif pathname == "/page-4":
        return html.Div([
            html.H4('Heatmap and Chances Created', style={'textAlign': 'center'}),

            # Dropdown to select the team
            dcc.Dropdown(
                id='team_dropdown',
                options=[{'label': team, 'value': team} for team in exp_data['Team'].unique()],
                placeholder="Select a Team"
            ),

            # Dropdown to select the player
            dcc.Dropdown(
                id='player_dropdown',
                placeholder="Select a Player"
            ),

            # Dropdown to select visualization type
            dcc.Dropdown(
                id='visualization_dropdown',
                options=[
                    {'label': 'Heatmap', 'value': 'heatmap'},
                    {'label': 'Chances Created', 'value': 'chances_created'},

                ],
                placeholder="Select Visualization Type"
            ),

            # Generate the image
            html.Img(id='visualization_img', style={'width': '100%', 'height': '100%'})
        ])
    else:
        return html.Div(['404 Not Found'])


# Update the visualization based onn what is selected
@app.callback(
    Output('visualization_img', 'src'),
    [Input('team_dropdown', 'value'),
     Input('player_dropdown', 'value'),
     Input('visualization_dropdown', 'value')]
)
def update_visualization(selected_team, selected_player, visualization_type):
    ind_player_data = exp_data[(exp_data['Team'] == selected_team) & (exp_data['Player'] == selected_player)]
    player_image = player_images.get(selected_player,
                                     'https://img.a.transfermarkt.technology/portrait/header/28003-1710080339.jpg?lm=1')
    if visualization_type == 'heatmap':
        return create_second_heatmap(ind_player_data, f"{selected_player}'s Heatmap", player_image)
    elif visualization_type == 'chances_created':
        return create_line_breaking_passes_chart(ind_player_data, f"{selected_player}'s Line-Breaking Passes", player_image)
    else:
        return None


# Update player options based on selected team
@app.callback(
    Output('player_dropdown', 'options'),
    Input('team_dropdown', 'value')
)
def update_player_dropdown(selected_team):
    # The following will generate the player dropdown after the team is selected
    if selected_team:
        players = exp_data[exp_data['Team'] == selected_team]['Player'].unique()
        return [{'label': player, 'value': player} for player in players]
    return []


@app.callback(
    Output('graph-container', 'figure'),
    [Input('game-dropdown', 'value'), Input('plot-type-dropdown', 'value')])
def update_graph(selected_game, plot_type):
    if plot_type == 'positions':
        fig = create_soccer_pitch(selected_game)
        fig.add_trace(
            go.Scatter(
                x=[0.185, 0.815],
                y=[0.5, 0.5],
                mode='markers',
                marker=dict(
                    size=2,
                    color='darkgray',
                    symbol='circle'
                ),
                hoverinfo='none',
                showlegend=False
            )
        )

        return fig

    elif plot_type == 'heatmap':
        image_data = create_heatmap(selected_game)

        # Create a Plotly figure with an image trace
        fig = go.Figure()
        fig.add_layout_image(
            dict(
                source=image_data,
                xref="x",
                yref="y",
                x=0,
                y=1,
                sizex=1,
                sizey=1,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )
        # Set the axis ranges
        fig.update_xaxes(range=[0, 1], showticklabels=False)
        fig.update_yaxes(range=[0, 1], showticklabels=False)

        fig.update_layout(
            plot_bgcolor='lightgray',
            paper_bgcolor='lightgray'
        )

        return fig
    else:
        return html.Div('Invalid plot type')


if __name__ == '__main__':
    app.run_server(debug=True)
