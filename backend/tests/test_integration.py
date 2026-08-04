"""
Integration tests for Telecom Outage Impact Prioritization System
Tests the complete data flow from ingestion to API response
"""

import pytest
import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.data_service import DataService
from backend.services.scoring_service import ScoringService
from backend.services.anomaly_service import AnomalyDetectionService


@pytest.fixture
def client():
    """Create test client for API"""
    return TestClient(app)


@pytest.fixture
def data_service():
    """Initialize DataService for testing"""
    return DataService()


@pytest.fixture
def scoring_service():
    """Initialize ScoringService for testing"""
    return ScoringService()


@pytest.fixture
def anomaly_service():
    """Initialize AnomalyDetectionService for testing"""
    return AnomalyDetectionService()


class TestDataProcessing:
    """Test complete data processing pipeline"""

    def test_data_ingestion_complete(self, data_service):
        """Test that all data sources are loaded and processed"""
        success, data = data_service.process()
        assert success is True
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert 'incident_id' in data.columns
        assert 'region' in data.columns
        assert 'severity' in data.columns

    def test_data_quality(self, data_service):
        """Test data quality metrics"""
        success, data = data_service.process()
        assert success is True
        
        # Check for null values
        assert data.isnull().sum().sum() == 0, "Data contains null values"
        
        # Check data types
        assert data['incident_id'].dtype == object
        assert data['severity'].dtype == object
        assert data['duration_minutes'].dtype in [int, float]

    def test_data_join_integrity(self, data_service):
        """Test that data joins preserve relationships"""
        success, data = data_service.process()
        assert success is True
        
        # All incidents should have scores and anomalies
        assert data['overall_score'].notna().all()
        assert data['complaint_count'].notna().all()
        assert data['affected_customers'].notna().all()


class TestScoring:
    """Test impact scoring system"""

    def test_scoring_calculation(self, data_service, scoring_service):
        """Test that scores are calculated correctly"""
        success, data = data_service.process()
        assert success is True
        
        # Score all incidents
        scored = scoring_service.score_all_incidents(data)
        assert len(scored) == len(data)
        
        # All incidents should have scores
        for incident in scored:
            assert incident.overall_score > 0
            assert incident.overall_score <= 100
            assert incident.explanation is not None

    def test_scoring_consistency(self, data_service, scoring_service):
        """Test that same incident produces same score"""
        success, data = data_service.process()
        assert success is True
        
        # Score twice
        scores1 = [inc.overall_score for inc in scoring_service.score_all_incidents(data)]
        scores2 = [inc.overall_score for inc in scoring_service.score_all_incidents(data)]
        
        assert scores1 == scores2

    def test_scoring_range(self, data_service, scoring_service):
        """Test that scores are within valid range"""
        success, data = data_service.process()
        assert success is True
        
        scored = scoring_service.score_all_incidents(data)
        
        for incident in scored:
            assert 0 < incident.overall_score <= 100


class TestAnomalyDetection:
    """Test anomaly detection system"""

    def test_anomaly_detection(self, data_service, anomaly_service):
        """Test that anomalies are detected"""
        success, data = data_service.process()
        assert success is True
        
        anomalies = anomaly_service.detect_all_anomalies(data)
        assert anomalies is not None
        assert 'total_anomalies' in anomalies
        assert 'anomalies_by_type' in anomalies

    def test_anomaly_types(self, data_service, anomaly_service):
        """Test that all anomaly types are detected"""
        success, data = data_service.process()
        assert success is True
        
        anomalies = anomaly_service.detect_all_anomalies(data)
        anomaly_types = anomalies['anomalies_by_type']
        
        assert 'complaint_spike' in anomaly_types
        assert 'regional_concentration' in anomaly_types
        assert 'customer_base_anomaly' in anomaly_types
        assert 'high_impact_region' in anomaly_types


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'

    def test_processed_data_endpoint(self, client):
        """Test processed data retrieval"""
        response = client.get("/api/data/processed")
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert 'data' in data or 'message' in data

    def test_ranked_incidents_endpoint(self, client):
        """Test ranked incidents endpoint"""
        response = client.get("/api/incidents/ranked")
        assert response.status_code == 200
        data = response.json()
        assert 'incidents' in data
        assert len(data['incidents']) > 0

    def test_anomalies_endpoint(self, client):
        """Test anomalies endpoint"""
        response = client.get("/api/anomalies")
        assert response.status_code == 200
        data = response.json()
        assert 'anomalies' in data

    def test_data_summary_endpoint(self, client):
        """Test data summary endpoint"""
        response = client.get("/api/data/summary")
        assert response.status_code == 200
        data = response.json()
        assert 'total_incidents' in data
        assert 'total_customers' in data
        assert 'total_regions' in data


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_endpoint(self, client):
        """Test invalid endpoint handling"""
        response = client.get("/api/invalid")
        assert response.status_code == 404

    def test_cors_enabled(self, client):
        """Test CORS headers"""
        response = client.get("/api/health")
        assert 'access-control-allow-origin' in response.headers.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
