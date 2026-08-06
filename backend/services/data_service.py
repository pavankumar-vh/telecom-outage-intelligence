"""Data service for loading and processing outage data"""
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class DataService:
    """Service for data ingestion, cleaning, and integration"""
    
    def __init__(self, data_dir: str = "../data"):
        """Initialize data service with data directory path"""
        self.data_dir = data_dir
        self.outage_df = None
        self.complaints_df = None
        self.usage_df = None
        self.processed_df = None
        self.validated = False
    
    def load_datasets(self) -> bool:
        """Load all three datasets from CSV files"""
        try:
            outage_path = os.path.join(self.data_dir, "outage_alerts.csv")
            complaints_path = os.path.join(self.data_dir, "complaint_logs.csv")
            usage_path = os.path.join(self.data_dir, "usage_metrics.csv")
            
            # Load datasets
            self.outage_df = pd.read_csv(outage_path)
            self.complaints_df = pd.read_csv(complaints_path)
            self.usage_df = pd.read_csv(usage_path)
            
            logger.info(f"Loaded outage alerts: {len(self.outage_df)} records")
            logger.info(f"Loaded complaints: {len(self.complaints_df)} records")
            logger.info(f"Loaded usage metrics: {len(self.usage_df)} records")
            
            return True
        except Exception as e:
            logger.error(f"Error loading datasets: {str(e)}")
            return False
    
    def clean_datasets(self) -> bool:
        """Clean and normalize datasets"""
        try:
            if self.outage_df is None or self.complaints_df is None or self.usage_df is None:
                logger.error("Datasets not loaded")
                return False
            
            # Convert timestamps to datetime
            self.outage_df['timestamp'] = pd.to_datetime(self.outage_df['timestamp'])
            self.complaints_df['timestamp'] = pd.to_datetime(self.complaints_df['timestamp'])
            self.usage_df['timestamp'] = pd.to_datetime(self.usage_df['timestamp'])
            
            # Standardize region names (uppercase)
            self.outage_df['region'] = self.outage_df['region'].str.upper()
            self.complaints_df['region'] = self.complaints_df['region'].str.upper()
            self.usage_df['region'] = self.usage_df['region'].str.upper()
            
            # Handle missing values
            self.outage_df['duration_minutes'] = self.outage_df['duration_minutes'].fillna(0)
            self.complaints_df['customer_count'] = self.complaints_df['customer_count'].fillna(0)
            self.usage_df['traffic_gbps'] = self.usage_df['traffic_gbps'].fillna(0)
            self.usage_df['active_users'] = self.usage_df['active_users'].fillna(0)
            self.usage_df['peak_utilization_percent'] = self.usage_df['peak_utilization_percent'].fillna(0)
            
            # Ensure numeric types
            self.outage_df['duration_minutes'] = self.outage_df['duration_minutes'].astype(int)
            self.complaints_df['customer_count'] = self.complaints_df['customer_count'].astype(int)
            self.usage_df['traffic_gbps'] = self.usage_df['traffic_gbps'].astype(float)
            self.usage_df['active_users'] = self.usage_df['active_users'].astype(int)
            
            logger.info("Datasets cleaned and normalized")
            return True
        except Exception as e:
            logger.error(f"Error cleaning datasets: {str(e)}")
            return False
    
    def join_datasets(self) -> bool:
        """Join all three datasets on region and temporal proximity using fast vectorized merges"""
        try:
            if self.outage_df is None or self.complaints_df is None or self.usage_df is None:
                logger.error("Datasets not loaded or cleaned")
                return False
            
            # Start with outage data
            self.processed_df = self.outage_df.copy()
            self.processed_df['date'] = self.processed_df['timestamp'].dt.date
            self.processed_df['hour'] = self.processed_df['timestamp'].dt.hour
            
            # 1. FAST COMPLAINTS AGGREGATION
            # Instead of O(N^2) time windows, we group complaints by region, date, and hour
            self.complaints_df['date'] = self.complaints_df['timestamp'].dt.date
            self.complaints_df['hour'] = self.complaints_df['timestamp'].dt.hour
            
            # Convert escalation to numeric for max() aggregation
            esc_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
            self.complaints_df['esc_num'] = self.complaints_df['escalation_level'].map(esc_map).fillna(0)
            
            complaints_agg = self.complaints_df.groupby(['region', 'date', 'hour']).agg(
                complaint_count=('customer_count', 'count'),
                total_affected_customers=('customer_count', 'sum'),
                max_escalation_level=('esc_num', 'max')
            ).reset_index()
            
            # Merge complaints into processed_df
            self.processed_df = pd.merge(
                self.processed_df, complaints_agg,
                on=['region', 'date', 'hour'],
                how='left'
            )
            
            self.processed_df.rename(columns={
                'total_affected_customers': 'affected_customers',
                'max_escalation_level': 'max_escalation'
            }, inplace=True)
            
            # 2. FAST USAGE AGGREGATION
            # Use pre-calculated region stats instead of scanning 101K rows per incident
            usage_stats = self.usage_df.groupby("region").agg(
                avg_traffic=("traffic_gbps", "mean"),
                peak_users=("active_users", "max"),
                peak_utilization=("peak_utilization_percent", "max")
            ).reset_index()
            
            # Merge usage into processed_df
            self.processed_df = pd.merge(
                self.processed_df, usage_stats,
                on='region',
                how='left'
            )
            
            self.processed_df.rename(columns={
                'avg_traffic': 'avg_traffic_gbps',
                'peak_users': 'peak_active_users'
            }, inplace=True)
            
            # Fill NaN values (where merges found no matches)
            fill_cols = ['complaint_count', 'affected_customers', 'max_escalation', 
                         'avg_traffic_gbps', 'peak_active_users', 'peak_utilization']
            for col in fill_cols:
                if col in self.processed_df.columns:
                    self.processed_df[col] = self.processed_df[col].fillna(0)
            
            # Drop temporary columns
            self.processed_df.drop(columns=['date', 'hour'], inplace=True, errors='ignore')
            
            # If 101K outages is too large for the frontend to render, take the top 1000 most recent active
            # (or just limit it so the API doesn't crash sending a 50MB JSON payload)
            if len(self.processed_df) > 2000:
                logger.info(f"Subsampling {len(self.processed_df)} incidents to 2000 for performance")
                # Prioritize Critical/Major and recent ones
                sev_order = pd.CategoricalDtype(["Critical", "Major", "Warning", "Minor"], ordered=True)
                self.processed_df['severity'] = self.processed_df['severity'].astype(sev_order)
                self.processed_df = self.processed_df.sort_values(['severity', 'timestamp'], ascending=[True, False]).head(2000)
            
            logger.info(f"Datasets joined successfully. Total records: {len(self.processed_df)}")
            return True
        except Exception as e:
            logger.error(f"Error joining datasets: {str(e)}")
            return False
    
    def validate_data(self) -> Dict[str, Any]:
        """Validate processed data quality"""
        if self.processed_df is None:
            return {
                'is_valid': False,
                'total_records': 0,
                'validation_errors': ['No processed data available']
            }
        
        validation_results = {
            'is_valid': True,
            'total_records': len(self.processed_df),
            'validation_errors': [],
            'data_quality': {
                'complete_records': 0,
                'records_with_missing_values': 0,
                'join_success_rate': 0.0
            }
        }
        
        # Check for missing critical values
        critical_columns = ['outage_id', 'region', 'timestamp', 'severity']
        for col in critical_columns:
            if col in self.processed_df.columns:
                missing = self.processed_df[col].isna().sum()
                if missing > 0:
                    validation_results['validation_errors'].append(
                        f"{missing} missing values in {col}"
                    )
        
        # Check join quality
        matched_records = (self.processed_df['complaint_count'] > 0).sum()
        join_rate = (matched_records / len(self.processed_df)) * 100 if len(self.processed_df) > 0 else 0
        validation_results['data_quality']['join_success_rate'] = round(join_rate, 2)
        
        # Count complete records
        validation_results['data_quality']['complete_records'] = len(
            self.processed_df.dropna()
        )
        validation_results['data_quality']['records_with_missing_values'] = len(
            self.processed_df[self.processed_df.isna().any(axis=1)]
        )
        
        # Overall validation
        if len(validation_results['validation_errors']) > 0:
            validation_results['is_valid'] = False
        
        return validation_results
    
    def process(self) -> Tuple[bool, Dict[str, Any]]:
        """Run complete data processing pipeline"""
        pipeline_status = {
            'loaded': False,
            'cleaned': False,
            'joined': False,
            'validated': False,
            'errors': []
        }
        
        # Load datasets
        if not self.load_datasets():
            pipeline_status['errors'].append("Failed to load datasets")
            self.validated = False
            return False, pipeline_status
        pipeline_status['loaded'] = True
        
        # Clean datasets
        if not self.clean_datasets():
            pipeline_status['errors'].append("Failed to clean datasets")
            self.validated = False
            return False, pipeline_status
        pipeline_status['cleaned'] = True
        
        # Join datasets
        if not self.join_datasets():
            pipeline_status['errors'].append("Failed to join datasets")
            self.validated = False
            return False, pipeline_status
        pipeline_status['joined'] = True
        
        # Validate data
        validation = self.validate_data()
        pipeline_status['validated'] = validation['is_valid']
        pipeline_status['validation'] = validation
        self.validated = validation['is_valid']
        
        if not validation['is_valid']:
            pipeline_status['errors'].extend(validation['validation_errors'])
        
        return pipeline_status['loaded'] and pipeline_status['cleaned'] and pipeline_status['joined'], pipeline_status
    
    def get_processed_data(self):
        """Get processed dataset"""
        if self.processed_df is None:
            return None
        
        # Convert to dictionary format for API response
        return self.processed_df.to_dict(orient='records')
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of processed data"""
        if self.processed_df is None:
            return {'error': 'No processed data available'}
        
        return {
            'total_incidents': len(self.processed_df),
            'regions': self.processed_df['region'].unique().tolist(),
            'region_count': self.processed_df['region'].nunique(),
            'severity_distribution': self.processed_df['severity'].value_counts().to_dict(),
            'avg_complaints_per_incident': round(
                self.processed_df['complaint_count'].mean(), 2
            ),
            'avg_affected_customers': round(
                self.processed_df['affected_customers'].mean(), 0
            ),
            'total_affected_customers': int(self.processed_df['affected_customers'].sum()),
            'avg_traffic_impact': round(
                self.processed_df['avg_traffic_gbps'].mean(), 2
            ),
            'latest_incident': self.processed_df['timestamp'].max().isoformat(),
            'oldest_incident': self.processed_df['timestamp'].min().isoformat()
        }
