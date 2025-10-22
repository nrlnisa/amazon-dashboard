import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# Load CSV
df = pd.read_csv("amazon.csv")

# Clean and convert numeric columns
df["discount_percentage"] = (
    df["discount_percentage"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .astype(float)
)

df["rating"] = (
    df["rating"]
    .astype(str)
    .str.extract(r"(\d+\.?\d*)")
    .astype(float)
)

# Convert prices to float
df["discounted_price"] = (
    df["discounted_price"]
    .astype(str)
    .str.replace("₹", "")
    .str.replace(",", "")
    .astype(float, errors="ignore")
)
df["actual_price"] = (
    df["actual_price"]
    .astype(str)
    .str.replace("₹", "")
    .str.replace(",", "")
    .astype(float, errors="ignore")
)

# Sample data for performance
df = df.sample(500)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Amazon Products Dashboard"

categories = df['category'].unique()

# Layout
app.layout = html.Div(
    style={
        "background": "linear-gradient(135deg, #E3FDFD, #FFE6FA)",
        "fontFamily": "Segoe UI, sans-serif",
        "minHeight": "100vh",
        "padding": "20px",
    },
    children=[
        html.H1(
            "📊 Amazon Products Dashboard",
            style={
                "textAlign": "center",
                "color": "#023e8a",
                "marginBottom": "20px",
                "textShadow": "1px 1px 2px #ccc",
            },
        ),

        html.Div(
            [
                html.Label("Select Category:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="category-dropdown",
                    options=[{"label": c, "value": c} for c in categories],
                    value=categories[0],
                    clearable=False,
                    style={
                        "borderRadius": "10px",
                        "padding": "5px",
                        "fontSize": "15px",
                    },
                ),
            ],
            style={
                "width": "300px",
                "margin": "0 auto",
                "textAlign": "center",
                "marginBottom": "30px",
            },
        ),

        html.Div(
            [
                html.Div(
                    dcc.Graph(id="top-rated-products"),
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "15px",
                        "padding": "20px",
                        "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
                        "width": "45%",
                        "minWidth": "350px",
                        "margin": "10px",
                    },
                ),
                html.Div(
                    dcc.Graph(id="discount-analysis"),
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "15px",
                        "padding": "20px",
                        "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
                        "width": "45%",
                        "minWidth": "350px",
                        "margin": "10px",
                    },
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "flexWrap": "wrap",
            },
        ),
    ],
)


@app.callback(
    Output("top-rated-products", "figure"),
    Output("discount-analysis", "figure"),
    Input("category-dropdown", "value"),
)
def update_charts(selected_category):
    filtered_df = df[df["category"] == selected_category].copy()
    filtered_df["rating"] = pd.to_numeric(filtered_df["rating"], errors="coerce")
    filtered_df["discount_percentage"] = pd.to_numeric(filtered_df["discount_percentage"], errors="coerce")
    filtered_df.dropna(subset=["rating", "discount_percentage"], inplace=True)

    # --- Top-rated products ---
    top_rated = (
        filtered_df.groupby("product_name", as_index=False)["rating"]
        .mean()
        .sort_values("rating", ascending=False)
        .head(10)
    )
    fig1 = px.bar(
        top_rated,
        y="product_name",
        x="rating",
        orientation="h",
        color="rating",
        color_continuous_scale="Tealgrn",
        title=f"⭐ Top 10 Rated Products in {selected_category}",
        text="rating",
    )
    fig1.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    # --- Discount analysis ---
    discount = (
        filtered_df.groupby("product_name", as_index=False)["discount_percentage"]
        .mean()
        .sort_values("discount_percentage", ascending=False)
        .head(10)
    )
    fig2 = px.bar(
        discount,
        y="product_name",
        x="discount_percentage",
        orientation="h",
        color="discount_percentage",
        color_continuous_scale="Mint",
        title=f"💸 Top 10 Discounted Products in {selected_category}",
        text="discount_percentage",
    )
    fig2.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig1, fig2


if __name__ == "__main__":
    app.run(debug=True)