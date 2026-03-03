"""
Airbnb Exploratory Data Analysis - Production Version
======================================================

This module provides a professional EDA pipeline for the Airbnb NYC dataset.

Features:
- Modular, class-based design
- Professional logging (file + console)
- Comprehensive statistical analysis (univariate, categorical, bivariate)
- Outlier-aware visualizations (95th-percentile capping for Price)
- Business insight generation with quantified price premiums
- Rating × Location analysis to support the 'value-disparity' thesis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eda_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AirbnbEDAAnalyzer:
    """
    Professional EDA analyzer for the cleaned Airbnb NYC dataset.

    Provides univariate, categorical, bivariate, and business-insight
    analyses with outlier-aware visualizations and a comprehensive report.
    """

    # Analytical column sets (constant variables excluded from correlation)
    NUMERICAL_COLS = ['Price', 'Review Scores Rating', 'Number Of Reviews', 'Beds']
    CATEGORICAL_COLS = ['Neighbourhood', 'Property Type', 'Room Type']

    def __init__(self, data_path: str):
        """
        Initialize EDA analyzer.

        Args:
            data_path: Path to the cleaned CSV file produced by ETL.py.
        """
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(__name__)

        # Visualization style — consistent across all charts
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("deep")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10

    # ------------------------------------------------------------------ #
    #  D A T A   L O A D I N G
    # ------------------------------------------------------------------ #

    def load_data(self) -> pd.DataFrame:
        """
        Load the cleaned Airbnb dataset.

        Returns:
            pd.DataFrame: The loaded dataset.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
        """
        try:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Data file not found: {self.data_path}")

            self.df = pd.read_csv(self.data_path)
            self.logger.info(
                f"Dataset loaded: {self.df.shape[0]:,} rows x {self.df.shape[1]} columns"
            )
            return self.df

        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            raise

    def _require_data(self):
        """Assert that data has been loaded before analysis."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

    def _get_existing_numerical_cols(self) -> List[str]:
        """
        Return the list of analytical numerical columns that exist in the DataFrame,
        excluding any constant-variance columns (e.g., 'Number of Records' = always 1).
        """
        return [
            col for col in self.NUMERICAL_COLS
            if col in self.df.columns and self.df[col].std() > 0
        ]

    def _get_existing_categorical_cols(self) -> List[str]:
        """Return categorical columns that exist in the DataFrame."""
        return [col for col in self.CATEGORICAL_COLS if col in self.df.columns]

    # ------------------------------------------------------------------ #
    #  A N A L Y S I S   M E T H O D S
    # ------------------------------------------------------------------ #

    def validate_data_quality(self) -> Dict[str, any]:
        """
        Generate a data quality report for the cleaned dataset.

        Returns:
            Dict: Quality metrics including missing values, duplicates, memory usage.
        """
        self._require_data()

        quality_metrics = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'missing_percentage': (
                self.df.isnull().sum().sum() /
                (len(self.df) * len(self.df.columns))
            ) * 100,
            'duplicate_rows': self.df.duplicated().sum(),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024 ** 2,
            'data_types': self.df.dtypes.to_dict()
        }

        self.logger.info("Data quality validation completed.")
        return quality_metrics

    def perform_univariate_analysis(self) -> Dict[str, any]:
        """
        Compute descriptive statistics for all analytical numerical variables.

        NOTE: 'Number of Records' is intentionally excluded from this analysis.
        After ETL cleaning, every listing has exactly 1 record (constant = 1,
        std = 0). A constant variable carries no information and would produce
        NaN values in any correlation or distribution analysis.

        Returns:
            Dict: Per-column statistics (count, mean, median, std, min, max,
                  quartiles, skewness, kurtosis).
        """
        self._require_data()

        existing_numerical_cols = self._get_existing_numerical_cols()
        univariate_results = {}

        for col in existing_numerical_cols:
            univariate_results[col] = {
                'count':    self.df[col].count(),
                'mean':     self.df[col].mean(),
                'median':   self.df[col].median(),
                'std':      self.df[col].std(),
                'min':      self.df[col].min(),
                'max':      self.df[col].max(),
                'q25':      self.df[col].quantile(0.25),
                'q75':      self.df[col].quantile(0.75),
                'skewness': self.df[col].skew(),
                'kurtosis': self.df[col].kurtosis()
            }

        self.logger.info("Univariate analysis completed.")
        return univariate_results

    def analyze_categorical_variables(self) -> Dict[str, any]:
        """
        Analyze the distribution of categorical variables.

        Returns:
            Dict: Per-column value counts, top categories, and percentage share.
        """
        self._require_data()

        existing_categorical_cols = self._get_existing_categorical_cols()
        categorical_results = {}

        for col in existing_categorical_cols:
            value_counts = self.df[col].value_counts()
            categorical_results[col] = {
                'unique_count':         self.df[col].nunique(),
                'top_categories':       value_counts.head(10).to_dict(),
                'category_percentages': (value_counts / len(self.df) * 100).to_dict()
            }

        self.logger.info("Categorical analysis completed.")
        return categorical_results

    def perform_bivariate_analysis(self) -> Dict[str, any]:
        """
        Perform bivariate analysis between Price, Rating, and categorical dimensions.

        Analyses included:
        - Price × Neighbourhood (geographic pricing intelligence)
        - Price × Room Type (room configuration economics)
        - Price × Property Type (property tier premiums)
        - Rating × Neighbourhood (critical for the 'value disparity' thesis:
          high-rating areas that are still underpriced vs. market average)
        - Correlation matrix of all analytical numerical variables
          (Number of Records excluded — it is a constant post-ETL)

        Returns:
            Dict: Bivariate statistics per analysis dimension.
        """
        self._require_data()

        bivariate_results = {}

        # Price × Neighbourhood
        if 'Price' in self.df.columns and 'Neighbourhood' in self.df.columns:
            bivariate_results['neighborhood_price'] = (
                self.df.groupby('Neighbourhood')['Price']
                .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                .round(2)
                .to_dict()
            )

        # Price × Room Type
        if 'Price' in self.df.columns and 'Room Type' in self.df.columns:
            bivariate_results['room_type_price'] = (
                self.df.groupby('Room Type')['Price']
                .agg(['count', 'mean', 'median', 'std'])
                .round(2)
                .to_dict()
            )

        # Price × Property Type
        if 'Price' in self.df.columns and 'Property Type' in self.df.columns:
            bivariate_results['property_type_price'] = (
                self.df.groupby('Property Type')['Price']
                .agg(['count', 'mean', 'median', 'std'])
                .round(2)
                .to_dict()
            )

        # Rating × Neighbourhood — the analytic foundation for the 'value-disparity' insight
        # (high-rating boroughs with below-market pricing reveal arbitrage opportunities)
        if 'Review Scores Rating' in self.df.columns and 'Neighbourhood' in self.df.columns:
            rating_by_neighbourhood = (
                self.df.groupby('Neighbourhood')['Review Scores Rating']
                .agg(['count', 'mean', 'median', 'std'])
                .round(2)
            )
            bivariate_results['neighbourhood_rating'] = rating_by_neighbourhood.to_dict()
            self.logger.info(
                "Rating × Neighbourhood analysis completed "
                "(supports value-disparity thesis)."
            )

        # Correlation matrix — analytical columns only (constant columns excluded)
        existing_numerical_cols = self._get_existing_numerical_cols()
        if len(existing_numerical_cols) > 1:
            correlation_matrix = self.df[existing_numerical_cols].corr()
            bivariate_results['correlation_matrix'] = correlation_matrix.to_dict()

        self.logger.info("Bivariate analysis completed.")
        return bivariate_results

    def generate_business_insights(self) -> Dict[str, any]:
        """
        Compute quantified business insights from the dataset.

        Insights generated:
        - Market concentration (top-5 neighbourhood share)
        - Price premiums by neighbourhood vs. overall average
        - Room type economics (price premium relative to Private Room baseline)
        - Price × Rating correlation (tests the 'hygiene factor' hypothesis)
        - Value-disparity matrix (high-rating neighbourhoods below market price)

        Returns:
            Dict: Quantified insights ready for reporting.
        """
        self._require_data()

        insights = {}

        # Market concentration
        if 'Neighbourhood' in self.df.columns:
            neighbourhood_counts = self.df['Neighbourhood'].value_counts()
            top_5 = neighbourhood_counts.head(5)
            insights['market_concentration'] = {
                'top_5_neighbourhoods': top_5.to_dict(),
                'concentration_percentage': round(
                    (top_5.sum() / len(self.df)) * 100, 2
                )
            }

        # Price premiums by neighbourhood
        if 'Price' in self.df.columns and 'Neighbourhood' in self.df.columns:
            overall_avg = self.df['Price'].mean()
            nb_avg = self.df.groupby('Neighbourhood')['Price'].mean()
            premiums = ((nb_avg - overall_avg) / overall_avg * 100).round(2)

            insights['price_premiums'] = {
                'overall_average_price': round(overall_avg, 2),
                'neighbourhood_premiums': premiums.to_dict()
            }

        # Room type economics
        if 'Price' in self.df.columns and 'Room Type' in self.df.columns:
            rt_avg = self.df.groupby('Room Type')['Price'].mean()
            if 'Private room' in rt_avg.index:
                private_room_price = rt_avg['Private room']
                rt_premiums = (
                    (rt_avg - private_room_price) / private_room_price * 100
                ).round(2)
                insights['room_type_economics'] = {
                    'private_room_baseline': round(private_room_price, 2),
                    'room_type_premiums': rt_premiums.to_dict()
                }

        # Price × Rating correlation — tests the 'hygiene factor' thesis
        if 'Price' in self.df.columns and 'Review Scores Rating' in self.df.columns:
            corr = self.df['Price'].corr(self.df['Review Scores Rating'])
            insights['price_rating_correlation'] = round(corr, 4)

        # Value-disparity matrix: high-rating areas with below-market pricing
        if all(c in self.df.columns for c in ['Neighbourhood', 'Price', 'Review Scores Rating']):
            overall_avg_price = self.df['Price'].mean()
            overall_avg_rating = self.df['Review Scores Rating'].mean()

            nb_stats = self.df.groupby('Neighbourhood').agg(
                avg_price=('Price', 'mean'),
                avg_rating=('Review Scores Rating', 'mean'),
                listing_count=('Price', 'count')
            ).round(2)

            # High value = above-average rating AND below-average price
            value_disparity = nb_stats[
                (nb_stats['avg_rating'] >= overall_avg_rating) &
                (nb_stats['avg_price'] < overall_avg_price)
            ].copy()
            value_disparity['price_discount_pct'] = (
                (value_disparity['avg_price'] - overall_avg_price) / overall_avg_price * 100
            ).round(2)

            insights['value_disparity_matrix'] = value_disparity.to_dict()
            self.logger.info(
                f"Value-disparity matrix: {len(value_disparity)} neighbourhood(s) "
                f"with above-average ratings and below-average prices."
            )

        self.logger.info("Business insights generated.")
        return insights

    # ------------------------------------------------------------------ #
    #  V I S U A L I Z A T I O N S
    # ------------------------------------------------------------------ #

    def create_visualizations(self, save_plots: bool = True) -> None:
        """
        Generate a full suite of analytical charts.

        Charts produced:
        1. Numerical variable distributions (histogram + box plot, Price capped at P95)
        2. Categorical variable distributions (bar charts)
        3. Price analysis (by neighbourhood, room type, price vs. rating scatter,
           price distribution with P95 cap annotation)
        4. Correlation heatmap (analytical columns only; Number of Records excluded)

        Args:
            save_plots: If True, save all charts to the 'plots/' directory at 300 DPI.
        """
        self._require_data()

        if save_plots:
            plot_dir = Path("plots")
            plot_dir.mkdir(exist_ok=True)

        self._plot_numerical_distributions(save_plots)
        self._plot_categorical_distributions(save_plots)
        self._plot_price_analysis(save_plots)
        self._plot_correlation_heatmap(save_plots)

        self.logger.info("All visualizations created successfully.")

    def _plot_numerical_distributions(self, save_plots: bool) -> None:
        """
        Plot histogram and box plot for each analytical numerical variable.

        OUTLIER HANDLING: Price is right-skewed (skewness ≈ 23.8, kurtosis ≈ 1303).
        The top 0.15% of listings (25 properties) are priced above $1,000, dragging
        the X-axis to $10,000. To make the distribution readable, histograms are
        capped at the 95th percentile ($340) with a visual annotation.
        The full un-capped data is used for all statistics.
        """
        existing_numerical_cols = self._get_existing_numerical_cols()
        n_cols = len(existing_numerical_cols)

        fig, axes = plt.subplots(2, n_cols, figsize=(5 * n_cols, 10))
        fig.suptitle('Numerical Variable Distributions', fontsize=16, fontweight='bold')

        for i, col in enumerate(existing_numerical_cols):
            plot_data = self.df[col].dropna()

            # Apply percentile cap to Price only — for readability
            if col == 'Price':
                p95 = plot_data.quantile(0.95)
                display_data = plot_data.clip(upper=p95)
                cap_note = f' (capped at P95: ${p95:.0f})'
            else:
                display_data = plot_data
                cap_note = ''

            # Histogram
            axes[0, i].hist(display_data, bins=30, alpha=0.7,
                            color='steelblue', edgecolor='white')
            axes[0, i].set_title(f'{col} Distribution{cap_note}', fontsize=12)
            axes[0, i].set_xlabel(col)
            axes[0, i].set_ylabel('Frequency')

            # Box plot (uses full, un-capped data to correctly show outlier extent)
            axes[1, i].boxplot(plot_data, showfliers=True)
            axes[1, i].set_title(f'{col} Box Plot (full range)', fontsize=12)
            axes[1, i].set_ylabel(col)

        plt.tight_layout()
        if save_plots:
            plt.savefig('plots/numerical_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()

    def _plot_categorical_distributions(self, save_plots: bool) -> None:
        """Plot bar charts for each categorical variable (top 10 categories)."""
        existing_categorical_cols = self._get_existing_categorical_cols()
        n_cols = len(existing_categorical_cols)

        fig, axes = plt.subplots(1, n_cols, figsize=(7 * n_cols, 6))
        fig.suptitle('Categorical Variable Distributions', fontsize=16, fontweight='bold')

        if n_cols == 1:
            axes = [axes]

        for i, col in enumerate(existing_categorical_cols):
            value_counts = self.df[col].value_counts().head(10)
            bars = axes[i].bar(range(len(value_counts)), value_counts.values,
                               color='coral', alpha=0.85)
            axes[i].set_title(f'{col} (Top {len(value_counts)})', fontsize=12)
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Count')
            axes[i].set_xticks(range(len(value_counts)))
            axes[i].set_xticklabels(value_counts.index, rotation=45, ha='right')

            # Annotate bars with count values
            for bar, count in zip(bars, value_counts.values):
                axes[i].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 20,
                    f'{count:,}', ha='center', va='bottom', fontsize=9
                )

        plt.tight_layout()
        if save_plots:
            plt.savefig('plots/categorical_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()

    def _plot_price_analysis(self, save_plots: bool) -> None:
        """
        Plot four-panel price analysis:
        [1] Average Price by Neighbourhood
        [2] Average Price by Room Type
        [3] Price vs. Review Rating scatter (random sample of 1,000)
        [4] Price distribution histogram (capped at P95 for visual clarity)
        """
        if 'Price' not in self.df.columns:
            return

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Price Analysis by Multiple Dimensions',
                     fontsize=16, fontweight='bold')

        # Panel 1: Average Price by Neighbourhood
        if 'Neighbourhood' in self.df.columns:
            nb_prices = (
                self.df.groupby('Neighbourhood')['Price'].mean()
                .sort_values(ascending=False)
            )
            overall_avg = self.df['Price'].mean()
            bars = axes[0, 0].bar(nb_prices.index, nb_prices.values,
                                  color='steelblue', alpha=0.85)
            axes[0, 0].axhline(overall_avg, color='red', linestyle='--',
                               linewidth=1.5, label=f'Market avg: ${overall_avg:.0f}')
            axes[0, 0].set_title('Average Price by Neighbourhood')
            axes[0, 0].set_ylabel('Average Price ($)')
            axes[0, 0].set_xlabel('Neighbourhood')
            axes[0, 0].legend()
            for bar in bars:
                axes[0, 0].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 2,
                    f'${bar.get_height():.0f}',
                    ha='center', va='bottom', fontsize=10
                )

        # Panel 2: Average Price by Room Type
        if 'Room Type' in self.df.columns:
            rt_prices = (
                self.df.groupby('Room Type')['Price'].mean()
                .sort_values(ascending=False)
            )
            bars = axes[0, 1].bar(rt_prices.index, rt_prices.values,
                                  color='mediumseagreen', alpha=0.85)
            axes[0, 1].set_title('Average Price by Room Type')
            axes[0, 1].set_ylabel('Average Price ($)')
            axes[0, 1].set_xlabel('Room Type')
            for bar in bars:
                axes[0, 1].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 2,
                    f'${bar.get_height():.0f}',
                    ha='center', va='bottom', fontsize=10
                )

        # Panel 3: Price vs. Rating scatter (sampled, Price capped for readability)
        if 'Review Scores Rating' in self.df.columns:
            p99 = self.df['Price'].quantile(0.99)
            sample = self.df[self.df['Price'] <= p99].sample(
                n=min(1000, len(self.df)), random_state=42
            )
            axes[1, 0].scatter(
                sample['Review Scores Rating'], sample['Price'],
                alpha=0.4, color='darkorange', s=20
            )
            axes[1, 0].set_title(
                f'Price vs. Review Rating (n=1,000 sample, Price ≤ ${p99:.0f})'
            )
            axes[1, 0].set_xlabel('Review Scores Rating (/100)')
            axes[1, 0].set_ylabel('Price ($)')

            # Add correlation annotation
            corr = sample['Review Scores Rating'].corr(sample['Price'])
            axes[1, 0].text(
                0.05, 0.92, f'r = {corr:.3f}',
                transform=axes[1, 0].transAxes,
                fontsize=12, color='navy',
                bbox=dict(facecolor='lightyellow', alpha=0.8)
            )

        # Panel 4: Price distribution (capped at P95 for readability)
        p95 = self.df['Price'].quantile(0.95)
        display_prices = self.df['Price'].clip(upper=p95)
        axes[1, 1].hist(display_prices, bins=50, alpha=0.75,
                        color='mediumpurple', edgecolor='white')
        axes[1, 1].set_title(
            f'Price Distribution (capped at P95: ${p95:.0f})\n'
            f'Note: {(self.df["Price"] > p95).sum()} listings above ${p95:.0f} not shown'
        )
        axes[1, 1].set_xlabel('Price ($)')
        axes[1, 1].set_ylabel('Frequency')

        plt.tight_layout()
        if save_plots:
            plt.savefig('plots/price_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

    def _plot_correlation_heatmap(self, save_plots: bool) -> None:
        """
        Plot a correlation heatmap for analytical numerical variables.

        DESIGN NOTE: 'Number of Records' is excluded because it has zero variance
        (all values = 1 after ETL cleaning), which produces NaN in every correlation
        cell. Only variables with std > 0 are included.
        """
        existing_numerical_cols = self._get_existing_numerical_cols()

        if len(existing_numerical_cols) < 2:
            self.logger.warning("Not enough variable columns for correlation heatmap.")
            return

        correlation_matrix = self.df[existing_numerical_cols].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix,
            annot=True,
            fmt='.3f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8}
        )
        plt.title(
            'Correlation Matrix — Analytical Variables\n'
            '(Number of Records excluded: constant = 1 post-ETL)',
            fontsize=14, fontweight='bold'
        )
        plt.tight_layout()

        if save_plots:
            plt.savefig('plots/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()

    # ------------------------------------------------------------------ #
    #  R E P O R T
    # ------------------------------------------------------------------ #

    def generate_comprehensive_report(self) -> Dict[str, any]:
        """
        Compile all analysis results into a single structured report dict.

        Returns:
            Dict: Complete analysis report with all dimensions.
        """
        self._require_data()

        report = {
            'data_quality':       self.validate_data_quality(),
            'univariate_analysis': self.perform_univariate_analysis(),
            'categorical_analysis': self.analyze_categorical_variables(),
            'bivariate_analysis':  self.perform_bivariate_analysis(),
            'business_insights':   self.generate_business_insights()
        }

        self.logger.info("Comprehensive report generated.")
        return report

    def run_complete_analysis(self, save_plots: bool = True) -> Dict[str, any]:
        """
        Execute the full EDA pipeline: load → analyse → visualize.

        Args:
            save_plots: Whether to save charts to disk.

        Returns:
            Dict: Complete analysis report.
        """
        try:
            self.logger.info("Starting complete EDA analysis.")

            self.load_data()
            report = self.generate_comprehensive_report()
            self.create_visualizations(save_plots)

            self.logger.info("Complete EDA analysis finished successfully.")
            return report

        except Exception as e:
            self.logger.error(f"EDA analysis failed: {e}")
            raise


# ------------------------------------------------------------------ #
#  E N T R Y   P O I N T
# ------------------------------------------------------------------ #

def main():
    """
    Entry point for running the EDA pipeline as a standalone script.
    """
    try:
        analyzer = AirbnbEDAAnalyzer("Datasource/airbnb_clean.csv")
        report = analyzer.run_complete_analysis(save_plots=True)

        print("\n" + "=" * 65)
        print("AIRBNB EDA ANALYSIS SUMMARY")
        print("=" * 65)

        quality = report['data_quality']
        print(f"Dataset:          {quality['total_rows']:,} rows x {quality['total_columns']} columns")
        print(f"Missing values:   {quality['missing_values']} ({quality['missing_percentage']:.2f}%)")
        print(f"Memory usage:     {quality['memory_usage_mb']:.2f} MB")

        insights = report['business_insights']
        if 'price_premiums' in insights:
            print(f"\nMarket avg price: ${insights['price_premiums']['overall_average_price']:.2f}")

        if 'price_rating_correlation' in insights:
            print(f"Price-Rating r:   {insights['price_rating_correlation']:.4f}")

        if 'room_type_economics' in insights:
            premiums = insights['room_type_economics']['room_type_premiums']
            entire_pct = premiums.get('Entire home/apt', 0)
            print(f"Entire Home premium over Private Room: {entire_pct:.1f}%")

        if 'value_disparity_matrix' in insights:
            vd = insights['value_disparity_matrix']
            nb_list = list(vd.get('avg_price', {}).keys())
            print(f"Value-disparity neighbourhoods: {nb_list}")

        print("=" * 65)
        print("Analysis complete. Charts saved to 'plots/' directory.")

    except Exception as e:
        logger.error(f"Main analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
