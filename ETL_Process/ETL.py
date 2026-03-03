"""
Airbnb Data ETL Pipeline - Production Version
==============================================

This module provides a professional ETL pipeline to process the Airbnb dataset.

Features:
- Modular, class-based design for reusability and testability
- Professional logging (file + console)
- Comprehensive error handling with specific exception types
- Data validation with explicit business rules
- Missing data pattern analysis before dropping
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Optional, Tuple
from pathlib import Path

# Configure logging
# Captures critical pipeline events to both a persistent log file and the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_process.log'),  # Persistent log file
        logging.StreamHandler()                   # Real-time console output
    ]
)
logger = logging.getLogger(__name__)


class AirbnbETLProcessor:
    """
    Professional ETL processor for the Airbnb NYC dataset.

    Encapsulates the full Extract-Transform-Load pipeline as discrete,
    independently testable methods. Each step logs its actions and
    row-count deltas so the data lineage is fully traceable.
    """

    def __init__(self, input_path: str, output_path: str):
        """
        Initialize ETL processor.

        Args:
            input_path: Path to the raw input Excel file.
            output_path: Path for the cleaned output CSV file.
        """
        self.input_path = Path(input_path)   # pathlib.Path for robust cross-platform handling
        self.output_path = Path(output_path)
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    #  E X T R A C T
    # ------------------------------------------------------------------ #

    def load_data(self) -> pd.DataFrame:
        """
        Load the Airbnb dataset from an Excel file.

        Returns:
            pd.DataFrame: The raw, unmodified dataset.

        Raises:
            FileNotFoundError: If the input file does not exist.
            Exception: For any other read-level errors.
        """
        try:
            if not self.input_path.exists():
                raise FileNotFoundError(f"Input file not found: {self.input_path}")

            df = pd.read_excel(self.input_path)
            self.logger.info(
                f"Dataset loaded successfully: {df.shape[0]:,} rows x {df.shape[1]} columns"
            )
            return df

        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            raise

    # ------------------------------------------------------------------ #
    #  T R A N S F O R M
    # ------------------------------------------------------------------ #

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Strip leading/trailing whitespace from all column names.

        The raw source has a trailing space in 'Neighbourhood ', which
        would silently break all downstream column-name lookups if not fixed.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with sanitized column names.
        """
        original_columns = df.columns.tolist()
        df.columns = [col.strip() for col in df.columns]

        changed_columns = [col for col in original_columns if col != col.strip()]
        if changed_columns:
            self.logger.info(f"Cleaned column names with whitespace: {changed_columns}")

        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records based on the (Host Id, Host Since) composite key.

        Business rationale: A host may legitimately own multiple listings,
        so Host Id alone is not sufficient. The combination of Host Id and
        Host Since uniquely identifies a host account registration event,
        and duplicate records on this key represent data entry redundancies
        rather than distinct listings.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with duplicates removed.
        """
        initial_count = len(df)
        df = df.drop_duplicates(subset=['Host Id', 'Host Since'])
        removed_count = initial_count - len(df)

        if removed_count > 0:
            self.logger.info(
                f"Removed {removed_count:,} duplicate records "
                f"(key: Host Id + Host Since). "
                f"Remaining: {len(df):,} rows."
            )
        return df

    def convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cast columns to their correct data types.

        - 'Host Since': parsed from DD/MM/YYYY string to a Python date object.
        - Numeric columns: use errors='coerce' so unparseable strings become NaN
          (which is then surfaced by the downstream missing-data analysis).

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with correct data types.
        """
        try:
            # Host Since: treat as date only (strip time component)
            df["Host Since"] = pd.to_datetime(
                df["Host Since"], format="%d/%m/%Y", errors="coerce"
            ).dt.date

            # Force-cast to numeric; non-parseable values become NaN
            numeric_columns = [
                'Price', 'Number of Records', 'Number Of Reviews', 'Review Scores Rating'
            ]
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            self.logger.info("Data types converted successfully.")
            return df

        except Exception as e:
            self.logger.error(f"Error converting data types: {e}")
            raise

    def drop_unnecessary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove columns that are redundant or carry no analytical value.

        'Review Scores Rating (bin)' is a pre-binned version of the continuous
        'Review Scores Rating' column. Retaining both would create collinearity
        and confusion in downstream analysis.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame without unnecessary columns.
        """
        columns_to_drop = ['Review Scores Rating (bin)', 'Name']
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]

        if existing_columns_to_drop:
            df = df.drop(columns=existing_columns_to_drop)
            self.logger.info(f"Dropped columns: {existing_columns_to_drop}")

        return df

    def impute_missing_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing Price values using a hierarchical geographic strategy.

        DESIGN NOTE: In the current dataset, Price has 0 missing values, so
        this method acts as a no-op. It is retained as a defensive component
        for future data refreshes or similar datasets where prices may be absent.

        Strategy (in priority order):
          1. Zipcode median  — most local geographic anchor
          2. Neighbourhood median — broader fallback if Zipcode lacks price data
          3. Drop             — row is too sparse to be financially evaluated

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with Price values imputed where possible.
        """
        initial_missing = df['Price'].isnull().sum()

        if initial_missing == 0:
            self.logger.info("No missing price data — imputation step skipped.")
            return df

        # Step 1: Impute using the median price within the same Zipcode
        df['Price'] = df['Price'].fillna(
            df.groupby('Zipcode')['Price'].transform('median')
        )

        # Step 2: Escalate to the broader Neighbourhood median for remaining gaps
        remaining_missing = df['Price'].isnull().sum()
        if remaining_missing > 0:
            df['Price'] = df['Price'].fillna(
                df.groupby('Neighbourhood')['Price'].transform('median')
            )

        # Step 3: Drop rows where both geographic anchors failed
        final_missing = df['Price'].isnull().sum()
        if final_missing > 0:
            df = df.dropna(subset=['Price'])
            self.logger.warning(
                f"Dropped {final_missing} rows where price imputation failed "
                f"(no Zipcode or Neighbourhood median available)."
            )

        imputed_count = initial_missing - final_missing
        self.logger.info(f"Successfully imputed {imputed_count} missing price values.")
        return df

    def analyze_missing_patterns(self, df: pd.DataFrame) -> None:
        """
        Log a structured missing-data report BEFORE the final dropna step.

        This makes the data loss fully transparent and traceable. The largest
        source of missing data is 'Review Scores Rating': listings with no
        reviews yet have no rating, which is expected business behaviour
        (survivor-bias consideration for the downstream analysis).

        Args:
            df: Input DataFrame (post-imputation, pre-final drop).
        """
        self.logger.info("=" * 60)
        self.logger.info("MISSING DATA PATTERN ANALYSIS (pre-drop)")
        self.logger.info("=" * 60)

        total_rows = len(df)
        missing_summary = df.isnull().sum()
        missing_summary = missing_summary[missing_summary > 0]

        if missing_summary.empty:
            self.logger.info("No missing values detected — all fields complete.")
        else:
            business_reasons = {
                'Review Scores Rating': (
                    "New listings with no guest reviews yet have no rating. "
                    "Dropping these means the analysis reflects only established, "
                    "reviewed listings (survivor-bias caveat documented in EDA)."
                ),
                'Beds': (
                    "Likely data entry omissions in the source system. "
                    "No imputation strategy is defensible without additional context."
                ),
                'Zipcode': (
                    "Incomplete host registration data. "
                    "Rows without a Zipcode cannot be included in geographic analysis."
                ),
                'Host Since': (
                    "Missing host registration date — likely incomplete host profiles."
                ),
            }

            for col, count in missing_summary.items():
                pct = count / total_rows * 100
                reason = business_reasons.get(col, "Reason: unknown — investigate source.")
                self.logger.info(
                    f"  [{col}]: {count:,} missing ({pct:.1f}%) — {reason}"
                )

        self.logger.info("=" * 60)

    def validate_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply explicit business rules to remove logically invalid records.

        Rules enforced:
          - Review Scores Rating must be in [1, 100].
          - Number of Records must be >= 1 (a listing must have at least one record).
          - Beds must be >= 1 (a property with 0 beds is not a valid rental unit).
          - All key fields must be non-null.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: Validated DataFrame with invalid records removed.
        """
        initial_count = len(df)

        # Rule 1: Rating must be within the valid 1–100 scale
        invalid_ratings = df[
            (df['Review Scores Rating'] < 1) | (df['Review Scores Rating'] > 100)
        ]
        if len(invalid_ratings) > 0:
            df = df[
                (df['Review Scores Rating'] >= 1) & (df['Review Scores Rating'] <= 100)
            ]
            self.logger.warning(
                f"Removed {len(invalid_ratings)} records with out-of-range review scores."
            )

        # Rule 2: Number of Records must be >= 1
        no_records = df[df['Number of Records'] < 1]
        if len(no_records) > 0:
            df = df[df['Number of Records'] >= 1]
            self.logger.warning(
                f"Removed {len(no_records)} records with anomalous zero-record counts."
            )

        # Rule 3: Beds must be >= 1 — properties with 0 beds are not valid rental units
        zero_beds = df[df['Beds'] < 1]
        if len(zero_beds) > 0:
            df = df[df['Beds'] >= 1]
            self.logger.warning(
                f"Removed {len(zero_beds)} records with Beds < 1 (not a valid rental unit)."
            )

        # Rule 4: Drop rows with any missing key fields
        key_fields = [
            'Host Id', 'Host Since', 'Neighbourhood', 'Zipcode',
            'Property Type', 'Room Type', 'Beds', 'Price',
            'Number of Records', 'Number Of Reviews', 'Review Scores Rating'
        ]
        existing_key_fields = [f for f in key_fields if f in df.columns]
        df = df.dropna(subset=existing_key_fields)

        final_count = len(df)
        removed_count = initial_count - final_count
        if removed_count > 0:
            self.logger.info(
                f"Validation complete: removed {removed_count:,} rows with missing key fields. "
                f"Final row count: {final_count:,}."
            )
        return df

    def optimize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Downcast data types to reduce memory footprint and improve query performance.

        Categorical columns (Neighbourhood, Room Type, Property Type) are converted
        to pandas 'category' dtype, which uses integer codes internally and can
        reduce memory by 50–90% for low-cardinality string columns.

        NOTE ON BEDS: Beds is kept as float64 (its post-CSV dtype). It is NOT
        converted to category because Beds has meaningful ordinal relationships
        (2 beds > 1 bed) and may be used in regression or sorting operations.

        NOTE ON ZIPCODE: Zipcode is stored as a string to prevent arithmetic
        operations (adding/subtracting zip codes is meaningless) and to preserve
        leading zeros if they appear in other geographic datasets.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: Memory-optimized DataFrame.
        """
        # Convert low-cardinality string columns to pandas category dtype
        categorical_columns = ['Neighbourhood', 'Room Type', 'Property Type']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype('category')

        # Zipcode: store as string — it is a geographic identifier, not a number
        if 'Zipcode' in df.columns:
            df['Zipcode'] = df['Zipcode'].astype('Int64').astype(str)
            df['Zipcode'] = df['Zipcode'].replace('<NA>', pd.NA)

        # Reorder columns for logical readability (identity → location → property → metrics)
        column_order = [
            'Host Id', 'Host Since', 'Neighbourhood', 'Zipcode',
            'Property Type', 'Room Type', 'Beds', 'Price',
            'Number of Records', 'Number Of Reviews', 'Review Scores Rating'
        ]
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        self.logger.info("Data types optimized and columns reordered.")
        return df

    def save_cleaned_data(self, df: pd.DataFrame) -> None:
        """
        Persist the cleaned dataset to a CSV file.

        Args:
            df: The fully cleaned DataFrame.

        Raises:
            Exception: If the file cannot be written.
        """
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.output_path, index=False)
            self.logger.info(f"Cleaned dataset saved to: {self.output_path}")
            self.logger.info(
                f"Final dimensions: {df.shape[0]:,} rows x {df.shape[1]} columns"
            )
        except Exception as e:
            self.logger.error(f"Error saving dataset: {e}")
            raise

    def generate_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Generate a structured summary of the final cleaned dataset.

        Args:
            df: The final cleaned DataFrame.

        Returns:
            dict: Summary statistics for logging and reporting.
        """
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 ** 2,
            'price_stats': {
                'mean':   df['Price'].mean(),
                'median': df['Price'].median(),
                'std':    df['Price'].std(),
                'min':    df['Price'].min(),
                'max':    df['Price'].max(),
                'p95':    df['Price'].quantile(0.95),
                'p99':    df['Price'].quantile(0.99),
            },
            'neighbourhood_distribution': df['Neighbourhood'].value_counts().to_dict()
        }

        self.logger.info("Data summary generated successfully.")
        return summary

    # ------------------------------------------------------------------ #
    #  M A I N   P I P E L I N E
    # ------------------------------------------------------------------ #

    def process(self) -> Tuple[pd.DataFrame, dict]:
        """
        Execute the full ETL pipeline end-to-end.

        Pipeline order:
          1. load_data              — Extract raw data
          2. clean_column_names     — Sanitize headers
          3. remove_duplicates      — Remove duplicate host-registration records
          4. convert_data_types     — Cast to correct types
          5. drop_unnecessary_columns — Remove redundant columns
          6. impute_missing_prices  — Defensive price gap-filling (no-op if Price complete)
          7. analyze_missing_patterns — Log remaining gaps BEFORE dropping
          8. validate_data_quality  — Apply business rules; drop invalid/incomplete rows
          9. optimize_data_types    — Downcast for memory efficiency; fix Zipcode dtype
          10. generate_data_summary — Produce final statistics dict
          11. save_cleaned_data     — Persist to CSV

        Returns:
            Tuple[pd.DataFrame, dict]: Cleaned DataFrame and summary statistics.

        Raises:
            Exception: Propagates any unhandled error from a pipeline step.
        """
        try:
            self.logger.info("Initiating the complete Airbnb ETL Pipeline.")

            df = self.load_data()
            df = self.clean_column_names(df)
            df = self.remove_duplicates(df)
            df = self.convert_data_types(df)
            df = self.drop_unnecessary_columns(df)
            df = self.impute_missing_prices(df)
            self.analyze_missing_patterns(df)     # Document gaps BEFORE the final drop
            df = self.validate_data_quality(df)
            df = self.optimize_data_types(df)

            summary = self.generate_data_summary(df)
            self.save_cleaned_data(df)

            self.logger.info("ETL Pipeline completed successfully.")
            return df, summary

        except Exception as e:
            self.logger.error(f"ETL Pipeline failed: {e}")
            raise


# ------------------------------------------------------------------ #
#  E N T R Y   P O I N T
# ------------------------------------------------------------------ #

def main():
    """
    Entry point for running the ETL pipeline as a standalone script.
    """
    try:
        processor = AirbnbETLProcessor(
            input_path="Datasource/airbnb.xlsx",
            output_path="Datasource/airbnb_clean.csv"
        )

        cleaned_df, summary = processor.process()

        print("\n" + "=" * 55)
        print("ETL PROCESS SUMMARY")
        print("=" * 55)
        print(f"Total rows:       {summary['total_rows']:,}")
        print(f"Total columns:    {summary['total_columns']}")
        print(f"Missing values:   {summary['missing_values']}")
        print(f"Duplicate rows:   {summary['duplicate_rows']}")
        print(f"Memory usage:     {summary['memory_usage_mb']:.2f} MB")
        print(f"Price range:      ${summary['price_stats']['min']:.0f} — ${summary['price_stats']['max']:.0f}")
        print(f"Price median:     ${summary['price_stats']['median']:.0f}")
        print(f"Price mean:       ${summary['price_stats']['mean']:.0f}")
        print(f"Price P95:        ${summary['price_stats']['p95']:.0f}")
        print("=" * 55)

    except Exception as e:
        logger.error(f"Main process failed: {e}")
        raise


if __name__ == "__main__":
    main()
