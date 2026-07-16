/**
 * API Service for Dashboard
 * 
 * Provides methods to fetch data from backend endpoints
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiService = {
  /**
   * Fetch processed incident data with quality metrics
   */
  async getProcessedData() {
    try {
      const response = await fetch(`${API_URL}/api/processed-data`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching processed data:', error);
      throw error;
    }
  },

  /**
   * Fetch data quality metrics
   */
  async getDataQuality() {
    try {
      const response = await fetch(`${API_URL}/api/data-quality`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching data quality:', error);
      throw error;
    }
  },

  /**
   * Fetch data summary statistics
   */
  async getDataSummary() {
    try {
      const response = await fetch(`${API_URL}/api/data-summary`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching data summary:', error);
      throw error;
    }
  },

  /**
   * Fetch ranked incidents by impact score
   */
  async getRankedIncidents(region = null) {
    try {
      const url = region
        ? `${API_URL}/api/ranked-incidents/${region}`
        : `${API_URL}/api/ranked-incidents`;
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching ranked incidents:', error);
      throw error;
    }
  },

  /**
   * Fetch detected anomalies
   */
  async getAnomalies(filterType = null, filterValue = null) {
    try {
      let url = `${API_URL}/api/anomalies`;
      
      if (filterType === 'severity' && filterValue) {
        url += `/${filterValue}`;
      } else if (filterType === 'region' && filterValue) {
        url += `/region/${filterValue}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      throw error;
    }
  },

  /**
   * Fetch health check
   */
  async getHealth() {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
};
