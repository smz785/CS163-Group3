import dash
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

dash.register_page(__name__, name='Analytics', path='/analytics')

df = pd.read_csv("C:/Users/SyedZain/Downloads/criteo-uplift-v2.1.csv", nrows=100)

visit_rate = df.groupby('treatment')['visit'].mean() * 100
conversion_rate = df.groupby('treatment')['conversion'].mean() * 100
conv_given_visit = (
    df[df['visit'] == 1]
    .groupby('treatment')['conversion']
    .mean() * 100
)


visit_lift = (visit_rate[1] - visit_rate[0]) / visit_rate[0] * 100
conv_lift  = (conversion_rate[1] - conversion_rate[0]) / conversion_rate[0] * 100

labels = ['Visit Rate', 'Conversion Rate', 'Conversion | Visit']

#CHART 1
figure_1 = go.Figure(
    data=[
        go.Bar(name = "Control",
               x=labels,
               y=[visit_rate[0], conversion_rate[0], conv_given_visit[0]]),
        go.Bar(name = "Treated",
               x=labels,
               y=[visit_rate[1], conversion_rate[1], conv_given_visit[1]])
    ]
)
figure_1.update_layout(
    barmode = "group",
    title = "Advertising Impact Across Funnel Stages",
    yaxis_title = "Rate (%)",
)

#CHART 2
figure_2 = go.Figure(
    data=[
        go.Bar(x=['Visit Lift','Conversion Lift'], y=[visit_lift, conv_lift])
    ]
)
figure_2.update_layout(
    title = 'Relative Lift from Advertising',
    yaixs_title = 'Relative Lift (%)'

)

#CHART 3
cols = ['treatment', 'visit', 'conversion', 'exposure']
corr = df[cols].corr().round(2)
fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale='RdBu',
        zmid=0,
        text=corr.values,
        texttemplate='%{text}'

    )
)
fig_corr.update_layout(title="Correlation Between Treatment and Outcomes")

#CHART 4
feature_cols = [c for c in df.columns if c.startswith('f')]

sample_df = df.sample(30000, random_state=42)

X_scaled = StandardScaler().fit_transform(sample_df[feature_cols])
X_pca = PCA(n_components=2).fit_transform(X_scaled)

fig_pca = px.scatter(
    x=X_pca[:, 0], y=X_pca[:, 1],
    color=sample_df['conversion'].astype(str),
    labels={'x': 'Principal Component 1', 'y': 'Principal Component 2', 'color': 'Conversion'},
    title='PCA Projection Colored by Conversion',
    opacity=0.4,
    color_discrete_map={'0': 'steelblue', '1': 'crimson'},
)

layout = html.Main([
    html.Section([
        html.H2("Analytics"),

        dcc.Graph(figure = figure_1),
        dcc.Graph(figure = figure_2),
        dcc.Graph(figure = fig_corr),
        dcc.Graph(figure = fig_pca),

    ])
]
)
