import dash
from dash import html

dash.register_page(__name__, name="Methods", path="/methods")

layout = html.Main([
    html.Section([
        html.H2("Methods: T-Learner with Histogram Gradient Boosting"),

        html.Div([
            html.H3("Overview"),
            html.P([
                "The goal of this analysis is to estimate the ",
                html.Strong("incremental effect of advertising on user behavior"),
                ". Instead of only predicting whether a user will convert, the model asks:"
            ]),
            html.Div(
                "How much does showing an ad change a user's probability of conversion?",
                className="quote-box"
            ),
            html.P([
                "To answer this, we use a ",
                html.Strong("T-learner framework"),
                " combined with ",
                html.Code("HistGradientBoostingClassifier"),
                " to estimate user-level uplift."
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("T-Learner Framework"),
            html.P("The T-learner trains two separate models:"),

            html.Div([
                html.Div([
                    html.H4("Treated Model"),
                    html.P("Trained only on users who were shown the ad."),
                    html.P("Learns conversion patterns under ad exposure.")
                ], className="mini-card"),

                html.Div([
                    html.H4("Control Model"),
                    html.P("Trained only on users who were not shown the ad."),
                    html.P("Learns conversion patterns without ad exposure.")
                ], className="mini-card"),
            ], className="two-column"),

            html.P([
                "Both models use the same feature set ",
                html.Code("f0–f11"),
                ", but they learn from different subsets of users."
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("Model Training"),
            html.P([
                "Each model is implemented using ",
                html.Code("HistGradientBoostingClassifier"),
                ", a tree-based algorithm that learns patterns by splitting users into groups based on feature values."
            ]),
            html.Ul([
                html.Li("The dataset is first split into training and test sets."),
                html.Li("The training data is then divided into treated and control subsets."),
                html.Li("Each model is trained independently using the same input features."),
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("Feature Binning and Split Selection"),
            html.P([
                "Because the features are continuous numerical values, the model first groups feature values into bins. "
                "For example, feature ",
                html.Code("f1"),
                " may be grouped into ranges such as:"
            ]),

            html.Div([
                html.Div("Bin A: 10.0 – 10.5", className="bin-pill"),
                html.Div("Bin B: 10.5 – 11.0", className="bin-pill"),
                html.Div("Bin C: 11.0 – 11.5", className="bin-pill"),
                html.Div("Bin D: 11.5 – 12.0", className="bin-pill"),
            ], className="bin-grid"),

            html.P([
                "Instead of testing every possible value, the model tests split points at these bin boundaries. "
                "It keeps the split that best separates users with different conversion behavior."
            ]),

            html.H4("Example Split"),

            html.Pre("""
                         Users
                           |
                      f1 < 11.0?
                     /          \\
                  Yes            No
              1% convert     8% convert
          Low conversion   High conversion
            """, className="tree-diagram"),

            html.P([
                "In this example, the split at ",
                html.Code("f1 < 11.0"),
                " is useful because it separates users into groups with very different conversion rates. "
                "The model repeats this process across many features and tree levels to learn complex behavior patterns."
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("Uplift Estimation"),
            html.P("After both models are trained, they are applied to the same test users."),
            html.P("For each user, the model estimates two probabilities:"),

            html.Ul([
                html.Li([html.Code("P(conversion | ad)"), " from the treated model"]),
                html.Li([html.Code("P(conversion | no ad)"), " from the control model"]),
            ]),

            html.Div(
                "uplift = P(conversion | ad) - P(conversion | no ad)",
                className="formula-box"
            ),

            html.P("The uplift score represents the estimated incremental impact of advertising for that user."),

            html.Div([
                html.Div([
                    html.Strong("Positive uplift"),
                    html.P("The ad increases conversion probability.")
                ], className="mini-card"),

                html.Div([
                    html.Strong("Near-zero uplift"),
                    html.P("The ad has little effect.")
                ], className="mini-card"),

                html.Div([
                    html.Strong("Negative uplift"),
                    html.P("The ad may reduce conversion probability.")
                ], className="mini-card"),
            ], className="three-column"),
        ], className="method-card"),

        html.Div([
            html.H3("Why This Works"),
            html.P([
                "In reality, we cannot observe both outcomes for the same user. "
                "A user either sees the ad or does not. The missing outcome is called the ",
                html.Strong("counterfactual"),
                "."
            ]),
            html.P([
                "Because the dataset comes from a randomized experiment, treated and control users are statistically comparable. "
                "The T-learner uses patterns from similar users in each group to approximate what would have happened under the opposite condition."
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("Ranking and Segmentation"),
            html.P([
                "After uplift scores are computed, users are sorted from highest to lowest predicted uplift. "
                "They are then grouped into bins, such as top 20%, next 20%, and so on. "
                "This allows us to test whether users predicted to have high uplift actually show higher realized uplift."
            ]),
        ], className="method-card"),

        html.Div([
            html.H3("Model Evaluation"),
            html.P("We evaluate the model using several metrics and plots:"),

            html.Div([
                html.Div([
                    html.Strong("ROC AUC"),
                    html.P("Checks whether treated and control models can predict conversion within their own groups.")
                ], className="mini-card"),

                html.Div([
                    html.Strong("Uplift-by-bin plot"),
                    html.P("Checks whether higher-ranked users show higher realized uplift.")
                ], className="mini-card"),

                html.Div([
                    html.Strong("Qini curve"),
                    html.P("Measures cumulative incremental conversions when targeting users by predicted uplift.")
                ], className="mini-card"),

                html.Div([
                    html.Strong("Policy table"),
                    html.P("Compares targeting strategies such as top-k targeting, treat-all, and treat-none.")
                ], className="mini-card"),
            ], className="two-column"),
        ], className="method-card"),

        html.Div([
            html.Strong("Key Insight: "),
            "This method moves beyond asking who is likely to convert. Instead, it asks who is likely to convert because of the ad."
        ], className="callout"),

        html.Div([
            html.H3("Summary"),
            html.P([
                "The T-learner combined with histogram gradient boosting estimates heterogeneous treatment effects by learning patterns "
                "from treated and control groups separately. Feature binning enables efficient split selection, while uplift scoring quantifies "
                "the causal impact of advertising. This method supports data-driven targeting decisions by identifying users most likely to be influenced by ads."
            ]),
        ], className="method-card"),
    ], id="methods", className="methods-page")
])