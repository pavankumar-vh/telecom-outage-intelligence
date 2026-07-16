"""
Unit tests for Anomaly Detection Service

Tests complaint spike detection, regional concentration, and customer base anomalies
using both synthetic and real incident data.
"""

import logging
from backend.services.data_service import DataService
from backend.services.anomaly_service import AnomalyDetectionService
from backend.models.anomalies import AnomalySeverity, AnomalyType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_complaint_spike_detection():
    """Test detection of complaint spikes."""
    logger.info("Testing complaint spike detection...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create synthetic data with known baselines
    incidents = [
        {"outage_id": f"INC-BASE-{i:03d}", "region": "US-EAST-01", "complaint_count": 3,
         "affected_customers": 500, "max_escalation": 2, "avg_traffic_gbps": 50, "severity": "Minor"}
        for i in range(10)
    ]
    
    # Add spike incident
    spike_incident = {
        "outage_id": "INC-SPIKE-001",
        "region": "US-EAST-01",
        "complaint_count": 10,  # Much higher than baseline
        "affected_customers": 500,
        "max_escalation": 4,
        "avg_traffic_gbps": 50,
        "severity": "Critical"
    }
    incidents.append(spike_incident)
    
    # Calculate baselines
    anomaly_service.calculate_baselines(incidents)
    
    # Detect anomalies for spike incident
    flags = anomaly_service.detect_complaint_spike(spike_incident)
    
    assert len(flags) > 0, "Complaint spike should be detected"
    assert flags[0].anomaly_type == AnomalyType.COMPLAINT_SPIKE
    assert flags[0].severity in [AnomalySeverity.HIGH, AnomalySeverity.MEDIUM]
    
    logger.info(f"  ✓ Complaint spike detected: {flags[0].description}")
    logger.info(f"    Severity: {flags[0].severity}, Deviation: {flags[0].deviation_percent:.1f}%")


def test_customer_base_anomaly_detection():
    """Test detection of unusual customer base impact."""
    logger.info("Testing customer base anomaly detection...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create baseline incidents
    incidents = [
        {"outage_id": f"INC-BASE-{i:03d}", "region": "US-WEST-01", "complaint_count": 2,
         "affected_customers": 200, "max_escalation": 1, "avg_traffic_gbps": 30, "severity": "Minor"}
        for i in range(8)
    ]
    
    # Add anomaly incident with many affected customers
    anomaly_incident = {
        "outage_id": "INC-CUST-001",
        "region": "US-WEST-01",
        "complaint_count": 5,
        "affected_customers": 5000,  # Much higher than baseline
        "max_escalation": 3,
        "avg_traffic_gbps": 80,
        "severity": "Major"
    }
    incidents.append(anomaly_incident)
    
    anomaly_service.calculate_baselines(incidents)
    flags = anomaly_service.detect_customer_base_anomaly(anomaly_incident)
    
    assert len(flags) > 0, "Customer base anomaly should be detected"
    assert flags[0].anomaly_type == AnomalyType.CUSTOMER_BASE_ANOMALY
    
    logger.info(f"  ✓ Customer base anomaly detected: {flags[0].description}")
    logger.info(f"    Severity: {flags[0].severity}, Deviation: {flags[0].deviation_percent:.1f}%")


def test_regional_concentration_detection():
    """Test detection of regional incident concentration."""
    logger.info("Testing regional concentration detection...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create incidents spread across regions
    incidents = [
        {"outage_id": "INC-R1-001", "region": "US-EAST-01", "complaint_count": 2,
         "affected_customers": 300, "max_escalation": 1, "avg_traffic_gbps": 40, "severity": "Minor"},
        {"outage_id": "INC-R1-002", "region": "US-EAST-01", "complaint_count": 3,
         "affected_customers": 400, "max_escalation": 2, "avg_traffic_gbps": 50, "severity": "Minor"},
        {"outage_id": "INC-R1-003", "region": "US-EAST-01", "complaint_count": 2,
         "affected_customers": 250, "max_escalation": 1, "avg_traffic_gbps": 35, "severity": "Warning"},
        {"outage_id": "INC-R1-004", "region": "US-EAST-01", "complaint_count": 4,
         "affected_customers": 350, "max_escalation": 2, "avg_traffic_gbps": 45, "severity": "Minor"},
        # Add one incident in different region
        {"outage_id": "INC-R2-001", "region": "EMEA-WEST", "complaint_count": 2,
         "affected_customers": 200, "max_escalation": 1, "avg_traffic_gbps": 30, "severity": "Minor"},
    ]
    
    anomaly_service.calculate_baselines(incidents)
    
    # Check concentration in US-EAST-01
    flags = anomaly_service.detect_regional_concentration(incidents[0], incidents)
    
    assert len(flags) > 0, "Regional concentration should be detected"
    assert flags[0].anomaly_type == AnomalyType.REGIONAL_CONCENTRATION
    
    logger.info(f"  ✓ Regional concentration detected: {flags[0].description}")
    logger.info(f"    Severity: {flags[0].severity}, Actual: {flags[0].actual_value:.0f}")


def test_high_impact_region_detection():
    """Test detection of high-impact regions."""
    logger.info("Testing high impact region detection...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create baseline with normal traffic
    incidents = [
        {"outage_id": f"INC-BASE-{i:03d}", "region": "ASIA-PAC", "complaint_count": 2,
         "affected_customers": 300, "max_escalation": 1, "avg_traffic_gbps": 100, "severity": "Minor"}
        for i in range(8)
    ]
    
    # Add incident with high traffic
    high_traffic_incident = {
        "outage_id": "INC-TRAFFIC-001",
        "region": "ASIA-PAC",
        "complaint_count": 5,
        "affected_customers": 800,
        "max_escalation": 3,
        "avg_traffic_gbps": 500.0,  # Much higher than baseline
        "severity": "Critical"
    }
    incidents.append(high_traffic_incident)
    
    anomaly_service.calculate_baselines(incidents)
    flags = anomaly_service.detect_high_impact_region(high_traffic_incident)
    
    assert len(flags) > 0, "High impact region should be detected"
    assert flags[0].anomaly_type == AnomalyType.HIGH_IMPACT_REGION
    
    logger.info(f"  ✓ High impact region detected: {flags[0].description}")
    logger.info(f"    Severity: {flags[0].severity}, Deviation: {flags[0].deviation_percent:.1f}%")


def test_multi_anomaly_detection():
    """Test detection of multiple anomalies in single incident."""
    logger.info("Testing multi-anomaly detection...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create baseline incidents
    base_incidents = [
        {"outage_id": f"INC-BASE-{i:03d}", "region": f"REGION-{i%3:02d}", "complaint_count": 2,
         "affected_customers": 300, "max_escalation": 1, "avg_traffic_gbps": 50, "severity": "Minor"}
        for i in range(12)
    ]
    
    # Create incident with multiple anomalies
    multi_anomaly = {
        "outage_id": "INC-MULTI-001",
        "region": "REGION-00",
        "complaint_count": 15,  # Spike
        "affected_customers": 8000,  # Unusual customers
        "max_escalation": 5,
        "avg_traffic_gbps": 600,  # High traffic
        "severity": "Critical"
    }
    
    all_incidents = base_incidents + [multi_anomaly]
    anomaly_service.calculate_baselines(all_incidents)
    
    # Detect all anomalies
    incident_anomalies = anomaly_service.detect_incident_anomalies(multi_anomaly, all_incidents)
    
    assert incident_anomalies.has_anomalies, "Should detect anomalies"
    assert incident_anomalies.total_flags > 1, "Should detect multiple anomalies"
    
    logger.info(f"  ✓ Multiple anomalies detected: {incident_anomalies.total_flags} total")
    for flag in incident_anomalies.anomaly_flags:
        logger.info(f"    - {flag.anomaly_type}: {flag.description}")


def test_anomaly_detection_with_real_data():
    """Test anomaly detection with real data from data pipeline."""
    logger.info("Testing anomaly detection with real data pipeline...")
    
    # Load real data
    data_service = DataService()
    success, result = data_service.process()
    
    if not success or not result.get("validated"):
        logger.error("Data pipeline validation failed")
        return
    
    processed_data = data_service.get_processed_data()
    if not processed_data:
        logger.error("No processed data available")
        return
    
    logger.info(f"  Loaded {len(processed_data)} incidents from data pipeline")
    
    # Run anomaly detection
    anomaly_service = AnomalyDetectionService()
    response = anomaly_service.detect_all_anomalies(processed_data)
    
    logger.info(f"  ✓ Anomaly detection complete")
    logger.info(f"    Total incidents analyzed: {response.total_incidents_analyzed}")
    logger.info(f"    Incidents with anomalies: {response.incidents_with_anomalies}")
    logger.info(f"    Total anomalies: {response.total_anomalies}")
    logger.info(f"    High severity: {response.high_severity_anomalies}")
    
    # Display anomalies by incident
    if response.incidents_with_anomalies > 0:
        logger.info("\n  Incidents with Anomalies:")
        for incident in response.incidents[:3]:  # Show top 3
            logger.info(f"    {incident.outage_id} ({incident.region}):")
            for flag in incident.anomaly_flags:
                logger.info(f"      - [{flag.severity.upper()}] {flag.description}")


def test_no_anomalies_normal_data():
    """Test that normal data doesn't trigger false positives."""
    logger.info("Testing normal data (no anomalies)...")
    
    anomaly_service = AnomalyDetectionService()
    
    # Create normal incidents with consistent metrics
    normal_incidents = [
        {"outage_id": f"INC-NORMAL-{i:03d}", "region": "US-EAST-01", "complaint_count": 3,
         "affected_customers": 400, "max_escalation": 2, "avg_traffic_gbps": 60, "severity": "Minor"}
        for i in range(10)
    ]
    
    anomaly_service.calculate_baselines(normal_incidents)
    
    # Check that normal incidents don't trigger anomalies
    for incident in normal_incidents[:3]:
        flags = []
        flags.extend(anomaly_service.detect_complaint_spike(incident))
        flags.extend(anomaly_service.detect_customer_base_anomaly(incident))
        
        assert len(flags) == 0, f"Normal incident {incident['outage_id']} triggered false positive"
    
    logger.info("  ✓ Normal data correctly identified - no false positives")


def run_all_tests():
    """Run all unit tests."""
    logger.info("=" * 70)
    logger.info("ANOMALY DETECTION SERVICE - UNIT TESTS")
    logger.info("=" * 70)
    logger.info("")
    
    test_functions = [
        test_complaint_spike_detection,
        test_customer_base_anomaly_detection,
        test_regional_concentration_detection,
        test_high_impact_region_detection,
        test_multi_anomaly_detection,
        test_no_anomalies_normal_data,
        test_anomaly_detection_with_real_data,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
            logger.info(f"✓ {test_func.__name__} PASSED\n")
        except AssertionError as e:
            failed += 1
            logger.error(f"✗ {test_func.__name__} FAILED: {str(e)}\n")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_func.__name__} ERROR: {str(e)}\n")
    
    logger.info("=" * 70)
    logger.info(f"TEST RESULTS: {passed} passed, {failed} failed")
    logger.info("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
