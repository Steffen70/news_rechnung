import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

# Dash-App initialisieren
app = dash.Dash(__name__)

# Layout der App
app.layout = html.Div([
    html.H1("Journalisten vs. DAU Visualisierung"),
    dcc.Graph(id='graph'),
    html.Label("Banner pro Artikel:"),
    dcc.Slider(
        id='banner-slider',
        min=1,
        max=3,
        step=0.1,
        value=1.5,
        marks={i: str(i) for i in range(1, 4)}
    ),
    html.Label("Max. DAU (Y-Achse):"),
    dcc.Slider(
        id='dau-slider',
        min=100000,  # Minimum 100k
        max=2000000,  # Maximum 2m
        step=100000,  # Schrittweite 100k
        value=100000,  # Standardwert 100k
        marks={i: f"{i:,}" for i in range(100000, 2000001, 500000)}
    ),
    html.Label("Artikel pro Tag pro Journalist:"),
    dcc.Slider(
        id='artikel-slider',
        min=0.5,
        max=5,
        step=0.5,
        value=1,  # Standardwert 1.5 Artikel/Tag
        marks={i: str(i) for i in range(1, 6)}
    )
])

# Callback für dynamische Aktualisierung
@app.callback(
    Output('graph', 'figure'),
    [Input('banner-slider', 'value'), Input('dau-slider', 'value'), Input('artikel-slider', 'value')]
)
def update_graph(banner_pro_artikel, max_dau, artikel_pro_tag):
    # Fixe Werte
    lohn_pro_feed = 12000
    feeds_pro_user = 2.5
    tage_pro_jahr = 360  # Annahme: 360 aktive Tage pro Jahr
    artikel_pro_jahr = artikel_pro_tag * tage_pro_jahr  # Dynamische Artikelanzahl
    
    # DAU-Bereich dynamisch an max_dau anpassen (Schrittweite 1% von max_dau)
    step_size = max_dau // 100
    dau_range = np.arange(1000, max_dau + 1, step_size)
    
    # CPM als Funktion von DAU
    cpm = [3 if d < 10000 else 8 if d <= 50000 else 12 for d in dau_range]
    
    # Max. finanzierbare Journalisten berechnen
    max_journalisten = []
    hover_text = []
    for d, c in zip(dau_range, cpm):
        # Impressionen pro Journalist für 12’000 CHF
        impressionen_pro_journalist = lohn_pro_feed / (c / 1000)
        # DAU pro Journalist (pro Feed)
        dau_pro_journalist = impressionen_pro_journalist / (banner_pro_artikel * artikel_pro_jahr)
        # Max. Journalisten unter Berücksichtigung von Feeds pro User
        max_j = d / (dau_pro_journalist * feeds_pro_user)
        max_journalisten.append(max_j)
        # Verhältnis für Hover
        verhältnis = d / max_j if max_j > 0 else 0
        hover_text.append(f"App-Nutzer: {d:,}<br>Journalisten: {max_j:.2f}<br>DAU/Journalist: {verhältnis:.2f}")
    
    # Graph erstellen
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=max_journalisten,
        y=dau_range,
        mode='lines',
        name=f'Banner: {banner_pro_artikel}, Artikel/Tag: {artikel_pro_tag}',
        text=hover_text,
        hoverinfo='text'
    ))
    fig.update_layout(
        title='Max. finanzierbare Journalisten vs. App-Nutzer (DAU)',
        xaxis_title='Anzahl finanzierbarer Journalisten',
        yaxis_title='Anzahl App-Nutzer (DAU)',
        hovermode='closest',
        yaxis=dict(range=[0, max_dau])
    )
    return fig

# App starten
if __name__ == '__main__':
    app.run_server(debug=True)