# Airbnb NYC Market Analysis: Comprehensive Findings & Strategic Insights

**Analysis Date:** 2025  
**Dataset:** Airbnb NYC Listings (Cleaned)  
**Scope:** Exploratory Data Analysis (EDA) for Market Intelligence  
> 📂 **Detailed Charts & Analysis:** See [`EDA_Process & Result/Airbnb_EDA.ipynb`](EDA_Process%20&%20Result/Airbnb_EDA.ipynb)

---

## TL;DR: Top 3 Business Impacts & Strategic Action

> **TODO:** Finalize after full document review — populate with the 3 most impactful findings and a clear call-to-action.

---

## Executive Summary

This comprehensive analysis of **17,230** Airbnb listings across New York City provides data-driven insights into pricing patterns, market concentration, and rental dynamics.

> **Analytical scope:** This dataset contains only listings with at least one guest review. New, unreviewed listings were excluded during ETL cleaning. All conclusions about ratings and pricing apply to the **reviewed-listing population** (survivor-bias consideration documented in the ETL pipeline).

**Key Findings:**
- Manhattan commands a ~17% price premium with 54.6% market share
- Entire homes generate a **124.9%** price premium over private rooms
- Ratings cluster tightly in the 91–93 range across all boroughs, offering virtually no pricing differentiation — location and property configuration are the true pricing levers
- The market shows significant concentration: Manhattan and Brooklyn together control 92.5% of all listings

---

## 1. Data Quality & Methodology

### 1.1 Dataset Overview
- **Dimensions:** 17,230 rows × 11 columns
- **Data Quality:** 100% complete (0 missing values, 0 duplicates)
- **Source:** Cleaned Airbnb listings dataset post-ETL processing
- **Population note:** Analysis covers reviewed listings only; 8,323 new unreviewed listings were excluded (see ETL pipeline)

### 1.2 Analysis Framework

**Statistical Methods Applied:**
- **Descriptive Statistics:** Mean, median, standard deviation, range, quartiles
- **Distribution Analysis:** Histogram plots, box plots, outlier detection
- **Market Concentration Analysis:** Market share calculations, concentration ratios
- **Price Premium Analysis:** Comparative pricing vs. market benchmarks
- **Categorical Analysis:** Value counts, percentage distributions, cross-tabulations

**Key Variables Analyzed:**
- **Numerical:** Price, Review Scores Rating, Number of Reviews, Beds
- **Categorical:** Neighbourhood, Zipcode, Property Type, Room Type
- **Derived Metrics:** Market share, price premiums

---

## 2. Univariate Analysis Results

### 2.1 Numerical Variables: Statistical Summary

| Variable               | Mean  | Median  | Std Dev | Min   | Max    | Range  | Insights 
|------------------------|-------|---------|---------|-------|--------|--------|-----------
| **Price ($)**          | 160.0 | 137.0   | 146.7   | 24    | 10,000 | 9,976  | Right-skewed; Top 1% outliers drag mean up
| **Review Score (/100)**| 92.6  | 94.0    | 8.6     | 20    | 100    | 80     | Survivor bias; 90+ is a hygiene factor
| **Number of Reviews**  | 15.0  | 6.0     | 22.6    | 1     | 256    | 255    | Long-tail; Winner-takes-most distribution
| **Beds**               | 1.5   | 1.0     | 1.0     | 1     | 16     | 15     | Single-bed properties dominate; Beds < 1 excluded by ETL validation

**Business Implications:**
- **Price Skewness (Luxury Impact):** The price distribution is highly right-skewed. While the median is $137, an exclusive luxury segment drives the mean up to $160 (the top 1% of properties are priced between $574 and $10,000).
- **Rating Survivor Bias:** A mean rating of 92.6 with extremely low variability (median 94.0) indicates that high ratings are a platform "hygiene factor." With over 76% of properties scoring ≥90, it strongly suggests a survivor bias where sub-par properties naturally exit the market.
- **Review Engagement (Winner-takes-most):** The median number of reviews is 6, indicating that over half the market (50.9%) has minimal booking history. However, the exact opposite occurs at the long tail (max 256), revealing a "winner-takes-most" dynamic where a small fraction of veteran hosts capture the vast majority of guest volume.
- **Market Saturation:** Single-bed properties dominate the inventory (66%), reflecting the fundamental structure of the NYC short-term rental market which relies heavily on spare rooms and small unit leasing rather than multi-bed operations.

### 2.2 Categorical Variables: Market Distribution

#### Neighbourhood Market Analysis

*Market avg price: $160. Premium = (Neighbourhood avg − Market avg) / Market avg × 100.*

| Neighbourhood    | Listings | Market Share | Avg Price | Price vs Market |
-------------------|----------|--------------|-----------|------------------|
| **Manhattan**    | 9,400    | 54.6%        | $187      | +16.9%           |
| **Brooklyn**     | 6,533    | 37.9%        | $133      | -16.9%           |
| **Queens**       | 1,107    | 6.4%         | $103      | -35.8%           |
| **Bronx**        | 136      | 0.8%         | $82       | -48.8%           |
| **Staten Island**| 55       | 0.3%         | $94       | -41.3%           |

#### Property Type Performance

*Market avg price: $160. Premium = (Type avg − Market avg) / Market avg × 100.*

| Property Type   | Listings | Market Share | Avg Price | Revenue Premium |
------------------|----------|--------------|-----------|-----------------|
| **Apartment**   | 15,822   | 91.8%        | $158      | -1.1%           |
| **House**       | 776      | 4.5%         | $164      | +2.6%           |
| **Loft**        | 419      | 2.4%         | $209      | +30.8%          |
| **Townhouse**   | 53       | 0.3%         | $267      | +66.9%          |
| **Condominium** | ~43      | 0.2%         | $229      | +43.3%          |


#### Room Type Economics

*Premium = (Room Type avg − Private Room avg) / Private Room avg × 100. Private Room avg: $88.*

| Room Type           | Listings | Market Share | Avg Price | Price Premium vs Private Room |
----------------------|----------|--------------|-----------|-------------------------------|
| **Entire home/apt** | 11,255   | 65.3%        | $198      | +**124.9%**                   |
| **Private room**    | 5,716    | 33.2%        | $88       | Baseline                      |
| **Shared room**     | 260      | 1.5%         | $77       | -12.5%                        |

---

## 3. Bivariate Analysis: Location Intelligence

### 3.1 Geographic Market Segmentation

**High Rating & Below-Average Price Areas:**

| Neighbourhood    | Avg Rating   | Avg Price | Price vs Market Avg   | Listings               |
|------------------|--------------|-----------|----------------------|------------------------|
| **Brooklyn**     | 92.9 / 100   | $133      | -16.9%                | 6,533                  |
| **Queens**       | 92.2 / 100   | $103      | -35.8%                | 1,107                  |
| **Staten Island**| 92.0 / 100   | $94       | -41.3%                | 55                     |
| **Bronx**        | 91.8 / 100   | $82       | -48.8%                | 135                    |


### 3.2 Zipcode Concentration Analysis

**Top 5 Zipcode Markets:**

| Zipcode   | Listings | Market Share | Avg Price | Primary Neighbourhood |
|-----------|----------|--------------|-----------|----------------------|
| **11211** | 1,000    | 5.8%         | $150      | Brooklyn (100%)       |
| **10009** | 714      | 4.1%         | $177      | Manhattan (100%)      |
| **10002** | 712      | 4.1%         | $174      | Manhattan (100%)      |
| **10003** | 665      | 3.8%         | $201      | Manhattan (100%)      |
| **11238** | 565      | 3.3%         | $134      | Brooklyn (100%)       |

**Geographic Insights:**
- Top 5 zipcodes represent 21.1% of all listings
- Perfect zipcode-neighbourhood alignment
- Manhattan zipcodes command 15-50% price premiums over Brooklyn equivalents

### 3.3 Price Volatility Analysis

**Most Volatile Markets (by Standard Deviation):**
| Neighbourhood  | Price Std Dev | Coefficient of Variation| Market Characteristics
|----------------|---------------|-------------------------|--------------------------------------
| **Manhattan**  | $178          | 96.4%                   | High volatility, diverse price range     
| **Brooklyn**   | $91           | 70.3%                   | Moderate volatility, consistent pricing 
| **Queens**     | $61           | 60.3%                   | Lower volatility, stable market         

---

## 4. Strategic Business Insights

### 4.1 Market Structure Analysis

**Concentration Metrics:**
- **Market Leadership:** Manhattan holds dominant 54.6% market share
- **Duopoly Pattern:** Manhattan + Brooklyn control 92.5% of total market
- **Property Type Dominance:** Apartments represent 91.8% of inventory
- **Room Type Preference:** 65.3% are entire homes, indicating strong privacy premium

**Competitive Dynamics:**
- **Entire Home Premium:** **124.9%** price advantage over private rooms ($198 vs. $88)
- **Property Type Premium:** Townhouses and condominiums show 43–67% price premiums despite low market volume
- **Geographic Price Disparity:** ~128% price differential between Manhattan ($187) and Bronx ($82) markets

### 4.2 Market Pattern Analysis

**Notable Market Segments:**
1. **Brooklyn Characteristics:** Above-market ratings (92.9) with 16.9% below-market pricing ($133 vs. $160 citywide avg)
2. **Luxury Property Premium:** Townhouses (+66.9%) and condominiums (+43.3%) command significant price premiums
3. **Outer Borough Dynamics:** Queens shows strong ratings (92.2) with significant price gap ($103, −35.8% vs. market)
4. **Room Configuration Impact:** Entire homes command **124.9%** premium over private rooms ($198 vs. $88)

**Market Concentration Observations:**
1. **Property Type Distribution:** Single-bed properties represent majority of inventory
2. **Apartment Dominance:** 91.2% market share across all property types
3. **Geographic Concentration:** Manhattan holds 54.8% of total market share

### 4.3 Operational Insights

**Key Pricing Determinants:**
- Location demonstrates stronger correlation with pricing than ratings
- Property type differentiation shows significant price variation patterns
- Room configuration (entire vs. private) represents primary pricing factor

**Market Patterns:**
- A "winner-takes-most" dynamic exists in reviews, with veteran hosts accumulating extreme interaction volumes compared to the median.
- Rating scores above 90 represent a platform "survival baseline" rather than a mark of premium differentiation.
- Price volatility varies significantly across geographic areas

---

## 5. Future Deep-Dive Analysis Recommendations

### 5.1 Geographic Visualization & Spatial Analysis

**Tableau Interactive Dashboards:**
- **Heat Map Visualizations:** Create neighborhood-level price and rating heat maps to identify spatial clusters
- **Geographic Distribution Analysis:** Interactive maps showing listing density, average prices, and rating distributions
- **Zipcode Boundary Analysis:** Overlay actual neighborhood boundaries with zipcode data for precise geographic insights
- **Transportation Accessibility:** Layer subway/transit data to analyze proximity impact on pricing

**Advanced Spatial Analytics:**
- **Spatial Autocorrelation:** Investigate whether nearby properties influence each other's pricing
- **Geographic Price Gradients:** Analyze how prices change with distance from Manhattan center
- **Neighborhood Boundary Effects:** Study price discontinuities at neighborhood borders

### 5.2 Temporal Trend Analysis

**Multi-Year Data Integration:**
- **Growth/Decline Trends:** Track listing count changes over 3-5 years by neighborhood
- **Price Evolution Analysis:** Identify neighborhoods with accelerating or declining price trends
- **Market Maturation Patterns:** Analyze how new neighborhoods enter and develop within the platform

**Seasonal Pattern Analysis:**
- **Booking Seasonality:** Integrate booking data to understand seasonal demand patterns
- **Price Elasticity by Season:** Analyze how pricing responds to seasonal demand changes

### 5.3 Advanced Analytical Techniques

**Machine Learning Applications:**
- **Price Prediction Models:** Develop ML models using property characteristics, location, and amenities
- **Market Segmentation:** Use clustering algorithms to identify distinct market segments
- **Recommendation Systems:** Build property recommendation engines based on guest preferences
- **Anomaly Detection:** Identify pricing outliers and unusual market patterns

**Text Analytics & Sentiment Analysis:**
- **Review Text Mining:** Extract insights from guest reviews about neighborhood preferences
- **Amenity Impact Analysis:** Quantify the value of specific amenities on pricing
- **Host Description Analysis:** Analyze how property descriptions correlate with performance

---

## 6. Limitations & Future Analysis

### 6.1 Current Analysis Limitations

**Temporal Scope:**
- Static analysis without seasonal/temporal patterns
- No booking frequency or occupancy rate data
- Missing causal relationship analysis

**Variable Scope:**
- Limited amenities and host characteristics data
- No guest demographic or behavior patterns

### 6.2 Recommended Future Research

**Advanced Analytics:**
1. **Predictive Modeling:** Revenue forecasting by property type and location
2. **Time Series Analysis:** Seasonal pricing patterns and booking cycles
3. **Machine Learning:** Guest preference clustering and recommendation engines
4. **Geographic Analysis:** Spatial autocorrelation and market heat mapping
5. **Sentiment Analysis:** Review text mining for quality indicators

**Business Intelligence Extensions:**
1. **Interactive Dashboards:** Real-time market monitoring and trend analysis
2. **Market Performance Analysis:** Multi-dimensional market performance tracking models
3. **Forecasting Models:** Supply/demand balance and price trend prediction systems

---

## Conclusion

This analysis of **17,230** reviewed Airbnb listings across New York City reveals a highly concentrated market with significant geographic and property-type pricing disparities. Manhattan's market dominance (54.6% share) and the substantial 124.9% price premium for entire homes indicate clear, data-supported market structure patterns. The near-zero correlation between ratings and prices (r ≈ 0.068) confirms that location and property configuration are primary pricing determinants rather than guest satisfaction scores.

From a consumer perspective, this distribution reveals a compelling **value disparity**: Brooklyn listings deliver guest ratings equal to or exceeding Manhattan (≥93.0/100) while pricing at a ~17% discount to the market average. Applied to platform strategy, this insight could power a 'high value-to-price' recommendation algorithm that precisely targets price-sensitive users with these high-quality, under-priced listings — effectively increasing platform booking conversion while helping guests maximize value.

> **Temporal caveat:** These findings are based on a static cross-sectional dataset. All recommendations should be validated with time-series data before production deployment, as market conditions (especially Brooklyn pricing trends) evolve over time.

The identified patterns provide a robust foundation for future analytical work, including temporal trend analysis, geographic heat-map visualization, and machine learning price-prediction models.

---

**Analysis Methodology:** Systematic EDA using Python (`pandas`, `matplotlib`, `seaborn`) with descriptive statistics, distribution analysis, and market concentration calculations.  
**Data Source:** Cleaned Airbnb NYC listings dataset (17,230 reviewed properties, 11 variables)  
**Analytical Scope:** Reviewed listings only — new unreviewed listings excluded during ETL (survivor-bias documented).  
**Statistical Confidence:** 100% complete post-ETL data (0 missing values) supports reliable within-scope insights. 