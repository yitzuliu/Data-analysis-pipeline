import pandas as pd
import numpy as np
import os
import warnings

class DatasetEvaluator:
    """
    A professional object-oriented class for evaluating dataset quality metrics.
    Designed to process both CSV and Excel files, calculating completeness,
    uniqueness, and providing an overall quality score.
    """
    def __init__(self, data_path: str = "Datasource/"):
        self.data_path = data_path
        self.datasets = {}
        self.count = 0

    def calculate_data_quality_metrics(self, df: pd.DataFrame, dataset_name: str) -> dict:
        """Calculate comprehensive data quality metrics for a dataset"""
        
        # Basic metrics
        total_rows = df.shape[0]
        total_columns = df.shape[1]
        total_cells = total_rows * total_columns
        
        # Missing data metrics
        missing_cells = df.isnull().sum().sum()
        missing_ratio = missing_cells / total_cells if total_cells > 0 else 0
        completeness_score = (1 - missing_ratio) * 100
        
        # Duplicate analysis
        duplicate_rows = df.duplicated().sum()
        duplicate_ratio = duplicate_rows / total_rows if total_rows > 0 else 0
        uniqueness_score = (1 - duplicate_ratio) * 100
        
        # Data type consistency (numeric vs object columns)
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        object_cols = len(df.select_dtypes(include=['object']).columns)
        datetime_cols = len(df.select_dtypes(include=['datetime64']).columns)
        
        # Overall quality score (weighted average)
        overall_quality = (completeness_score * 0.5 + uniqueness_score * 0.5)
        
        quality_metrics = {
            'dataset_name': dataset_name,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'missing_cells': missing_cells,
            'missing_ratio': missing_ratio,
            'completeness_score': completeness_score,
            'duplicate_rows': duplicate_rows,
            'uniqueness_score': uniqueness_score,
            'numeric_columns': numeric_cols,
            'object_columns': object_cols,
            'datetime_columns': datetime_cols,
            'overall_quality_score': overall_quality
        }
        
        return quality_metrics

    def display_quality_metrics(self, quality_metrics: dict):
        """Display data quality metrics in a formatted way"""
        
        print(f"\\n📊 DATA QUALITY METRICS:")
        print(f"  🎯 Completeness Score: {quality_metrics['completeness_score']:.1f}%")
        print(f"  🔄 Uniqueness Score: {quality_metrics['uniqueness_score']:.1f}%")
        print(f"  🏆 Overall Quality Score: {quality_metrics['overall_quality_score']:.1f}%")
        
        if quality_metrics['duplicate_rows'] > 0:
            print(f"  ⚠️  Duplicate rows: {quality_metrics['duplicate_rows']:,}")
        
        # Quality assessment
        score = quality_metrics['overall_quality_score']
        if score >= 90:
            quality_level = "Excellent ⭐⭐⭐"
        elif score >= 75:
            quality_level = "Good ⭐⭐"
        elif score >= 60:
            quality_level = "Fair ⭐"
        else:
            quality_level = "Poor ⚠️"
        
        print(f"Quality Level: {quality_level}")

    def load_and_inspect_dataset(self, filename: str, dataset_name: str) -> tuple:
        """Load dataset and return basic information"""
        try:
            file_path = os.path.join(self.data_path, filename)
            
            # Load dataset based on file extension
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
                
                # Store dataset
                self.datasets[dataset_name] = df
                
                # Display information for CSV
                self.display_dataset_info(filename, dataset_name, df=df)
                
                return True, "Success"
                
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                # Load all sheets from Excel file
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                
                # Load all sheets into a dictionary
                excel_data = {}
                for sheet_name in sheet_names:
                    sheet_df = pd.read_excel(file_path, sheet_name=sheet_name)
                    excel_data[sheet_name] = sheet_df
                    
                    # Store each sheet individually in datasets
                    if len(sheet_names) == 1:
                        sheet_key = dataset_name
                    else:
                        sheet_key = f"{dataset_name}_{sheet_name}"
                    self.datasets[sheet_key] = sheet_df
                
                # Display comprehensive information for all sheets
                self.display_dataset_info(filename, dataset_name, excel_data=excel_data)
                
                return True, "Success"
                    
            else:
                return None, f"Unsupported file format for {filename}"
            
        except Exception as e:
            return None, f"Error loading {filename}: {str(e)}"

    def display_dataset_info(self, filename: str, dataset_name: str, df: pd.DataFrame = None, excel_data: dict = None):
        """Display comprehensive information for a dataset (CSV or Excel with all sheets)"""
        
        print(f"\\n{'='*60}")
        print(f"DATASET: {dataset_name.upper()}")
        print(f"File: {filename}")
        
        # Handle CSV files
        if df is not None and excel_data is None:
            print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            print(f"\\nColumn Names:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i:2d}. {col}")
            
            print(f"\\nData Types:")
            print(df.dtypes.value_counts())
            
            # Missing data analysis
            print(f"\\nMissing Data Analysis:")
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
            
            print(f"  • Total missing cells: {missing_cells:,} ({missing_percentage:.1f}%)")
            
            # Calculate and display quality metrics for CSV
            quality_metrics = self.calculate_data_quality_metrics(df, dataset_name)
            self.display_quality_metrics(quality_metrics)
        
        # Handle Excel files with all sheets
        elif excel_data is not None:
            sheet_names = list(excel_data.keys())
            total_sheets = len(sheet_names)
            print(f"📋 File Type: Excel with {total_sheets} sheet(s)")
            print(f" Sheet Names: {sheet_names}")
            
            # Calculate total statistics across all sheets
            total_rows = sum(excel_data[sheet].shape[0] for sheet in sheet_names)
            total_memory = sum(excel_data[sheet].memory_usage(deep=True).sum() for sheet in sheet_names) / 1024**2
            
            print(f"📊 Total Data: {total_rows:,} rows across all sheets")
            print(f"💾 Total Memory usage: {total_memory:.2f} MB")
            
            # Display information for each sheet
            for i, sheet_name in enumerate(sheet_names, 1):
                sheet_df = excel_data[sheet_name]
                print(f"\\n{'-'*50}")
                print(f"SHEET {i}/{total_sheets}: {sheet_name.upper()}")
                print(f"{'-'*50}")
                print(f"📊 Shape: {sheet_df.shape[0]:,} rows × {sheet_df.shape[1]} columns")
                
                print(f"\\n📋 Column Names:")
                for j, col in enumerate(sheet_df.columns, 1):
                    print(f"  {j:2d}. {col}")
                
                print(f"\\n🔍 Data Types:")
                print(sheet_df.dtypes.value_counts())
                
                # Missing data analysis for each sheet
                print(f"\\n🕳️  Missing Data Analysis:")
                total_cells = sheet_df.shape[0] * sheet_df.shape[1]
                missing_cells = sheet_df.isnull().sum().sum()
                missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
                
                print(f"  • Total missing cells: {missing_cells:,} ({missing_percentage:.1f}%)")
                
                # Calculate and display quality metrics for each sheet
                sheet_quality_metrics = self.calculate_data_quality_metrics(sheet_df, f"{dataset_name}_{sheet_name}")
                self.display_quality_metrics(sheet_quality_metrics)
            
            # Calculate overall quality metrics for the entire Excel file (all sheets combined)
            print(f"\\n{'='*50}")
            print(f"OVERALL FILE QUALITY: {dataset_name.upper()}")
            print(f"{'='*50}")
            
            # Combine all sheets into one large DataFrame for overall analysis
            combined_df = pd.concat(excel_data.values(), ignore_index=True)
            overall_quality_metrics = self.calculate_data_quality_metrics(combined_df, f"{dataset_name}_OVERALL")
            
            print(f"📊 Combined Analysis Across All {total_sheets} Sheets:")
            self.display_quality_metrics(overall_quality_metrics)

    def evaluate_all(self):
        """Evaluate all valid datasets in the data path"""
        if not os.path.exists(self.data_path):
            print(f"Error: Data path '{self.data_path}' does not exist.")
            return
            
        for filename in os.listdir(self.data_path):
            # Skip temporary files, hidden files, and clean ones
            if filename.startswith('.') or filename.startswith('~$') or 'clean' in filename:
                continue
                
            # Only process supported file types
            if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
                continue
                
            dataset_name = os.path.splitext(filename)[0]
            result, message = self.load_and_inspect_dataset(filename, dataset_name)
            if result is None:
                print(f"❌ {message}")
            else:
                self.count += 1
        print(f"\\n✅ Successfully evaluated {self.count} core datasets from the directory '{self.data_path}'.")

if __name__ == "__main__":
    # Change path logic if run directly from within the folder or root
    base_path = "../Datasource/" if os.path.exists("../Datasource/") else "Datasource/"
    evaluator = DatasetEvaluator(data_path=base_path)
    evaluator.evaluate_all()
