# The Sugar Trap — Market Gap Analysis

## A. Executive Summary

This project analyzes the first 500,000 rows of the Open Food Facts product export to explore nutritional positioning across six snack categories: biscuits, nuts, snack bars, chips, crackers, and confectionery. After category classification and removal of products without an identifiable product name, the sample contained 28,851 snack records, 8,042 products with usable names, sugar, and protein measurements formed the core nutritional analysis set. Using sample-derived thresholds of at least 8.33g protein and no more than 3.57g sugar per 100g, 580 products (7.21% of the core set) met the target profile. Confectionery had the lowest target-profile share (0.49%, 13 of 2,649 analyzed products), making it a preliminary nutritional-positioning hypothesis for further R&D validation, the result is constrained by uneven nutritional-data completeness and does not establish consumer demand.

## B. Project Links

- **Notebook on Google Colab** https://colab.research.google.com/drive/1yfwlYDoqf1j2Qytrn2D_iagrb5yDkWn8?usp=sharing
- **GitHub Repository:** https://github.com/b-o-m-pixel/sugar-trap-market-analysis
- **Dashboard:** https://sugar-trap-market-analysis-8jtvhbzqpiy6pjrtdvnf38.streamlit.app/
- **Presentation:** https://docs.google.com/presentation/d/1zX299cHMoYb0sKXM7hsFBIk8Gk-EYl_uMtZdghSIicw/edit?usp=sharing (presentation/sugar_trap_insight_presentation.pptx)

## C. Technical Explanation

### Data acquisition and scope

The analysis reads the first 500,000 records from the Open Food Facts tab-separated export using Pandas chunk processing (25,000 rows per chunk) and selects eight fields relevant to product identification, category classification, nutritional analysis, and ingredients. This is a convenience sample based on export order, not a random or globally representative sample of the Open Food Facts database.

### Data cleaning

- The source `categories_tags` field is parsed into individual tags. Explicit tag mappings assign products to six high-level categories. When a product matches more than one mapped category, the notebook applies the documented priority: Snack Bars, Biscuits, Crackers, Chips, Confectionery, then Nuts.
- The initial category extraction returned 29,152 records. The 301 records with missing product names were excluded, leaving 28,851 named snack records.
- No duplicate product codes were detected among the 29,152 initially classified records.
- Nutritional measurements below 0 or above 100g per 100g were treated as invalid and replaced with missing values, not zero. The initial validation identified 15 invalid nutrient cells across 13 products (8 sugar, 6 fat, 1 fiber, and 0 protein cells).
- Missing nutrient values were not imputed. The broad cleaned dataset preserves products with partial nutritional information. The core analysis dataset contains 8,042 products with a product name and usable sugar and protein values.
- Ingredient-source frequency analysis uses products with non-empty ingredient text, 459 of the 580 target-profile products had ingredient information available.

### Main analytical findings

The core dataset contains 8,042 products. Overall mean sugar was 26.31g/100g and mean protein was 7.42g/100g, the corresponding medians were 22.58g and 6.00g.

Median sugar and median protein by category:

| Category | Median sugar (g/100g) | Median protein (g/100g) | Core products analyzed |
|---|---:|---:|---:|
| Confectionery | 52.50 | 3.33 | 2,649 |
| Biscuits | 29.60 | 5.70 | 1,917 |
| Snack Bars | 25.00 | 8.33 | 485 |
| Nuts | 4.58 | 20.00 | 875 |
| Crackers | 3.33 | 8.85 | 498 |
| Chips | 2.50 | 6.00 | 1,618 |

Exploratory target-profile thresholds were derived from the core sample's quartiles: low sugar at or below 3.57g/100g (25th percentile) and high protein at or above 8.33g/100g (75th percentile). A total of 580 products (7.21%) met both conditions. Confectionery had the lowest target-profile share (0.49%, 13/2,649), while crackers had the highest share (34.74%, 173/498) and nuts had the highest qualifying-product count (221/875).

### Candidate's Choice: Category-Level Nutritional Gap Score

The additional metric is the share of analyzed products in each category that fall outside the selected high-protein/low-sugar target profile:

`Nutritional gap score = 100% - target-profile penetration (%)`

This provides a consistent descriptive comparison of nutritional positioning across categories. It is not a measure of commercial market size, unmet consumer demand, or product-market fit. The dashboard also displays the qualifying-product count and data-completeness context to avoid interpreting the percentage in isolation.

### Hidden Gem: Ingredient mentions

Among the 459 target-profile products with ingredient text, the most frequent keyword groups were soy-derived ingredients (120 products), peanuts (78), and whey (69). These counts are keyword-based product mentions, a product can mention multiple sources, and the counts do not measure ingredient quantity or protein contribution.
