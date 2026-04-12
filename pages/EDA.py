import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

dash.register_page(__name__, name='Analytics', path='/analytics')

# Loading precomputed results
visit_rate       = pd.read_csv("precomputed/visit_rate.csv", index_col=0).squeeze()
conversion_rate  = pd.read_csv("precomputed/conversion_rate.csv", index_col=0).squeeze()
conv_given_visit = pd.read_csv("precomputed/conv_given_visit.csv", index_col=0).squeeze()
corr             = pd.read_csv("precomputed/corr.csv", index_col=0)
pca_sample       = pd.read_csv("precomputed/pca_sample.csv")

# Lift calculations
v0, v1   = visit_rate.iloc[0],       visit_rate.iloc[1]
c0, c1   = conversion_rate.iloc[0],  conversion_rate.iloc[1]
cv0, cv1 = conv_given_visit.iloc[0], conv_given_visit.iloc[1]

visit_lift = (v1 - v0) / v0 * 100
conv_lift  = (c1 - c0) / c0 * 100

#Chart 1
labels = ['Visit Rate', 'Conversion Rate', 'Conversion | Visit']

figure_1 = go.Figure(data=[
    go.Bar(name='Control', x=labels, y=[v0, c0, cv0]),
    go.Bar(name='Treated', x=labels, y=[v1, c1, cv1]),
])
figure_1.update_layout(
    barmode='group',
    title='Advertising Impact Across Funnel Stages',
    yaxis_title='Rate (%)',
)

# Chart 2
figure_2 = go.Figure(data=[
    go.Bar(x=['Visit Lift', 'Conversion Lift'], y=[visit_lift, conv_lift])
])
figure_2.update_layout(
    title='Relative Lift from Advertising',
    yaxis_title='Relative Lift (%)',
)

#Chart 3
fig_corr = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.columns.tolist(),
    colorscale='RdBu',
    zmid=0,
    text=corr.values,
    texttemplate='%{text}',
))
fig_corr.update_layout(title='Correlation Between Treatment and Outcomes')

# Chart 4
feature_cols = [c for c in pca_sample.columns if c.startswith('f')]

X_scaled = StandardScaler().fit_transform(pca_sample[feature_cols])
X_pca    = PCA(n_components=2).fit_transform(X_scaled)

fig_pca = px.scatter(
    x=X_pca[:, 0], y=X_pca[:, 1],
    color=pca_sample['conversion'].astype(str),
    labels={'x': 'Principal Component 1', 'y': 'Principal Component 2', 'color': 'Conversion'},
    title='PCA Projection Colored by Conversion',
    opacity=0.4,
    color_discrete_map={'0': 'steelblue', '1': 'crimson'},
)


layout = html.Main([
    html.Section([
        html.H2("Analytics"),
        dcc.Graph(figure=figure_1),
        dcc.Graph(figure=figure_2),
        dcc.Graph(figure=fig_corr),
        dcc.Graph(figure=fig_pca),
    ])
])