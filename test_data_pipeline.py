#!/usr/bin/env python
"""Test data pipeline"""
import sys
sys.path.insert(0, '.')

from backend.services.data_service import DataService

print("Testing Data Pipeline...")
print("=" * 50)

ds = DataService('data')
success, status = ds.process()

print(f"✓ Pipeline Success: {success}")
print(f"✓ Loaded: {status['loaded']}")
print(f"✓ Cleaned: {status['cleaned']}")
print(f"✓ Joined: {status['joined']}")
print(f"✓ Validated: {status['validated']}")

if ds.processed_df is not None:
    print(f"\n✓ Total Records: {len(ds.processed_df)}")
    print(f"✓ Columns: {list(ds.processed_df.columns)}")
    
    # Print summary
    summary = ds.get_summary()
    print(f"\n✓ Summary:")
    print(f"  - Total Incidents: {summary['total_incidents']}")
    print(f"  - Regions: {summary['region_count']}")
    print(f"  - Total Affected Customers: {summary['total_affected_customers']}")
    print(f"  - Latest Incident: {summary['latest_incident']}")
    
    # Print validation
    print(f"\n✓ Data Quality:")
    validation = status['validation']
    print(f"  - Is Valid: {validation['is_valid']}")
    print(f"  - Join Success Rate: {validation['data_quality']['join_success_rate']}%")
    print(f"  - Complete Records: {validation['data_quality']['complete_records']}")
    
    # Print first record
    print(f"\n✓ Sample Record (First Incident):")
    first_record = ds.processed_df.iloc[0]
    print(f"  - Outage ID: {first_record['outage_id']}")
    print(f"  - Region: {first_record['region']}")
    print(f"  - Severity: {first_record['severity']}")
    print(f"  - Complaints: {first_record['complaint_count']}")
    print(f"  - Affected Customers: {first_record['affected_customers']}")
    print(f"  - Avg Traffic (Gbps): {first_record['avg_traffic_gbps']}")

print("\n" + "=" * 50)
print("✓ Data Pipeline Test Complete!")
