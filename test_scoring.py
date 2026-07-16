"""
Unit tests for Impact Scoring Service

Tests the scoring algorithm, component calculations, and ranking logic
using both synthetic and realistic incident data.
"""

import logging
from backend.services.data_service import DataService
from backend.services.scoring_service import ScoringService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_severity_score():
    """Test severity score calculation."""
    logger.info("Testing severity score calculation...")
    scoring = ScoringService()
    
    # Test all severity levels
    test_cases = [
        ("Critical", 1.0),
        ("Major", 0.75),
        ("Warning", 0.5),
        ("Minor", 0.25),
    ]
    
    for severity, expected_value in test_cases:
        score = scoring.calculate_severity_score(severity)
        assert score.level == severity
        assert score.normalized_value == expected_value
        assert score.weight == 0.40
        logger.info(f"  ✓ {severity}: normalized={score.normalized_value}, contribution={score.contribution:.2f}")


def test_complaint_score():
    """Test complaint score calculation."""
    logger.info("Testing complaint score calculation...")
    scoring = ScoringService()
    
    # Test case 1: Low complaints, low escalation
    score = scoring.calculate_complaint_score(10, 1)
    assert score.complaint_count == 10
    assert score.max_escalation == 1
    assert 0 <= score.normalized_value <= 1
    logger.info(f"  ✓ Low complaints (10, esc=1): normalized={score.normalized_value:.2f}")
    
    # Test case 2: Medium complaints, medium escalation
    score = scoring.calculate_complaint_score(50, 3)
    assert score.complaint_count == 50
    assert score.max_escalation == 3
    assert 0 <= score.normalized_value <= 1
    logger.info(f"  ✓ Medium complaints (50, esc=3): normalized={score.normalized_value:.2f}")
    
    # Test case 3: High complaints, high escalation
    score = scoring.calculate_complaint_score(100, 5)
    assert score.complaint_count == 100
    assert score.max_escalation == 5
    assert score.normalized_value > 0.7  # Should be high
    logger.info(f"  ✓ High complaints (100, esc=5): normalized={score.normalized_value:.2f}")


def test_usage_score():
    """Test usage impact score calculation."""
    logger.info("Testing usage impact score calculation...")
    scoring = ScoringService()
    
    # Test case 1: Low impact
    score = scoring.calculate_usage_score(10.0, 1000, 20.0)
    assert 0 <= score.normalized_value <= 1
    logger.info(f"  ✓ Low impact (10 Gbps, 1K users, 20%): normalized={score.normalized_value:.2f}")
    
    # Test case 2: Medium impact
    score = scoring.calculate_usage_score(100.0, 50000, 60.0)
    assert score.avg_traffic_gbps == 100.0
    logger.info(f"  ✓ Medium impact (100 Gbps, 50K users, 60%): normalized={score.normalized_value:.2f}")
    
    # Test case 3: High impact
    score = scoring.calculate_usage_score(500.0, 100000, 95.0)
    assert score.normalized_value > 0.5  # Should be significant
    logger.info(f"  ✓ High impact (500 Gbps, 100K users, 95%): normalized={score.normalized_value:.2f}")


def test_incident_scoring():
    """Test complete incident scoring."""
    logger.info("Testing complete incident scoring...")
    scoring = ScoringService()
    
    # Create synthetic critical incident
    critical_incident = {
        "outage_id": "INC-TEST-001",
        "region": "US-EAST-01",
        "timestamp": "2026-07-15T10:00:00",
        "severity": "Critical",
        "component": "Router",
        "status": "Active",
        "duration_minutes": 180,
        "complaint_count": 85,
        "affected_customers": 5000,
        "max_escalation": 5,
        "avg_traffic_gbps": 450.0,
        "peak_active_users": 95000,
        "peak_utilization": 98.5,
    }
    
    score = scoring.score_incident(critical_incident)
    
    assert score.outage_id == "INC-TEST-001"
    assert score.region == "US-EAST-01"
    assert score.severity == "Critical"
    assert 0 <= score.overall_score <= 100
    assert score.rank is None  # Not set until ranking phase
    assert len(score.explanation) > 0
    
    logger.info(f"  ✓ Critical incident scored: {score.overall_score:.1f}/100")
    logger.info(f"    - Severity: {score.severity_score.contribution:.2f}")
    logger.info(f"    - Complaints: {score.complaint_score.contribution:.2f}")
    logger.info(f"    - Usage: {score.usage_score.contribution:.2f}")
    logger.info(f"    - Explanation: {score.explanation}")
    
    # Create synthetic low-impact incident
    low_incident = {
        "outage_id": "INC-TEST-002",
        "region": "EMEA-WEST",
        "timestamp": "2026-07-15T12:00:00",
        "severity": "Minor",
        "component": "Switch",
        "status": "Active",
        "duration_minutes": 15,
        "complaint_count": 2,
        "affected_customers": 50,
        "max_escalation": 1,
        "avg_traffic_gbps": 5.0,
        "peak_active_users": 500,
        "peak_utilization": 15.0,
    }
    
    score = scoring.score_incident(low_incident)
    
    assert score.outage_id == "INC-TEST-002"
    assert score.severity == "Minor"
    assert score.overall_score < 30  # Should be low impact
    
    logger.info(f"  ✓ Minor incident scored: {score.overall_score:.1f}/100 (lower than critical)")


def test_incident_ranking():
    """Test ranking of multiple incidents."""
    logger.info("Testing incident ranking...")
    scoring = ScoringService()
    
    # Create multiple incidents with varying severity
    incidents = [
        {
            "outage_id": "INC-RANK-001",
            "region": "US-EAST-01",
            "timestamp": "2026-07-15T10:00:00",
            "severity": "Minor",
            "component": "Switch",
            "status": "Active",
            "duration_minutes": 10,
            "complaint_count": 5,
            "affected_customers": 100,
            "max_escalation": 1,
            "avg_traffic_gbps": 20.0,
            "peak_active_users": 5000,
            "peak_utilization": 25.0,
        },
        {
            "outage_id": "INC-RANK-002",
            "region": "EMEA-WEST",
            "timestamp": "2026-07-15T11:00:00",
            "severity": "Critical",
            "component": "Router",
            "status": "Active",
            "duration_minutes": 120,
            "complaint_count": 80,
            "affected_customers": 4500,
            "max_escalation": 5,
            "avg_traffic_gbps": 400.0,
            "peak_active_users": 85000,
            "peak_utilization": 95.0,
        },
        {
            "outage_id": "INC-RANK-003",
            "region": "ASIA-PAC",
            "timestamp": "2026-07-15T12:00:00",
            "severity": "Major",
            "component": "Cable",
            "status": "Active",
            "duration_minutes": 60,
            "complaint_count": 40,
            "affected_customers": 1200,
            "max_escalation": 3,
            "avg_traffic_gbps": 150.0,
            "peak_active_users": 35000,
            "peak_utilization": 60.0,
        },
    ]
    
    # Score and rank
    ranked = scoring.score_all_incidents(incidents)
    
    assert len(ranked) == 3
    
    # Verify ranking
    for i, incident in enumerate(ranked):
        logger.info(
            f"  Rank {i + 1}: {incident.outage_id} ({incident.severity}) = {incident.overall_score:.1f}/100"
        )
    
    # Verify order (highest to lowest)
    assert ranked[0].overall_score >= ranked[1].overall_score
    assert ranked[1].overall_score >= ranked[2].overall_score
    
    # Verify ranks are set correctly
    assert ranked[0].rank == 1
    assert ranked[1].rank == 2
    assert ranked[2].rank == 3
    
    logger.info("  ✓ Incidents ranked correctly by impact score")


def test_scoring_with_real_data():
    """Test scoring with data from the data pipeline."""
    logger.info("Testing scoring with real data from data pipeline...")
    
    # Initialize data service
    data_service = DataService()
    success, result = data_service.process()
    
    if not success or not result.get("validated"):
        logger.error("Data pipeline validation failed")
        return
    
    # Get processed data
    processed_data = data_service.get_processed_data()
    if not processed_data:
        logger.error("No processed data available")
        return
    
    logger.info(f"  Loaded {len(processed_data)} incidents from data pipeline")
    
    # Initialize scoring service
    scoring = ScoringService()
    
    # Score all incidents
    ranked = scoring.score_all_incidents(processed_data)
    
    logger.info(f"  ✓ Successfully scored {len(ranked)} incidents")
    
    # Display top 3
    if len(ranked) > 0:
        logger.info("\n  Top 3 Highest Impact Incidents:")
        for incident in ranked[:3]:
            logger.info(
                f"    Rank {incident.rank}: {incident.outage_id} ({incident.region}) = {incident.overall_score:.1f}/100"
            )
            logger.info(f"      {incident.explanation}")
    
    # Verify all incidents have valid scores
    for incident in ranked:
        assert 0 <= incident.overall_score <= 100
        assert incident.rank is not None
        assert len(incident.explanation) > 0


def test_explanation_generation():
    """Test explanation text generation."""
    logger.info("Testing explanation generation...")
    scoring = ScoringService()
    
    # Create test incident
    incident = {
        "outage_id": "INC-EXP-001",
        "region": "US-WEST-02",
        "timestamp": "2026-07-15T14:30:00",
        "severity": "Critical",
        "component": "Backbone",
        "status": "Active",
        "duration_minutes": 90,
        "complaint_count": 75,
        "affected_customers": 3800,
        "max_escalation": 4,
        "avg_traffic_gbps": 380.0,
        "peak_active_users": 72000,
        "peak_utilization": 87.5,
    }
    
    score = scoring.score_incident(incident)
    explanation = score.explanation
    
    # Verify explanation contains key information
    assert "CRITICAL" in explanation or "HIGH" in explanation
    assert str(round(score.overall_score, 1)) in explanation or f"{int(score.overall_score)}" in explanation
    assert "severity" in explanation.lower()
    assert "complaints" in explanation.lower()
    
    logger.info(f"  ✓ Explanation generated successfully:")
    logger.info(f"    {explanation}")


def run_all_tests():
    """Run all unit tests."""
    logger.info("=" * 70)
    logger.info("IMPACT SCORING SERVICE - UNIT TESTS")
    logger.info("=" * 70)
    logger.info("")
    
    test_functions = [
        test_severity_score,
        test_complaint_score,
        test_usage_score,
        test_incident_scoring,
        test_incident_ranking,
        test_explanation_generation,
        test_scoring_with_real_data,
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
