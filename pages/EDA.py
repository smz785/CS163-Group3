import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from data_store import get_df

dash.register_page(__name__, name='Analytics', path='/analytics')

df = get_df()

visit_rate       = df.groupby('treatment')['visit'].mean() * 100
conversion_rate  = df.groupby('treatment')['conversion'].mean() * 100
conv_given_visit = df[df['visit'] == 1].groupby('treatment')['conversion'].mean() * 100

cols = ['treatment', 'visit', 'conversion', 'exposure']
corr = df[cols].corr()

pca_sample = df.sample(30000, random_state=42)

# Lift calculations
v0, v1   = visit_rate.iloc[0],       visit_rate.iloc[1]
c0, c1   = conversion_rate.iloc[0],  conversion_rate.iloc[1]
cv0, cv1 = conv_given_visit.iloc[0], conv_given_visit.iloc[1]

visit_lift = (v1 - v0) / v0 * 100
conv_lift  = (c1 - c0) / c0 * 100

# Summary stats from df (used in stat cards)
total_rows      = len(df)
treatment_pct   = df['treatment'].mean() * 100
conversion_mean = df['conversion'].mean() * 100
visit_mean      = df['visit'].mean() * 100

# Chart 1: Funnel Stage Comparison
labels = ['Visit Rate', 'Conversion Rate', 'Conversion | Visit']

fig_funnel = go.Figure(data=[
    go.Bar(
        name='Control',
        x=labels,
        y=[v0, c0, cv0],
        text=[f'{v:.2f}%' for v in [v0, c0, cv0]],
        textposition='outside',
        marker_color='steelblue',
    ),
    go.Bar(
        name='Treated',
        x=labels,
        y=[v1, c1, cv1],
        text=[f'{v:.2f}%' for v in [v1, c1, cv1]],
        textposition='outside',
        marker_color='crimson',
    ),
])
fig_funnel.update_layout(
    barmode='group',
    title='Advertising Impact Across Funnel Stages',
    yaxis_title='Rate (%)',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
)

# Chart 2: Relative Lift
fig_lift = go.Figure(data=[
    go.Bar(
        x=['Visit Lift', 'Conversion Lift'],
        y=[visit_lift, conv_lift],
        text=[f'{v:.1f}%' for v in [visit_lift, conv_lift]],
        textposition='outside',
        marker_color=['steelblue', 'crimson'],
    )
])
fig_lift.update_layout(
    title='Relative Lift from Advertising',
    yaxis_title='Relative Lift (%)',
)

# Chart 3: Correlation Heatmap
fig_corr = go.Figure(data=go.Heatmap(
    z=corr.values,
    x=corr.columns.tolist(),
    y=corr.columns.tolist(),
    colorscale='RdBu',
    zmid=0,
    text=corr.round(3).values,
    texttemplate='%{text}',
))
fig_corr.update_layout(title='Correlation Between Treatment and Outcomes')

# Chart 4: PCA Projection
feature_cols = [c for c in pca_sample.columns if c.startswith('f')]
X_scaled = StandardScaler().fit_transform(pca_sample[feature_cols])
X_pca    = PCA(n_components=2).fit_transform(X_scaled)

fig_pca = px.scatter(
    x=X_pca[:, 0], y=X_pca[:, 1],
    color=pca_sample['conversion'].astype(str),
    labels={
        'x': 'Principal Component 1',
        'y': 'Principal Component 2',
        'color': 'Conversion',
    },
    title='PCA Projection Colored by Conversion',
    opacity=0.4,
    color_discrete_map={'0': 'steelblue', '1': 'crimson'},
)
fig_pca.update_traces(marker=dict(size=3))

# Helper: insight card
def insight(text):
    return html.Blockquote(text, style={
        'borderLeft': '4px solid #888',
        'paddingLeft': '1rem',
        'color': '#555',
        'margin': '0.5rem 0 1.5rem 0',
        'fontStyle': 'italic',
    })

def stat_card(label, value):
    return html.Div([
        html.Span(value, style={'fontSize': '1.6rem', 'fontWeight': 'bold'}),
        html.Br(),
        html.Span(label, style={'fontSize': '0.85rem', 'color': '#666'}),
    ], style={
        'border': '1px solid #ddd',
        'borderRadius': '8px',
        'padding': '1rem 1.5rem',
        'textAlign': 'center',
        'minWidth': '160px',
        'background': '#fafafa',
    })

# Layout
layout = html.Main([
    html.Section([
        html.H2("Exploratory Data Analysis"),

        # Section 1: Dataset Overview
        html.H3("1. Dataset Overview"),
        html.P(
            "The dataset contains ~14 million observations from a randomized "
            "online advertising experiment. Key variables are treatment (ad shown), "
            "conversion (purchase), visit (site visit), and anonymized user features."
        ),
        html.Div([
            stat_card("Total Observations",  f"{total_rows:,}"),
            stat_card("Treatment Rate",      f"{treatment_pct:.1f}%"),
            stat_card("Conversion Rate",     f"{conversion_mean:.2f}%"),
            stat_card("Visit Rate",          f"{visit_mean:.2f}%"),
        ], style={
            'display': 'flex', 'gap': '1rem',
            'flexWrap': 'wrap', 'margin': '1rem 0 2rem 0',
        }),

        # Section 2: Data Quality
        html.H3("2. Data Quality"),
        insight(
            "No missing values were detected. ~1.63M rows share identical feature values — "
            "1.26M are exact duplicates across all columns, while 0.37M share features but "
            "differ in treatment or outcomes. These represent different users or impressions, "
            "not data errors. All rows were retained to preserve experimental structure."
        ),

        # Section 3: Summary Statistics
        html.H3("3. Summary Statistics"),
        insight(
            "Conversion rate ≈ 0.29% and visit rate ≈ 4.7% reveal strong class imbalance — "
            "most users do not convert or visit. ~85% of users received treatment, so the "
            "treated/control split is also imbalanced. This reinforces the need for uplift "
            "modeling rather than standard classification."
        ),

        # Section 4: Funnel Chart
        html.H3("4. Advertising Impact Across Funnel Stages"),
        insight(
            f"Advertising increases visit rates from {v0:.2f}% (control) to {v1:.2f}% (treated). "
            f"Conversion rates rise from {c0:.2f}% to {c1:.2f}%. Among users who visited, "
            f"the treated group shows higher conversion ({cv1:.2f}% vs {cv0:.2f}%), suggesting "
            "ads both drive traffic and influence purchasing behavior."
        ),
        dcc.Graph(figure=fig_funnel),

        # Section 5: Lift Chart
        html.H3("5. Relative Lift from Advertising"),
        insight(
            f"Conversion lift is ~{conv_lift:.0f}% and visit lift is ~{visit_lift:.0f}%. "
            "While the absolute conversion increase is small, the relative lift shows advertising "
            "meaningfully improves outcomes compared to no treatment."
        ),
        dcc.Graph(figure=fig_lift),

        # Section 6: Correlation Heatmap
        insight(
            f"Treatment correlates weakly with visit ({corr.loc['treatment', 'visit']:.3f}) "
            f"and conversion ({corr.loc['treatment', 'conversion']:.3f}) — "
            "expected in a randomized experiment with modest average effects. "
            f"Visit and conversion share a stronger correlation ({corr.loc['visit', 'conversion']:.3f}), "
            "consistent with the funnel structure (visit → conversion). "
            f"Exposure moderately correlates with visit ({corr.loc['exposure', 'visit']:.3f}), "
            "indicating more ad exposure drives engagement."
        ),
        dcc.Graph(figure=fig_corr),

        # Section 7: PCA
        html.H3("7. PCA Projection Colored by Conversion"),
        insight(
            "Converters (red) are spread throughout the feature space with no clear cluster "
            "separating them from non-converters (blue). Conversion likely depends on complex "
            "feature combinations rather than a simple linear boundary — supporting the use "
            "of nonlinear uplift models."
        ),
        dcc.Graph(figure=fig_pca),

    ], style={'maxWidth': '960px', 'margin': '0 auto', 'padding': '0 1rem'}),
])