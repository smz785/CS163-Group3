import dash
from dash import html

dash.register_page(__name__, name="Methods", path='/methods')

layout = html.Main([
    html.Section([
        html.H2("Methods & Pipeline"),
        html.P([
            "Our analysis is structured around three core hypotheses, each tested using the ",
            html.Strong("Criteo Uplift Dataset"), " — approximately 14 million observations drawn from "
            "a randomized controlled trial (RCT) of real online advertising campaigns. In an RCT, "
            "users are randomly assigned to either see an ad (treatment group) or not (control group), "
            "which means treatment assignment is independent of user characteristics by design. "
            "This allows us to measure the causal effect of advertising directly, without needing to "
            "correct for confounding variables."
        ]),

        html.Ol([
            html.Li([
                html.Strong("Exploratory Data Analysis (EDA)"), " — ",
                "Before modeling, we examined the structure and quality of the dataset. "
                "We computed summary statistics and assessed class balance: the conversion rate "
                "(the share of users who made a purchase) is approximately 0.29%, and the visit rate "
                "(users who visited the site) is approximately 4.7%, both indicating strong class imbalance — "
                "the vast majority of users do not convert or visit. Approximately 85% of users were "
                "in the treatment group. "
                "We also computed a Pearson correlation matrix across the key variables — treatment, visit, "
                "conversion, and exposure — to understand their linear relationships. Weak correlations "
                "between treatment and outcomes are expected in a low-effect randomized experiment. "
                "Finally, we applied Principal Component Analysis (PCA), a dimensionality reduction technique, "
                "to project the 12 anonymized user features (f0–f11) down to 2 dimensions after standardization. "
                "This projection, computed on a 30,000-row sample, showed no clear separation between "
                "converters and non-converters in low-dimensional space — indicating that conversion depends "
                "on complex, nonlinear feature combinations rather than a simple boundary. This motivated "
                "our choice of nonlinear models."
            ]),

            html.Li([
                html.Strong("Funnel Analysis (Hypothesis 1)"), " — ",
                "We estimated the Average Treatment Effect (ATE) — the average difference in outcomes "
                "between the treated and control groups — at two stages of the user funnel. "
                "Formally, ATE = E[Y | T=1] − E[Y | T=0], where Y is the outcome (visit or conversion) "
                "and T indicates whether the user received treatment. Because the data comes from an RCT, "
                "this difference is a valid causal estimate with no additional adjustment needed. "
                "We computed the ATE separately for site visits and conversions, and also calculated the "
                "conditional conversion rate given a visit — E[conversion | visit=1, T] — to isolate "
                "post-click purchasing behavior from top-of-funnel engagement effects."
            ]),

            html.Li([
                html.Strong("Uplift Modeling via T-Learner (Hypothesis 2)"), " — ",
                "To estimate how advertising affects different users individually, we used a technique "
                "called uplift modeling, which estimates the Conditional Average Treatment Effect (CATE) "
                "— the expected treatment effect for a specific user given their features. "
                "We implemented a T-learner, a meta-learning approach that trains two separate models: "
                "one on treated users (μ̂₁) and one on control users (μ̂₀), each predicting the probability "
                "of conversion. The individual uplift estimate for a user with features x is then "
                "τ̂(x) = μ̂₁(x) − μ̂₀(x) — the difference in predicted conversion probability between "
                "the two worlds. Both models use a ",
                html.Code("HistGradientBoostingClassifier"),
                ", a high-performance gradient boosted decision tree algorithm well-suited for large, "
                "imbalanced tabular datasets. Trained models are saved as serialized files "
                "(model_treated.pkl, model_control.pkl) to Google Cloud Storage for reuse. "
                "Users are then ranked by their τ̂(x) score and grouped into deciles (10 equal segments) "
                "to evaluate whether users predicted to benefit most from advertising actually show "
                "higher realized uplift."
            ]),

            html.Li([
                html.Strong("Policy Evaluation via Qini Curve (Hypothesis 3)"), " — ",
                "We evaluated the practical value of uplift-based targeting using a Qini curve — "
                "a metric borrowed from uplift modeling literature that measures how efficiently a model "
                "identifies users who respond to treatment. The curve plots cumulative incremental "
                "conversions (conversions gained due to advertising, above the control baseline) "
                "as a function of the percentage of users targeted, ranked by descending predicted uplift τ̂(x). "
                "A steeper curve means the model is successfully concentrating high-uplift users at the top "
                "of the ranking. The Qini coefficient — the area between the model's curve and a random "
                "targeting baseline — serves as a scalar summary of model performance, analogous to "
                "AUC-ROC (Area Under the Curve for classification models). A policy table summarizes "
                "estimated incremental conversions at select targeting thresholds (5%, 10%, 20%, 30%, 50%, and 100% of users)."
            ]),

            html.Li([
                html.Strong("Visualization & Deployment"), " — ",
                "All results are presented through an interactive multi-page Plotly Dash dashboard "
                "containerized with Docker and deployed on Google App Engine. To avoid loading the full "
                "14-million-row dataset at runtime, all model outputs (funnel metrics, decile uplift, "
                "Qini curve data, policy table) are precomputed offline and serialized as CSV files to "
                "Google Cloud Storage. The app loads these lightweight files instantly using a cached "
                "loader, making the dashboard fast and scalable without repeated model inference."
            ]),
        ], className="steps"),

        html.Div([
            "Full EDA and modeling code is available in ", html.Code("EDA.ipynb"),
            " in our project repository. Analysis was conducted in Google Colab using "
            "pandas, scikit-learn, matplotlib, and seaborn."
        ], className="callout"),
    ], id="methods")
])
