import dash
from dash import html

dash.register_page(__name__, name="Dataset", path='/dataset')

layout = html.Main([
    html.Section([
        html.H2("Dataset"),
        html.P([
            "We use the ", html.Strong("Criteo Uplift Modeling Dataset v2.1"),
            ", a large-scale benchmark dataset released by Criteo for causal inference and uplift research. "
            "It contains approximately 13.98 million observations drawn from a randomized controlled trial "
            "of real online advertising campaigns, making it one of the largest publicly available datasets "
            "for uplift modeling."
        ]),

        html.Table([
            html.Thead(html.Tr([html.Th("Property"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td("Source"),               html.Td("Criteo AI Lab")]),
                html.Tr([html.Td("Rows"),                 html.Td("~13,979,592")]),
                html.Tr([html.Td("Anonymized Features"),  html.Td("12 continuous numeric features (f0–f11)")]),
                html.Tr([html.Td("treatment"),            html.Td("Binary — 1 if user was shown an ad, 0 otherwise (~85% treated)")]),
                html.Tr([html.Td("visit"),                html.Td("Binary outcome — 1 if user visited the site (~4.7% positive rate)")]),
                html.Tr([html.Td("conversion"),           html.Td("Binary outcome — 1 if user made a purchase (~0.29% positive rate)")]),
                html.Tr([html.Td("exposure"),             html.Td("Binary — whether the user was actually exposed to the ad")]),
                html.Tr([html.Td("Storage"),              html.Td("criteo-uplift-v2.1.csv (hosted on Google Cloud Storage)")]),
            ])
        ]),

        html.P([
            "The dataset is structured as a randomized experiment, meaning treatment assignment is "
            "independent of user features by design. This allows us to estimate causal effects directly "
            "from the data without needing to correct for confounding."
        ], style={"marginTop": "1.2rem"}),

        html.P([
            "Both outcome variables exhibit strong class imbalance — the median for both ",
            html.Code("conversion"), " and ", html.Code("visit"),
            " is 0, with positive outcomes being rare. This reinforces the need for uplift modeling "
            "rather than standard classification, as predicting the most common outcome would trivially "
            "ignore the minority of high-value users."
        ]),

        html.Div([
            html.Strong("Data Quality: "),
            "No missing values were detected. Approximately 1.26 million rows are exact duplicates "
            "across all columns, while an additional 0.37 million share identical feature values but "
            "differ in treatment assignment or outcomes. These were retained to preserve the experimental "
            "structure of the dataset."
        ], className="callout"),

        html.P([
            "The dataset was obtained from the ",
            html.A("Criteo AI Lab", href="https://ailab.criteo.com/ressources/", target="_blank"),
            ". All features are anonymized and pre-processed by Criteo prior to release."
        ], style={"marginTop": "1rem", "fontSize": "0.88rem", "color": "#555"}),
    ], id="dataset")
])
