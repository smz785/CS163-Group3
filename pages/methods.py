import dash
from dash import html

dash.register_page(__name__, name="Methods", path='/methods')

layout = html.Main([
    html.Section([
        html.H2("Methods & Pipeline"),
        html.P([
            "Our analysis is structured around three core hypotheses: whether advertising primarily drives "
            "engagement or purchasing, whether treatment effects vary across user segments, and whether "
            "uplift-based targeting outperforms a treat-all strategy."
        ]),

        html.Ol([
            html.Li([
                html.Strong("Exploratory Data Analysis"), " — ",
                "We examined class balance across treatment, visit, and conversion variables; computed "
                "summary statistics; checked for missing values and duplicates; and analyzed correlations "
                "between treatment and outcomes. A PCA projection of the 12 anonymized features was used "
                "to assess whether converters form separable clusters in low-dimensional space — they do not, "
                "supporting the use of nonlinear models."
            ]),
            html.Li([
                html.Strong("Funnel Analysis (Hypothesis 1)"), " — ",
                "We computed Average Treatment Effects (ATE) at two stages of the user funnel: site visits "
                "and conversions. This included both the unconditional conversion rate and the conditional "
                "rate given a visit, allowing us to isolate where advertising has the most impact."
            ]),
            html.Li([
                html.Strong("Uplift Modeling via T-Learner (Hypothesis 2)"), " — ",
                "To estimate heterogeneous treatment effects, we trained a T-learner: two separate models, "
                "one fit on treated users and one on control users, each predicting conversion probability. "
                "The difference in predictions serves as an estimate of individual uplift. Users were then "
                "ranked by predicted uplift and grouped into deciles to evaluate model discrimination across segments."
            ]),
            html.Li([
                html.Strong("Policy Evaluation via Qini Curve (Hypothesis 3)"), " — ",
                "We evaluated targeting policies by computing cumulative incremental conversions as a function "
                "of the percentage of users targeted, ranked by predicted uplift. This produced a Qini curve "
                "comparing uplift-based targeting against a random baseline, along with a policy table "
                "quantifying incremental conversions at thresholds from 5% to 100%."
            ]),
            html.Li([
                html.Strong("Visualization & Deployment"), " — ",
                "Results are presented through an interactive Dash dashboard deployed on Google App Engine, "
                "allowing exploration of model outputs, funnel metrics, and Qini curve behavior across "
                "targeting thresholds."
            ]),
        ], className="steps"),

        html.Div([
            "Full EDA and modeling code is available in ", html.Code("EDA.ipynb"),
            " in our project repository. Analysis was conducted in Google Colab using "
            "pandas, scikit-learn, matplotlib, and seaborn."
        ], className="callout"),
    ], id="methods")
])
