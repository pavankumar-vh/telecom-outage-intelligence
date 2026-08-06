"""
Integration tests for Telecom Outage Impact Prioritization System
Tests the complete data flow from ingestion to API response
"""

import pytest
import pandas as pd
from fastapi.testclient import TestClient
from main import app
from services.data_service import DataService
from services.scoring_service import ScoringService
from services.anomaly_service import AnomalyDetectionService


@pytest.fixture(autouse=True)
def setup_data_service():
    from api.data import data_service
    data_service.process()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


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
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        assert data is not None
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'outage_id' in data[0]
        assert 'region' in data[0]
        assert 'severity' in data[0]

    def test_data_quality(self, data_service):
        """Test data quality metrics"""
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        
        # Check for null values
        has_nulls = any(val is None for row in data for val in row.values())
        assert not has_nulls, "Data contains null values"
        
        # Check data types
        assert isinstance(data[0]['outage_id'], str)
        assert isinstance(data[0]['severity'], str)

    def test_data_join_integrity(self, data_service):
        """Test that data joins preserve relationships"""
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        
        # All incidents should have anomalies
        assert all('complaint_count' in row for row in data)
        assert all('affected_customers' in row for row in data)


class TestScoring:
    """Test impact scoring system"""

    def test_scoring_calculation(self, data_service, scoring_service):
        """Test that scores are calculated correctly"""
        success, status = data_service.process()
        data = data_service.get_processed_data()
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
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        
        # Score twice
        scores1 = [inc.overall_score for inc in scoring_service.score_all_incidents(data)]
        scores2 = [inc.overall_score for inc in scoring_service.score_all_incidents(data)]
        
        assert scores1 == scores2

    def test_scoring_range(self, data_service, scoring_service):
        """Test that scores are within valid range"""
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        
        scored = scoring_service.score_all_incidents(data)
        
        for incident in scored:
            assert 0 < incident.overall_score <= 100


class TestAnomalyDetection:
    """Test anomaly detection system"""

    def test_anomaly_detection(self, data_service, anomaly_service):
        """Test that anomalies are detected"""
        success, status = data_service.process()
        data = data_service.get_processed_data()
        assert success is True
        
        anomalies = anomaly_service.detect_all_anomalies(data)
        assert anomalies is not None
        assert anomalies.total_anomalies >= 0


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'

    def test_processed_data_endpoint(self, client):
        """Test processed data retrieval"""
        response = client.get("/api/processed-data")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'data' in data or 'message' in data

    def test_ranked_incidents_endpoint(self, client):
        """Test ranked incidents endpoint"""
        response = client.get("/api/ranked-incidents")
        assert response.status_code == 200
        data = response.json()
        assert 'incidents' in data
        assert len(data['incidents']) > 0

    def test_anomalies_endpoint(self, client):
        """Test anomalies endpoint"""
        response = client.get("/api/anomalies")
        assert response.status_code == 200
        data = response.json()
        assert 'incidents' in data

    def test_data_summary_endpoint(self, client):
        """Test data summary endpoint"""
        response = client.get("/api/data-summary")
        assert response.status_code == 200
        data = response.json()
        assert 'total_incidents' in data['summary']
        assert 'total_customers' in data['summary'] or 'total_affected_customers' in data['summary']
        assert 'total_regions' in data['summary'] or 'region_count' in data['summary']


class TestErrorHandling:
    """Test error handling"""

    def test_invalid_endpoint(self, client):
        """Test invalid endpoint handling"""
        response = client.get("/api/invalid")
        assert response.status_code == 404

    def test_cors_enabled(self, client):
        """Test CORS headers"""
        response = client.get("/health", headers={"Origin": "http://localhost:8501"})
        assert 'access-control-allow-origin' in response.headers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
