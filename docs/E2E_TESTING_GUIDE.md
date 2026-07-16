# End-to-End Testing Guide

## Overview
This guide covers comprehensive testing of the Telecom Outage Impact Prioritization System across all phases.

## Testing Strategy

### 1. Unit Testing
**Backend:** Test individual service methods
**Frontend:** Test component rendering and state management

```bash
# Run backend unit tests
cd backend
python -m pytest tests/ -v

# Run frontend unit tests
cd frontend
npm test
```

### 2. Integration Testing
**Test complete data flow from ingestion to API response**

```bash
# Run integration tests
cd backend
python -m pytest tests/test_integration.py -v
```

### 3. End-to-End Testing
**Test complete user workflows**

#### Workflow 1: Dashboard Access
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Verify:
   - ✅ KPI cards load with correct metrics
   - ✅ Incident table displays data
   - ✅ Charts render correctly
   - ✅ Filters respond to user input
   - ✅ Auto-refresh updates every 30 seconds

#### Workflow 2: Search & Filter
1. On dashboard, type in search box: "NYC"
2. Verify:
   - ✅ Table filters in real-time
   - ✅ Results show only NYC incidents
   - ✅ Result count updates
3. Clear search with X button
4. Verify:
   - ✅ All incidents reappear

#### Workflow 3: Sort & Pagination
1. Click "Impact Score" column header
2. Verify:
   - ✅ Column sorts ascending/descending
   - ✅ Arrow indicator shows direction
   - ✅ Data re-orders correctly
3. Navigate pagination:
   - Click page 2
   - Verify: ✅ Shows next 10 items
   - Click "Next"
   - Verify: ✅ Pagination advances

#### Workflow 4: Incident Detail Drill-down
1. Click "View Full Details" on any incident
2. Verify page loads with:
   - ✅ Incident header (ID, region, severity)
   - ✅ Scoring breakdown chart
   - ✅ Complaint progression chart
   - ✅ Impact metrics visualization
   - ✅ Timeline with events
   - ✅ Related incidents list
3. Click related incident
4. Verify: ✅ Detail updates for new incident

#### Workflow 5: Regional View
1. On dashboard, filter to specific region
2. Click "View Regional Analysis"
3. Verify regional page shows:
   - ✅ Region selector
   - ✅ Region-specific KPI cards
   - ✅ Severity distribution
   - ✅ Component breakdown
   - ✅ Regional statistics

#### Workflow 6: Error Handling
1. Stop backend API
2. On dashboard, click refresh
3. Verify:
   - ✅ Error boundary catches error
   - ✅ Error message displays
   - ✅ "Go Home" button visible
   - ✅ "Refresh" button visible
4. Click "Refresh"
5. Verify: ✅ Retry logic attempts connection

#### Workflow 7: CSV Export
1. On dashboard, apply filters
2. Click "Export as CSV"
3. Verify:
   - ✅ File downloads
   - ✅ Filename includes date
   - ✅ File contains filtered incidents
   - ✅ All 8 columns present with headers

#### Workflow 8: Loading States
1. Start backend with artificial delay (add `time.sleep(2)` in API)
2. Refresh dashboard
3. Verify loading states appear:
   - ✅ KPI card skeletons
   - ✅ Table row skeletons
   - ✅ Chart skeletons
4. Verify loading completes and data appears

### 4. Performance Testing

#### Load Time Targets
```
First Contentful Paint:     < 1.5s
Largest Contentful Paint:   < 2.5s
Time to Interactive:        < 3.5s
Cumulative Layout Shift:    < 0.1
Bundle Size (gzipped):      < 200KB
```

#### Measure Performance
```bash
# Using Lighthouse
npm install -g lighthouse
lighthouse http://localhost:5173 --view

# Using WebPageTest
# Visit: https://www.webpagetest.org
# Test URL: http://localhost:5173
```

### 5. API Testing

#### Health Check
```bash
curl http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

#### Data Endpoints
```bash
# Processed data
curl http://localhost:8000/api/data/processed

# Ranked incidents
curl http://localhost:8000/api/incidents/ranked

# Anomalies
curl http://localhost:8000/api/anomalies

# Data summary
curl http://localhost:8000/api/data/summary
```

#### CORS Testing
```bash
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     http://localhost:8000/api/health -v
# Check for CORS headers in response
```

### 6. Browser Testing

#### Desktop Browsers
- [ ] Chrome/Chromium (Latest)
- [ ] Firefox (Latest)
- [ ] Safari (Latest)
- [ ] Edge (Latest)

#### Responsive Design
- [ ] Mobile (375px width)
- [ ] Tablet (768px width)
- [ ] Desktop (1920px width)
- [ ] Ultra-wide (2560px width)

#### Browser Features
- [ ] Local Storage (filter persistence)
- [ ] Fetch API (data loading)
- [ ] SVG rendering (charts)
- [ ] CSS Grid/Flexbox (layout)

### 7. Data Quality Testing

#### Verify Data Integrity
1. Check row counts match across endpoints
2. Verify no duplicate incidents
3. Check all required fields present
4. Validate score calculations
5. Test anomaly detection accuracy

```bash
# Sample data validation script
python scripts/validate_data.py
```

### 8. Security Testing

#### Checklist
- [ ] No sensitive data in logs
- [ ] API auth tokens secure (if applicable)
- [ ] CORS properly configured
- [ ] Input validation on all forms
- [ ] No XSS vulnerabilities (use React escaping)
- [ ] HTTPS enforced in production
- [ ] API rate limiting configured
- [ ] Error messages don't leak details

### 9. Regression Testing

After each code change:
1. Run all unit tests
2. Run integration tests
3. Test critical workflows (1-7 above)
4. Verify performance hasn't degraded
5. Check no visual regressions

### 10. Deployment Testing

#### Staging Environment
1. Deploy to staging
2. Run full E2E test suite
3. Performance testing
4. Load testing
5. Backup/restore testing
6. Monitoring verification

#### Production Pre-flight
```bash
# Final checks before production
python scripts/pre-flight-check.py
```

## Test Results Checklist

Use this checklist to track test completion:

```
Phase 1: Data Processing
[ ] ETL pipeline loads all CSV files
[ ] Data joins succeed with 100% success rate
[ ] 9,000+ customer records processed
[ ] No null values in critical fields

Phase 2: API Functionality
[ ] Health endpoint responds
[ ] All 8 endpoints return correct data
[ ] CORS headers present
[ ] Error responses proper format

Phase 3: Frontend Rendering
[ ] Dashboard loads without errors
[ ] KPI cards display metrics
[ ] Charts render correctly
[ ] Responsive layout works

Phase 4: User Interactions
[ ] Filters work correctly
[ ] Search finds incidents
[ ] Sorting functions properly
[ ] Pagination navigates correctly
[ ] CSV export downloads file

Phase 5: Detail Views
[ ] Incident detail loads
[ ] Timeline displays
[ ] Charts render
[ ] Related incidents link
[ ] Back navigation works

Phase 6: Error Scenarios
[ ] Network error handled gracefully
[ ] Missing data shows empty state
[ ] Invalid route shows 404
[ ] Error boundary catches crashes

Phase 7: Performance
[ ] Page loads < 3s
[ ] Interactions < 500ms
[ ] Bundle size < 200KB
[ ] No layout shifts
[ ] Smooth animations

Phase 8: Production Readiness
[ ] All tests passing
[ ] No console errors
[ ] No memory leaks
[ ] Monitoring configured
[ ] Documentation complete
```

## Continuous Integration

Configure CI/CD pipeline to run tests on every push:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Backend Tests
        run: cd backend && python -m pytest
      - name: Frontend Tests
        run: cd frontend && npm test
      - name: Build Frontend
        run: cd frontend && npm run build
      - name: Performance Check
        run: python scripts/performance-check.py
```

## Sign-off Template

```
E2E Testing Complete
Date: _______________
Tester: ______________

All workflows tested:    ✅ Yes  ☐ No
All performance targets: ✅ Yes  ☐ No
All browsers tested:     ✅ Yes  ☐ No
Security checklist:      ✅ Yes  ☐ No
Data quality verified:   ✅ Yes  ☐ No

Issues Found: _______________________

Approved for Production: ✅ Yes  ☐ No
Signature: ______________________
```

## Rollback Procedure

If issues found in production:

1. Switch traffic back to previous version
2. Investigate root cause
3. Create hotfix branch
4. Test thoroughly
5. Re-deploy

```bash
# Rollback to previous version
git revert <commit-hash>
git push
# Redeploy with new image tag
```
