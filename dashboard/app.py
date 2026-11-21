
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sugar Trap | Market Gap Analysis",
    page_icon="🍫",
    layout="wide"
)


# --------------------------------------------------
# 2. DATA LOADING
# --------------------------------------------------

DATA_DIR = Path("outputs")

CORE_DATA_PATH = DATA_DIR / "core_nutrient_analysis.csv"
ALL_DATA_PATH = DATA_DIR / "cleaned_snack_products.csv"


@st.cache_data
def load_data(core_path, all_path):

    core_df = pd.read_csv(core_path)

    all_df = pd.read_csv(
        all_path,
        usecols=["code", "primary_category"]
    )

    return core_df, all_df


try:
    df, all_products = load_data(
        str(CORE_DATA_PATH),
        str(ALL_DATA_PATH)
    )

except FileNotFoundError:
    st.error(
        "Dataset files not found. "
        "Check that both CSV files exist in the outputs folder."
    )
    st.stop()

REQUIRED_COLUMNS = [
    "product_name",
    "primary_category",
    "sugars_100g",
    "proteins_100g"
]

missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

df["sugars_100g"] = pd.to_numeric(
    df["sugars_100g"], errors="coerce"
)

df["proteins_100g"] = pd.to_numeric(
    df["proteins_100g"], errors="coerce"
)

df = df.dropna(subset=REQUIRED_COLUMNS).copy()


# --------------------------------------------------
# 3. NUTRITIONAL THRESHOLDS
# --------------------------------------------------

LOW_SUGAR_THRESHOLD = df["sugars_100g"].quantile(0.25)
HIGH_PROTEIN_THRESHOLD = df["proteins_100g"].quantile(0.75)

df["target_profile"] = (
    (df["sugars_100g"] <= LOW_SUGAR_THRESHOLD) &
    (df["proteins_100g"] >= HIGH_PROTEIN_THRESHOLD)
)


# --------------------------------------------------
# 4. CATEGORY-LEVEL ANALYSIS
# --------------------------------------------------

category_summary = (
    df.groupby("primary_category")
    .agg(
        complete_products=("product_name", "count"),
        qualifying_products=("target_profile", "sum"),
        median_sugar=("sugars_100g", "median"),
        median_protein=("proteins_100g", "median")
    )
)

all_category_counts = (
    all_products.groupby("primary_category")
    .size()
)

category_summary["total_products"] = (
    all_category_counts
)

category_summary["profile_penetration"] = (
    category_summary["qualifying_products"] /
    category_summary["complete_products"] * 100
)

category_summary["nutritional_gap"] = (
    100 - category_summary["profile_penetration"]
)

category_summary["data_completeness"] = (
    category_summary["complete_products"] /
    category_summary["total_products"] * 100
)

category_summary = category_summary.reset_index()


# --------------------------------------------------
# 5. SIDEBAR FILTER
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")

categories = sorted(df["primary_category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Select snack categories",
    options=categories,
    default=categories
)

st.sidebar.divider()

st.sidebar.caption(
    "Nutritional measurements are expressed per 100g."
)

st.sidebar.caption(
    "Only products with complete sugar and protein "
    "measurements are included in the nutrient matrix."
)


filtered_df = df[
    df["primary_category"].isin(selected_categories)
]


# --------------------------------------------------
# 6. DASHBOARD HEADER
# --------------------------------------------------

st.title("The Sugar Trap")
st.subheader("Healthy Snacking | Market Gap Analysis")

st.markdown(
    """
    Exploring nutritional positioning across six snack
    categories to identify potential opportunities for
    high-protein, low-sugar product development.
    """
)

st.divider()


# --------------------------------------------------
# 7. EXECUTIVE METRICS
# --------------------------------------------------

total_products = len(all_products)
analyzed_products = len(df)
qualifying_products = int(df["target_profile"].sum())

profile_percentage = (
    qualifying_products / analyzed_products * 100
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Classified Products",
    f"{total_products:,}"
)

col2.metric(
    "Products Analyzed",
    f"{analyzed_products:,}"
)

col3.metric(
    "High-Protein / Low-Sugar",
    f"{qualifying_products:,}"
)

col4.metric(
    "Target Profile Share",
    f"{profile_percentage:.2f}%"
)

st.divider()


# --------------------------------------------------
# 8. NUTRIENT MATRIX
# --------------------------------------------------

st.header("The Nutrient Matrix")

st.markdown(
    """
    Compare sugar and protein concentrations across
    snack categories. Use the sidebar to filter categories.
    """
)

if filtered_df.empty:

    st.warning("Select at least one category to display the chart.")

else:

    scatter_fig = px.scatter(
        filtered_df,
        x="sugars_100g",
        y="proteins_100g",
        color="primary_category",
        hover_name="product_name",
        hover_data={
            "sugars_100g": ":.2f",
            "proteins_100g": ":.2f",
            "primary_category": True
        },
        opacity=0.6,
        labels={
            "sugars_100g": "Sugar per 100g (g)",
            "proteins_100g": "Protein per 100g (g)",
            "primary_category": "Snack Category"
        },
        title="Sugar vs Protein by Snack Category"
    )

    scatter_fig.add_vline(
        x=LOW_SUGAR_THRESHOLD,
        line_dash="dash",
        line_color="gray",
        annotation_text="Low sugar threshold"
    )

    scatter_fig.add_hline(
        y=HIGH_PROTEIN_THRESHOLD,
        line_dash="dash",
        line_color="gray",
        annotation_text="High protein threshold"
    )

    scatter_fig.update_layout(
        height=620,
        legend_title_text="Category",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )

st.caption(
    f"Low sugar: ≤ {LOW_SUGAR_THRESHOLD:.2f}g | "
    f"High protein: ≥ {HIGH_PROTEIN_THRESHOLD:.2f}g"
)

st.divider()


# --------------------------------------------------
# 9. CATEGORY-LEVEL NUTRITIONAL GAP
# --------------------------------------------------

st.header("Category-Level Nutritional Gap")

st.markdown(
    """
    Measures the percentage of analyzed products in each
    category that do not meet our exploratory
    high-protein, low-sugar criteria.
    """
)

gap_fig = px.bar(
    category_summary.sort_values(
        "nutritional_gap",
        ascending=True
    ),
    x="nutritional_gap",
    y="primary_category",
    orientation="h",
    text=category_summary.sort_values(
        "nutritional_gap",
        ascending=True
    )["nutritional_gap"].apply(lambda x: f"{x:.2f}%"),
    hover_data=[
        "complete_products",
        "qualifying_products",
        "data_completeness"
    ],
    labels={
        "nutritional_gap": "Outside Target Profile (%)",
        "primary_category": "Snack Category",
        "complete_products": "Products Analyzed",
        "qualifying_products": "Products Meeting Target",
        "data_completeness": "Data Completeness (%)"
    },
    title="Share of Products Outside the Target Nutritional Profile"
)

gap_fig.update_layout(
    height=430,
    showlegend=False,
    xaxis_range=[0, 105]
)

st.plotly_chart(
    gap_fig,
    use_container_width=True
)


# --------------------------------------------------
# 10. KEY INSIGHT / RECOMMENDATION
# --------------------------------------------------

st.header("Key Insight & Recommendation")

largest_gap = category_summary.loc[
    category_summary["nutritional_gap"].idxmax()
]

st.info(
    f"""
    **Preliminary opportunity: {largest_gap['primary_category']}**

    Among products with complete nutritional information,
    only {int(largest_gap['qualifying_products']):,} out of
    {int(largest_gap['complete_products']):,} products
    ({largest_gap['profile_penetration']:.2f}%)
    meet our high-protein, low-sugar criteria.

    This suggests potential nutritional whitespace for
    differentiated product development.
    """
)

st.markdown(
    f"""
    **R&D target profile**

    - Protein: at least {HIGH_PROTEIN_THRESHOLD:.2f}g per 100g.
    - Sugar: no more than {LOW_SUGAR_THRESHOLD:.2f}g per 100g.
    - Investigate soy-derived ingredients, peanuts and whey
      as potential protein sources.
    """
)

st.warning(
    f"""
    **Data limitation:** Nutritional completeness for
    {largest_gap['primary_category']} is
    {largest_gap['data_completeness']:.2f}%.
    The observed nutritional gap is based only on products
    with available sugar and protein measurements.
    These data do not establish consumer demand.
    """
)

st.divider()


# --------------------------------------------------
# 11. DATA COMPLETENESS
# --------------------------------------------------

st.header("Data Quality & Coverage")

coverage_fig = px.bar(
    category_summary,
    x="primary_category",
    y="data_completeness",
    text=category_summary["data_completeness"].apply(
        lambda x: f"{x:.1f}%"
    ),
    labels={
        "primary_category": "Snack Category",
        "data_completeness": "Core Nutritional Completeness (%)"
    },
    title="Availability of Complete Sugar and Protein Data"
)

coverage_fig.update_layout(
    height=400,
    showlegend=False,
    yaxis_range=[0, 105]
)

st.plotly_chart(
    coverage_fig,
    use_container_width=True
)


# --------------------------------------------------
# 12. SAMPLE QUALIFYING PRODUCTS
# --------------------------------------------------

st.header("Example Products Meeting the Target Profile")

candidates = (
    df[df["target_profile"]]
    .sort_values(
        "proteins_100g",
        ascending=False
    )
)

st.caption(
    "Examples are products recorded in Open Food Facts, "
    "not independently validated product recommendations."
)

st.dataframe(
    candidates[
        [
            "product_name",
            "primary_category",
            "sugars_100g",
            "proteins_100g"
        ]
    ].head(15),
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 13. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    """
    Data source: Open Food Facts.
    Analysis uses a 500,000-row convenience sample from
    the source export. Results should not be interpreted
    as representative global market shares or measured
    consumer demand.
    """
)

st.caption(
    "Sugar Trap Market Gap Analysis | Helix CPG Partners"
)
