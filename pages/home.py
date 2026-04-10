import dash
from dash import html

dash.register_page(__name__, name="Overview", path='/')

layout = html.Main([
    html.Section([
        html.H2("Project Overview"),
        html.P([
            "This project explores ", html.Strong("uplift modeling"),
            "— a technique for estimating the incremental impact of a treatment \
             (such as an advertisement or promotion) on individual user behavior. \
            Rather than simply predicting whether a user will convert uplift modeling identifies ",
         html.Em("who is most likely to convert because of the treatment"), "."
        ]),
        html.P([
            "Using the Criteo Uplift dataset, we perform exploratory data analysis, build predictive \
            models, and visualize conversion lift across user segments. Our goal is to understand \
            which users respond best to advertising and quantify the causal effect of treatment", "."
        ]),
        html.Div([
            html.Strong("Research Question: "),
            "Can we reliably estimate individual treatment effect \
            (ITE) from observational advertising data, and which user features are most predictive of uplift?"
            ], className="callout")
    ], id="overview")

])