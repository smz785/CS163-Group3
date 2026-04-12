import dash
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path='/preliminary_results', name='Preliminary Results')

# ── Load precomputed results (from full 14M row analysis) ─────────
visit_rate       = pd.read_csv("precomputed/visit_rate.csv", index_col=0).squeeze()
conversion_rate  = pd.read_csv("precomputed/conversion_rate.csv", index_col=0).squeeze()
conv_given_visit = pd.read_csv("precomputed/conv_given_visit.csv", index_col=0).squeeze()
decile_df        = pd.read_csv("precomputed/decile_uplift.csv")
qini_tbl         = pd.read_csv("precomputed/qini_table.csv")
policy_df        = pd.read_csv("precomputed/policy_table.csv")

# ── Derived values ────────────────────────────────────────────────
v0, v1   = visit_rate.iloc[0] * 100,       visit_rate.iloc[1] * 100
c0, c1   = conversion_rate.iloc[0] * 100,  conversion_rate.iloc[1] * 100
cv0, cv1 = conv_given_visit.iloc[0] * 100, conv_given_visit.iloc[1] * 100

ate_visit = v1 - v0
ate_conv  = c1 - c0
ate_cv    = cv1 - cv0

# ── Chart 1: Funnel Bar Chart ─────────────────────────────────────
funnel_labels = ['Visit Rate', 'Conversion Rate', 'Conversion | Visit']
fig_funnel = go.Figure(data=[
    go.Bar(name='Control', x=funnel_labels, y=[v0, c0, cv0],
           marker_color='#2c5f8a',
           text=[f'{v:.2f}%' for v in [v0, c0, cv0]], textposition='outside'),
    go.Bar(name='Treated', x=funnel_labels, y=[v1, c1, cv1],
           marker_color='#e8a020',
           text=[f'{v:.2f}%' for v in [v1, c1, cv1]], textposition='outside'),
])
fig_funnel.update_layout(
    barmode='group',
    title='Advertising Impact Across Funnel Stages',
    yaxis_title='Rate (%)',
    plot_bgcolor='white', paper_bgcolor='white',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(t=60, b=40),
)

# ── Chart 2: Uplift by Decile ─────────────────────────────────────
deciles     = decile_df['decile'].tolist()
uplift_vals = decile_df['uplift_pp'].tolist()
bar_colors  = ['#c0392b' if v < 0 else '#2c5f8a' for v in uplift_vals]

fig_decile = go.Figure(data=[
    go.Bar(
        x=deciles, y=uplift_vals,
        marker_color=bar_colors,
        text=[f'{v:.3f}' for v in uplift_vals],
        textposition='outside',
    )
])
fig_decile.update_layout(
    title='Realized Conversion Uplift by Predicted-Uplift Decile (T-Learner)',
    xaxis_title='Decile (1 = highest predicted uplift)',
    yaxis_title='Realized uplift (percentage points)',
    xaxis=dict(tickmode='linear', dtick=1),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(t=60, b=40),
)

# ── Chart 3: Qini Curve ───────────────────────────────────────────
fig_qini = go.Figure()
fig_qini.add_trace(go.Scatter(
    x=[0] + qini_tbl['Top % targeted'].tolist(),
    y=[0] + qini_tbl['Cumulative incremental conversions'].tolist(),
    mode='lines+markers', name='Uplift targeting (Qini curve)',
    line=dict(color='#2c5f8a', width=2.5), marker=dict(size=7),
))
fig_qini.add_trace(go.Scatter(
    x=[0] + qini_tbl['Top % targeted'].tolist(),
    y=[0] + qini_tbl['Random baseline'].tolist(),
    mode='lines', name='Random targeting baseline',
    line=dict(color='#e8a020', width=2, dash='dash'),
))
fig_qini.update_layout(
    title='Qini Curve: Incremental Conversions vs % Targeted',
    xaxis_title='Top % of users targeted (ranked by predicted uplift)',
    yaxis_title='Cumulative incremental conversions',
    plot_bgcolor='white', paper_bgcolor='white',
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    margin=dict(t=60, b=40),
)

# ── Reusable components ───────────────────────────────────────────
def metric_card(label, value, delta=None):
    return html.Div([
        html.Div(label, className='metric-label'),
        html.Div(value, className='metric-value'),
        html.Div(delta, className='metric-delta') if delta else None,
    ], className='metric-card')

def callout(text):
    return html.Div(text, className='callout')

def insight_box(title, items):
    return html.Div([
        html.Strong(title),
        html.Ul([html.Li(i) for i in items])
    ], className='insight-box')

# ── Layout ────────────────────────────────────────────────────────
layout = html.Div([

    # ── Executive Summary ─────────────────────────────────────────
    html.Section([
        html.H2("Executive Summary"),
        html.P(
            "This report presents a comprehensive causal analysis of the Criteo uplift dataset "
            "to evaluate the incremental effectiveness of online advertising. Unlike traditional "
            "predictive modeling approaches that focus on identifying users likely to convert, "
            "this analysis emphasizes incremental impact — specifically how advertising changes "
            "user behavior relative to a control condition."
        ),
        html.P("Three key hypotheses are investigated:"),
        html.Ol([
            html.Li("Whether advertising primarily drives engagement or purchasing behavior."),
            html.Li("Whether treatment effects vary across user segments."),
            html.Li("Whether uplift-based targeting strategies outperform a treat-all approach."),
        ]),
        callout(
            "Key finding: While advertising increases both site visits and conversions, its overall "
            "effect is modest and highly uneven across the population. A small subset of users "
            "contributes disproportionately to incremental gains."
        ),
    ], className='result-section'),

    # ── Hypothesis 1 ─────────────────────────────────────────────
    html.Section([
        html.H2("Hypothesis 1: Advertising Impact Across Funnel Stages"),
        html.Div([
            metric_card("Visit Rate — Control",      f"{v0:.2f}%"),
            metric_card("Visit Rate — Treated",      f"{v1:.2f}%", f"ATE: +{ate_visit:.3f} pp"),
            metric_card("Conversion Rate — Control", f"{c0:.2f}%"),
            metric_card("Conversion Rate — Treated", f"{c1:.2f}%", f"ATE: +{ate_conv:.3f} pp"),
            metric_card("Conv | Visit — Control",    f"{cv0:.2f}%"),
            metric_card("Conv | Visit — Treated",    f"{cv1:.2f}%", f"ATE: +{ate_cv:.3f} pp"),
        ], className='metric-grid'),
        dcc.Graph(figure=fig_funnel),
        html.H3("Key Insight"),
        html.P(
            "The advertising intervention influences both stages of the user funnel, but not equally. "
            "The primary effect is at the awareness stage (visits), indicating that advertising is "
            "effective in driving engagement. A secondary effect exists at the conversion stage, where "
            "treated users who visit are more likely to purchase. However, due to the extremely low "
            "baseline conversion rate, the absolute conversion gain remains small."
        ),
        callout(
            "Advertising generates approximately 1 additional conversion per ~870 users shown an ad."
        ),
        html.H3("Implications"),
        html.P(
            "This refutes the common assumption that advertising mainly drives purchases. Conversion "
            "improvements depend not only on exposure but also on what happens after the user arrives "
            "on the site."
        ),
        insight_box("Next Steps", [
            "Improve post-click experience (landing pages, UI, pricing) to convert increased traffic into purchases.",
            "Segment users based on visit behavior to understand where conversion drop-off occurs.",
            "Combine funnel analysis with uplift modeling to identify users who are both likely to visit and convert.",
        ]),
        insight_box("Broader Impacts", [
            "Focusing only on driving traffic may lead to inefficient systems that prioritize clicks over meaningful outcomes.",
            "This can inflate engagement metrics without improving revenue.",
            "Excessive ad exposure without meaningful value may degrade user experience and trust.",
        ]),
    ], className='result-section'),

    # ── Hypothesis 2 ─────────────────────────────────────────────
    html.Section([
        html.H2("Hypothesis 2: Heterogeneous Treatment Effects"),
        html.P(
            "The uplift-by-decile analysis reveals that advertising effectiveness varies substantially "
            "across user segments. The highest predicted uplift group (Decile 1) achieves a realized "
            "uplift approximately five times larger than the overall average treatment effect."
        ),
        html.P(
            "In contrast, most deciles show uplift values close to zero, indicating that for the "
            "majority of users, advertising has little to no effect. A small segment even exhibits "
            "slightly negative uplift, suggesting advertising may be counterproductive for some users."
        ),
        html.H3("What the T-Learner Does"),
        html.P(
            "To estimate these differences, we use a T-learner (HistGradientBoostingClassifier), "
            "which trains two separate models: one on treated users and one on control users. "
            "The difference between their predictions gives an estimate of individual uplift. "
            "Users are then ranked by predicted uplift and grouped into deciles."
        ),
        dcc.Graph(figure=fig_decile),
        callout(
            "Key Insight: The impact of advertising is not uniform. It is highly concentrated in a "
            "small subset of users — commonly referred to as 'persuadables'."
        ),
        insight_box("Next Steps", [
            "Improve model stability and ranking consistency.",
            "Explore alternative uplift methods (e.g., X-learner, DR-learner).",
            "Analyze feature importance to better understand drivers of high uplift.",
        ]),
        insight_box("Broader Impacts", [
            "Segment-based targeting can significantly improve efficiency but must be implemented carefully.",
            "Over-targeting specific groups may introduce bias or unequal exposure.",
            "Fairness and transparency should be considered when deploying uplift-based strategies.",
        ]),
    ], className='result-section'),

    # ── Hypothesis 3 ─────────────────────────────────────────────
    html.Section([
        html.H2("Hypothesis 3: Policy Evaluation and Targeting Efficiency"),
        html.P(
            "The policy evaluation results show that uplift-based targeting significantly outperforms "
            "both random targeting and a treat-all strategy. The Qini curve demonstrates strong gains "
            "in the early targeting range, indicating that the model effectively ranks users by their "
            "responsiveness to advertising."
        ),
        callout(
            "Targeting only the top 10% of users captures roughly 50% of total incremental conversions, "
            "despite using only a small fraction of impressions."
        ),
        dcc.Graph(figure=fig_qini),

        html.H3("Qini Table"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Top % Targeted"),
                html.Th("Cumulative Incremental Conversions"),
                html.Th("Random Baseline"),
                html.Th("Qini (over random)"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(f"{int(row['Top % targeted'])}%"),
                    html.Td(f"{row['Cumulative incremental conversions']:,.2f}"),
                    html.Td(f"{row['Random baseline']:,.2f}"),
                    html.Td(
                        f"{row['Qini (over random)']:+,.2f}",
                        style={'color': '#2c5f8a' if row['Qini (over random)'] >= 0 else '#c0392b',
                               'fontWeight': 'bold'}
                    ),
                ])
                for _, row in qini_tbl.iterrows()
            ])
        ]),

        html.H3("Policy Table"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Policy"),
                html.Th("Estimated Incremental Conversions"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(row['Policy']),
                    html.Td(f"{row['Estimated incremental conversions']:,.2f}"),
                ])
                for _, row in policy_df.iterrows()
            ])
        ]),

        html.H3("Key Insight"),
        html.P(
            "Targeting the top 10% achieves ~50% of the total incremental conversions. "
            "This demonstrates that most advertising impact is concentrated in a small subset "
            "of users, and that precision in targeting is more important than scale."
        ),
        insight_box("Potential Business Actions", [
            "Select an optimal targeting threshold (e.g., top 10–20%) based on business objectives and budget.",
            "Incorporate cost and revenue metrics to evaluate profit, not just conversions.",
            "Validate the targeting policy through online A/B testing before deployment.",
        ]),
        insight_box("Broader Impacts", [
            "Uplift-based targeting can improve efficiency by reducing unnecessary ad exposure.",
            "Selective targeting raises ethical considerations around fairness and exclusion.",
            "Fairness checks and transparency are important when deploying targeting strategies.",
        ]),
    ], className='result-section'),
])