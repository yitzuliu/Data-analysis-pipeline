# Data Science Portfolio — Airbnb NYC Market Analysis

A complete data science pipeline applied to the Airbnb NYC dataset (17,230 reviewed listings),
demonstrating end-to-end skills from dataset selection through ETL, EDA, and business insight generation.

> 📄 **Analysis findings and business insights:** [Airbnb_Analysis_Conclusions.md](Airbnb_Analysis_Conclusions.md)

## Project Description

This repository demonstrates data science best practices through a systematic workflow:

- **Dataset Evaluation**: Systematic scoring of 6 candidate datasets using a weighted criteria framework (Data Quality 40%, Business Relevance 35%, Technical Complexity 25%)
- **ETL Pipeline**: Production-grade data cleaning including deduplication, type casting, missing data analysis, and business-rule validation — implemented as a reusable OOP class with full logging
- **EDA Analysis**: Univariate, categorical, and bivariate analysis with outlier-aware visualizations and quantified business insights
- **Business Report**: Actionable market intelligence derived from the cleaned dataset (see `Airbnb_Analysis_Conclusions.md`)

## Project Structure

```
├── Dataset_Evaluation_Process/     # Dataset selection and evaluation methodology
├── EDA_Process & Result/            # Exploratory data analysis workflows
├── ETL_Process/                     # Data extraction, transformation, and loading
├── Datasource/                      # Raw datasets and data files
└── README.md                        # Project documentation
```

## How to Run

### EDA Analysis
To run the Exploratory Data Analysis:
```bash
python "EDA_Process & Result/EDA.py"
```

### ETL Process
To run the Extract-Transform-Load process:
```bash
python "ETL_Process/ETL.py"
```

### Dataset Evaluation
To run the dataset evaluation process:
```bash
python "Dataset_Evaluation_Process/Dataset_Evaluation_Process.py"
```

### Jupyter Notebooks
To run the interactive notebooks:
```bash
jupyter notebook "EDA_Process & Result/Airbnb_EDA.ipynb"
jupyter notebook "ETL_Process/ETL_Airbnb_Process.ipynb"
jupyter notebook "Dataset_Evaluation_Process/Dataset_Evaluation_Process.ipynb"
```

## Dependencies

Make sure you have the following Python packages installed:
```bash
pip install pandas numpy matplotlib seaborn jupyter notebook openpyxl
```

## Datasets

The project includes several datasets:
- Airbnb listings data
- Netflix titles
- Spotify features
- Titanic passenger data
- AI adoption data
- Superstore sales data

## Design Notes

- **`.py` files** — Production-grade pipeline engines (reusable, class-based, fully logged)
- **`.ipynb` files** — Step-by-step storytelling notebooks that demonstrate each pipeline stage interactively
- **Logging** — All pipeline runs write to `etl_process.log` / `eda_analysis.log` for full audit trails