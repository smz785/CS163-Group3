import dash
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go

from data_store import get_precomputed


dash.register_page(__name__, name="EDA", path="/analytics")


def _empty_page(message: str):
    return html.Main([
        html.Section([
            html.H2("Exploratory Data Analysis"),
            html.Div(message, className="callout"),
        ], style={
            "maxWidth": "960px",
            "margin": "0 auto",
            "padding": "0 1rem"
        })
    ])


def layout():
    pre = get_precomputed()

    visit_rate = pre["visit_rate"]
    conversion_rate = pre["conversion_rate"]
    conv_given_visit = pre["conv_given_visit"]
    corr_df = pre["corr"]
    pca_sample = pre["pca_sample"]

    required_ok = not (
        visit_rate.empty
        or conversion_rate.empty
        or conv_given_visit.empty
    )

    if not required_ok:
        return _empty_page(
            "Precomputed EDA files are missing or could not be loaded."
        )

    v0, v1 = visit_rate.iloc[0], visit_rate.iloc[1]
    c0, c1 = conversion_rate.iloc[0], conversion_rate.iloc[1]
    cv0, cv1 = conv_given_visit.iloc[0], conv_given_visit.iloc[1]

    visit_lift = (v1 - v0) / v0 * 100 if v0 else 0
    conv_lift = (c1 - c0) / c0 * 100 if c0 else 0

    labels = ["Visit Rate", "Conversion Rate", "Conversion | Visit"]

    fig_funnel = go.Figure(data=[
        go.Bar(
            name="Control",
            x=labels,
            y=[v0, c0, cv0],
            text=[f"{v:.2f}%" for v in [v0, c0, cv0]],
            textposition="outside"
        ),
        go.Bar(
            name="Treated",
            x=labels,
            y=[v1, c1, cv1],
            text=[f"{v:.2f}%" for v in [v1, c1, cv1]],
            textposition="outside"
        ),
    ])

    fig_funnel.update_layout(
        barmode="group",
        title="Advertising Impact Across Funnel Stages",
        yaxis_title="Rate (%)"
    )

    fig_lift = go.Figure(data=[
        go.Bar(
            x=["Visit Lift", "Conversion Lift"],
            y=[visit_lift, conv_lift],
            text=[f"{v:.1f}%" for v in [visit_lift, conv_lift]],
            textposition="outside"
        )
    ])

    fig_lift.update_layout(
        title="Relative Lift from Advertising",
        yaxis_title="Relative Lift (%)"
    )

    fig_corr = go.Figure()

    if not corr_df.empty:
        # corr.csv usually has first unnamed column as row labels.
        corr = corr_df.set_index(corr_df.columns[0])

        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.round(3).values,
            texttemplate="%{text}",
        ))

        fig_corr.update_layout(
            title="Correlation Between Treatment and Outcomes"
        )

    fig_pca = go.Figure()

    if (
        not pca_sample.empty
        and {"f0", "f1", "conversion"}.issubset(pca_sample.columns)
    ):
        fig_pca = px.scatter(
            pca_sample,
            x="f0",
            y="f1",
            color=pca_sample["conversion"].astype(str),
            labels={"color": "Conversion"},
            title="Precomputed Feature Projection Sample Colored by Conversion",
            opacity=0.4,
        )

        fig_pca.update_traces(marker={"size": 3})

    def insight(text):
        return html.Blockquote(text, style={
            "borderLeft": "4px solid #888",
            "paddingLeft": "1rem",
            "color": "#555",
            "margin": "0.5rem 0 1.5rem 0",
            "fontStyle": "italic",
        })

    return html.Main([
        html.Section([

            html.H2("Exploratory Data Analysis"),

            html.H3("1. Advertising Impact Across Funnel Stages"),
            insight(
                f"Advertising increases visit rates from {v0:.2f}% to {v1:.2f}% "
                f"and conversion rates from {c0:.2f}% to {c1:.2f}%."
            ),
            dcc.Graph(figure=fig_funnel),

            html.H3("2. Relative Lift"),
            insight(
                f"Visit lift is ~{visit_lift:.1f}% and conversion lift is "
                f"~{conv_lift:.1f}% compared with control."
            ),
            dcc.Graph(figure=fig_lift),

            html.H3("3. Correlation Heatmap"),
            dcc.Graph(figure=fig_corr),

            html.H3("4. Precomputed Feature Projection Sample"),
            insight(
                "This production page uses precomputed artifacts instead of "
                "recomputing PCA from the full 14M-row dataset at request time."
            ),
            dcc.Graph(figure=fig_pca),

        ], style={
            "maxWidth": "960px",
            "margin": "0 auto",
            "padding": "0 1rem"
        })
    ])