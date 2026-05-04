import dash
from dash import html

dash.register_page(__name__, name="Methods", path='/methods')

layout = html.Main([

    # ── Overview ──────────────────────────────────────────────────────────────
    html.Section([
        html.H2("Methods & Pipeline"),
        html.P([
            "This page documents the full methodology behind our analysis of the ",
            html.Strong("Criteo Uplift Dataset"),
            " — ~14 million observations from a randomized controlled trial (RCT) of real "
            "online advertising campaigns. Rather than predicting who will buy, our goal is "
            "to measure ",
            html.Em("how much showing an ad changes each user's probability of conversion"),
            ". The sections below build from first principles to the full modeling pipeline.",
        ]),
    ], id="methods"),

    # ── Core Problem ──────────────────────────────────────────────────────────
    html.Section([
        html.H3("The Core Problem"),
        html.P([
            "The naive approach to advertising is to predict “who will buy?” and show ads "
            "to them. But that’s the wrong question for targeting. Some users were going to buy ",
            html.Em("anyway"),
            " — showing them an ad wastes budget. Others actively dislike ads and won’t buy ",
            html.Em("because"),
            " of them.",
        ]),
        html.P([
            "What we actually want to know is: ",
            html.Strong("for each user, how much does the ad change their behavior?"),
            " This delta — the causal effect of the treatment on a specific individual — "
            "is called the ",
            html.Strong("Individual Treatment Effect (ITE)"),
            ", or more broadly, the ",
            html.Strong("uplift"),
            ".",
        ]),
        html.P("Uplift thinking naturally reveals four user archetypes:"),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Type"), html.Th("Without Ad"), html.Th("With Ad"),
                html.Th("Uplift"), html.Th("Strategy"),
            ])),
            html.Tbody([
                html.Tr([html.Td(html.Strong("Persuadables")), html.Td("Won’t buy"), html.Td("Will buy"),       html.Td("High ✓"),    html.Td("Target these")]),
                html.Tr([html.Td(html.Strong("Sure Things")),  html.Td("Will buy"),        html.Td("Will buy"),       html.Td("~Zero"),           html.Td("Don’t waste spend")]),
                html.Tr([html.Td(html.Strong("Lost Causes")),  html.Td("Won’t buy"), html.Td("Won’t buy"), html.Td("~Zero"),           html.Td("Don’t bother")]),
                html.Tr([html.Td(html.Strong("Sleeping Dogs")),html.Td("Will buy"),        html.Td("Won’t buy"), html.Td("Negative ⚠"), html.Td("Actively avoid")]),
            ]),
        ], className="user-types-table"),
        html.P([
            "Traditional ML (predicting conversion likelihood) cannot distinguish between these "
            "four types. Uplift modeling can. That’s the entire point of this analysis.",
        ]),
    ], className="methods-section"),

    # ── Causal Inference ──────────────────────────────────────────────────────
    html.Section([
        html.H3("The Fundamental Problem of Causal Inference"),
        html.P([
            "For any single user, you can only ever observe ",
            html.Em("one"),
            " outcome: either they saw the ad, or they didn’t. You can never run both "
            "experiments on the same person simultaneously. This is called the ",
            html.Strong("Fundamental Problem of Causal Inference"),
            " — the counterfactual outcome is always missing.",
        ]),
        html.P([
            "Formally, we want to estimate τ(x) = Y(1) − Y(0) for each user, where Y(1) "
            "is their outcome if treated and Y(0) if not. Since we observe only one of these, we "
            "cannot compute τ(x) directly. The solution is randomization.",
        ]),
    ], className="methods-section"),

    # ── RCT ───────────────────────────────────────────────────────────────────
    html.Section([
        html.H3("Randomized Experiments as the Foundation"),
        html.P([
            "The Criteo dataset comes from a ",
            html.Strong("randomized controlled trial (RCT)"),
            " — users were randomly assigned to either:",
        ]),
        html.Ul([
            html.Li([html.Strong("Treatment group"), " → shown the ad (treatment = 1)"]),
            html.Li([html.Strong("Control group"),   " → not shown the ad (treatment = 0)"]),
        ]),
        html.P([
            "Because the assignment is random, the two groups are statistically identical ",
            html.Em("on average"),
            " before the experiment. Any difference in conversion rates between the groups is "
            "therefore caused by the ad, not by pre-existing differences between users. This means "
            "the following formula is a valid causal estimate with no additional adjustment needed. "
            "This is the foundation everything else is built on.",
        ]),
        html.Pre("ATE = E[Y | T=1] − E[Y | T=0]", className="code-block formula"),
        html.Ul([
            html.Li([html.Strong("E[ ]"), " — “Expected value,” basically just the average"]),
            html.Li([html.Strong("Y"),    " — the outcome we care about (e.g. did the user convert? 1 or 0)"]),
            html.Li([html.Strong("T=1"), " — the user was in the treatment group (saw the ad)"]),
            html.Li([html.Strong("T=0"), " — the user was in the control group (did not see the ad)"]),
        ]),
        html.P([
            "Approximately ",
            html.Strong("85% of users"),
            " are in the treatment group. The overall conversion rate is ~0.29% and the visit "
            "rate is ~4.7%, both indicating strong class imbalance — motivating the use of "
            "models robust to rare positive labels.",
        ]),
    ], className="methods-section"),

    # ── T-Learner ─────────────────────────────────────────────────────────────
    html.Section([
        html.H3("The T-Learner: Two Models Instead of One"),
        html.P([
            "To estimate uplift at the individual level, we use a ",
            html.Strong("T-Learner"),
            " — a meta-learning framework where the “T” stands for “two models.” "
            "Instead of one joint model, we train two separate models on different subsets of the data:",
        ]),
        html.Ol([
            html.Li([
                html.Strong(["Treated model μ̂", html.Sub("1"), "(x)"]),
                " — trained only on users who saw the ad. It learns the relationship between "
                "user features and conversion ",
                html.Em("in the world where the ad was shown"),
                ".",
            ]),
            html.Li([
                html.Strong(["Control model μ̂", html.Sub("0"), "(x)"]),
                " — trained only on users who did not see the ad. It learns the same relationship ",
                html.Em("in the world where no ad was shown"),
                ".",
            ]),
        ]),
        html.P([
            "Both models use the same 12 anonymized feature inputs (f0–f11) but learn from "
            "disjoint subsets of the training data. After training, both are applied to the same "
            "held-out test users — users neither model has seen before — and for each "
            "user we obtain two predicted probabilities:",
        ]),
        html.Pre(
            "P(convert | ad shown)    ← from μ̂₁(x)\n"
            "P(convert | no ad shown) ← from μ̂₀(x)",
            className="code-block"
        ),
        html.P("The individual-level uplift score is then:"),
        html.Pre("τ̂(x)  =  μ̂₁(x)  −  μ̂₀(x)", className="code-block formula"),
        html.P([
            "This is the estimated counterfactual difference: how much more likely is this specific "
            "user to convert if we show them an ad versus not? The T-Learner uses the randomized "
            "groups to train two separate “world simulators,” then applies both to the "
            "same individual to approximate what ",
            html.Em("would have happened"),
            " in each world.",
        ]),
        html.H4("Uplift Score Interpretation"),
        html.Ul([
            html.Li([html.Strong("τ̂(x) > 0"), " — the ad increases conversion probability (Persuadable)"]),
            html.Li([html.Strong("τ̂(x) ≈ 0"), " — the ad has little effect (Sure Thing or Lost Cause)"]),
            html.Li([html.Strong("τ̂(x) < 0"), " — the ad may reduce conversion probability (Sleeping Dog)"]),
        ]),
    ], className="methods-section"),

    # ── HistGBM ───────────────────────────────────────────────────────────────
    html.Section([
        html.H3("The Base Model: Histogram Gradient Boosting"),
        html.P([
            "Each of the two T-Learner models is implemented using scikit-learn’s ",
            html.Code("HistGradientBoostingClassifier"),
            ". To understand why, it helps to understand the three layers: decision trees, "
            "histogram binning, and gradient boosting.",
        ]),

        html.H4("Layer 1 — Decision Trees (the building block)"),
        html.P([
            "A decision tree makes predictions by asking a sequence of yes/no questions about "
            "features. It learns ",
            html.Em("which feature to split on"),
            " and ",
            html.Em("where to split it"),
            " by finding the boundary that creates the most separated groups in terms of the outcome.",
        ]),
        html.P("For example, with a split on feature f1 at the value 11.0:"),
        html.Div(
            html.Img(
                src="/assets/decision_tree.png",
                alt="Decision tree: f1 < 11.0 splits users into 1% vs 8% conversion rate groups",
                className="decision-tree-img",
            ),
            className="decision-tree-container",
        ),
        html.P([
            "The split at ",
            html.Code("f1 < 11.0"),
            " is useful because it separates users into groups with meaningfully different "
            "conversion rates (1% vs 8%). The model evaluates all candidate splits and selects "
            "the one that creates the largest separation in outcomes — measured by a criterion "
            "such as Gini impurity or information gain. This process repeats recursively at each "
            "branch, building a tree of decisions.",
        ]),

        html.H4("Layer 2 — Histogram Binning (the speed trick)"),
        html.P([
            "The features here (f0–f11) are continuous numerical values. Evaluating every "
            "possible split point is computationally expensive at 14 million rows. ",
            html.Strong("Histogram binning"),
            " solves this: instead of checking every value, the model first buckets the data into "
            "a fixed number of ranges. For example, feature f1 might be divided into:",
        ]),
        html.Ul([
            html.Li("Bin A: 10.0 – 10.5"),
            html.Li("Bin B: 10.5 – 11.0"),
            html.Li("Bin C: 11.0 – 11.5"),
            html.Li("Bin D: 11.5 – 12.0"),
        ]),
        html.P([
            "The model only considers splits at these bin boundaries — dramatically reducing "
            "computation without meaningfully hurting accuracy. This is the “Hist” in ",
            html.Code("HistGradientBoostingClassifier"),
            ".",
        ]),

        html.H4("Layer 3 — Gradient Boosting (the ensemble)"),
        html.P([
            "A single decision tree is weak — it overfits easily and misses complex patterns. ",
            html.Strong("Gradient boosting"),
            " fixes this by training many trees sequentially, where each new tree corrects the "
            "residual errors of all previous ones.",
        ]),
        html.P([
            "The first tree makes rough predictions. The second focuses on cases the first got wrong. "
            "The third focuses on the remaining errors, and so on. The final prediction is the weighted "
            "sum of all trees’ contributions. By combining many shallow trees, the ensemble learns "
            "complex nonlinear patterns in user feature combinations that a single tree or logistic "
            "regression would miss.",
        ]),
        html.P([
            "This is why PCA on the 12 features showed no clean separation between converters and "
            "non-converters in 2D: conversion is a high-dimensional nonlinear signal, and gradient "
            "boosted trees are specifically designed to capture it.",
        ]),

        html.H4("Training Setup"),
        html.P([
            "Before training, the full dataset is split into training and test sets. The training "
            "data is then divided into treated (T=1) and control (T=0) subsets. Each model is trained "
            "independently on its respective subset using f0–f11 as features and conversion as "
            "the label. Trained models are serialized and saved to Google Cloud Storage (",
            html.Code("model_treated.pkl"),
            ", ",
            html.Code("model_control.pkl"),
            ") for reuse without retraining.",
        ]),
    ], className="methods-section"),

    # ── Ranking & Segmentation ────────────────────────────────────────────────
    html.Section([
        html.H3("Ranking and Segmentation"),

        html.H4("What You Have After Training"),
        html.P([
            "After the T-Learner runs on all test users, every user has one number attached to them "
            "— their uplift score τ̂(x):",
        ]),
        html.Pre(
            "User 1:  +0.18\n"
            "User 2:  +0.03\n"
            "User 3:  -0.05\n"
            "User 4:  +0.31\n"
            "User 5:  +0.09\n"
            "...\n"
            "~14M users",
            className="code-block"
        ),
        html.P([
            "That’s it — just a list of users with scores. The question is: ",
            html.Em("did the model actually learn something real, or is it outputting noise?"),
            " Ranking and segmentation is how you answer that.",
        ]),

        html.H4("Step 1 — Ranking"),
        html.P("Sort everyone from highest uplift to lowest:"),
        html.Pre(
            "Rank 1:   User 4   → +0.31\n"
            "Rank 2:   User 1   → +0.18\n"
            "Rank 3:   User 5   → +0.09\n"
            "Rank 4:   User 2   → +0.03\n"
            "Rank 5:   User 3   → -0.05\n"
            "...",
            className="code-block"
        ),
        html.P([
            "The model is saying: ",
            html.Em("“User 4 is the most persuadable; User 3 is someone the ad might actually hurt.”"),
            " But you don’t know yet if that ranking is meaningful — the model could be "
            "confidently wrong.",
        ]),

        html.H4("Step 2 — Grouping into Bins"),
        html.P([
            "Instead of analyzing 14M individual ranks, users are bucketed into equal-sized groups "
            "based on their rank. The number of bins is a choice — common options are "
            "deciles (10), quintiles (5), or percentiles (100). We use ",
            html.Strong("deciles"),
            " because they offer enough granularity to see a trend without individual bins becoming "
            "too noisy. Each decile contains ~1.4M users:",
        ]),
        html.Pre(
            "Decile 1  → top 10% of predicted uplift     (most persuadable)\n"
            "Decile 2  → next 10%\n"
            "Decile 3  → next 10%\n"
            "...\n"
            "Decile 10 → bottom 10%                      (least persuadable / sleeping dogs)",
            className="code-block"
        ),

        html.H4("Step 3 — The Reality Check"),
        html.P([
            "Here is the key move. Because this is a randomized experiment, inside every decile "
            "there are both treated users (saw the ad) and control users (did not), since assignment "
            "was random. That means within each decile you can compute the actual ",
            html.Strong("realized uplift"),
            ":",
        ]),
        html.Pre(
            "Realized uplift = conversion rate (treated) − conversion rate (control)",
            className="code-block formula"
        ),
        html.P("This is the ground truth for that group. Now compare:"),
        html.Ul([
            html.Li([html.Strong("Decile 1"), " (model predicted high uplift) → did they actually convert more when shown ads?"]),
            html.Li([html.Strong("Decile 10"), " (model predicted low uplift) → did they barely respond or respond negatively?"]),
        ]),
        html.P("If the model learned something real, you would expect a chart like this:"),
        html.Pre(
            "Realized\n"
            "uplift\n"
            "  ↑\n"
            "  |  █\n"
            "  |  █  █\n"
            "  |  █  █  █\n"
            "  |  █  █  █  █\n"
            "  |  █  █  █  █  █\n"
            "  |  █  █  █  █  █  █  █\n"
            "  |  █  █  █  █  █  █  █  █  █\n"
            "  |  █  █  █  █  █  █  █  █  █  █\n"
            "  +--1--2--3--4--5--6--7--8--9-10→ Decile",
            className="code-block"
        ),
        html.P([
            "High realized uplift in Decile 1, declining as you go right — the model’s "
            "ranking matches reality. If the bars were all roughly equal height, the model learned "
            "nothing useful. If they were randomly ordered, same conclusion.",
        ]),
    ], className="methods-section"),

    # ── Model Evaluation ──────────────────────────────────────────────────────
    html.Section([
        html.H3("Model Evaluation"),
        html.P("The effectiveness of the T-Learner is evaluated using four complementary methods:"),
        html.Ul([
            html.Li([
                html.Strong("ROC AUC (per model)"),
                " — measures how well each individual model (treated and control) predicts "
                "conversion within its own group. This is a sanity check: each model should be at "
                "least a reasonable classifier before we subtract their outputs. It is not a direct "
                "uplift metric.",
            ]),
            html.Li([
                html.Strong("Uplift-by-Bin Plot"),
                " — splits test users into equal-sized bins by predicted uplift rank and plots "
                "the realized average uplift per bin. The number of bins is configurable; we use 10 "
                "(deciles) as a standard choice. A good model produces a monotonically decreasing "
                "curve — the top bin has the highest actual incremental conversion rate.",
            ]),
            html.Li([
                html.Strong("Qini Curve"),
                " — the primary evaluation metric. It plots cumulative incremental conversions "
                "(conversions attributable to the ad, above the control baseline) as a function of "
                "the percentage of users targeted, ranked by descending τ̂(x). A perfect "
                "model concentrates all persuadable users at the top of the ranking, producing a "
                "steep early curve. A random targeting policy produces a straight diagonal line. The ",
                html.Strong("AUUC (Area Under the Uplift Curve)"),
                " — the area between the model curve and the random baseline — is a scalar "
                "summary of model quality, analogous to AUC-ROC for classifiers.",
            ]),
            html.Li([
                html.Strong("Policy Table"),
                " — summarizes estimated incremental conversions at select targeting thresholds: "
                "5%, 10%, 20%, 30%, 50%, and 100% of users. This translates the model’s ranking "
                "into actionable budget decisions: for a given number of ad impressions, how many "
                "incremental conversions do we expect versus a treat-all baseline?",
            ]),
        ]),
    ], className="methods-section"),

    # ── Full Pipeline ─────────────────────────────────────────────────────────
    html.Section([
        html.H3("The Full Pipeline"),
        html.P("Here is the complete analysis pipeline from data to targeting policy:"),
        html.Ol([
            html.Li([
                html.Strong("Exploratory Data Analysis (EDA)"), " — "
                "Summary statistics, class balance assessment, Pearson correlation matrix across "
                "treatment/visit/conversion/exposure, and PCA on a 30,000-row sample to project "
                "f0–f11 into 2D. PCA showed no clean cluster separation, confirming that "
                "conversion requires nonlinear modeling.",
            ]),
            html.Li([
                html.Strong("Funnel Analysis"), " — "
                "Computed ATE = E[Y | T=1] − E[Y | T=0] at two funnel "
                "stages (site visits and conversions). Also computed conditional conversion rate "
                "E[conversion | visit=1, T] to isolate post-click purchasing behavior "
                "from top-of-funnel engagement effects.",
            ]),
            html.Li([
                html.Strong("T-Learner Training"), " — Trained μ̂",
                html.Sub("1"), "(x) on treated users and μ̂",
                html.Sub("0"), "(x) on control users using ",
                html.Code("HistGradientBoostingClassifier"),
                ". Serialized both models to GCS.",
            ]),
            html.Li([
                html.Strong("Uplift Scoring"), " — "
                "Applied both models to the same test set. Computed τ̂(x) = μ̂",
                html.Sub("1"), "(x) − μ̂", html.Sub("0"),
                "(x) for each user. Ranked users by descending score.",
            ]),
            html.Li([
                html.Strong("Policy Evaluation"), " — "
                "Evaluated model quality via uplift-by-bin plot, Qini curve (AUUC), and policy "
                "table at select targeting thresholds.",
            ]),
            html.Li([
                html.Strong("Visualization & Deployment"), " — "
                "All results precomputed offline and serialized as CSV files to GCS. Interactive "
                "Plotly Dash dashboard containerized with Docker and deployed on Google App Engine. "
                "The app loads lightweight precomputed files via a cached loader — no runtime "
                "model inference.",
            ]),
        ], className="steps"),
        html.Div([
            "Full EDA and modeling code is available in ", html.Code("EDA.ipynb"),
            " in the project repository. Analysis was conducted in Google Colab using "
            "pandas, scikit-learn, matplotlib, and seaborn.",
        ], className="callout"),
    ], className="methods-section"),

])
