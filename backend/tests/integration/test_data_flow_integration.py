"""
Data Flow Integration Tests
Tests that verify end-to-end data flow between components
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from unittest.mock import Mock, patch

class TestDataFlowIntegration:
    """Test integration between different system components"""
    
    def test_scraper_to_database_flow(self, client, db_session):
        """Test complete data flow from scraper to database"""
        
        # Setup: Mock scraper data
        mock_scraper_data = {
            'bills': [
                {
                    'title': 'Test Bill 1',
                    'description': 'Test Description 1',
                    'bill_number': 'C-001',
                    'introduced_date': '2024-01-01',
                    'sponsor': 'Test Sponsor',
                    'jurisdiction': 'federal'
                }
            ],
            'mps': [
                {
                    'name': 'Test MP 1',
                    'party': 'Test Party',
                    'constituency': 'Test Riding',
                    'jurisdiction': 'federal'
                }
            ]
        }
        
        # Execute: Run scraper and store data
        with patch('scrapers.federal_parliament_scraper.FederalParliamentScraper') as mock_scraper_class:
            mock_scraper = Mock()
            mock_scraper_class.return_value = mock_scraper
            mock_scraper.scrape_all.return_value = mock_scraper_data
            
            # Simulate scraper execution
            from scrapers.federal_parliament_scraper import FederalParliamentScraper
            scraper = FederalParliamentScraper()
            data = scraper.scrape_all()
            
            # Store data in database
            for bill in data['bills']:
                db_session.execute(text("""
                    INSERT INTO bills_bill (title, description, bill_number, introduced_date, sponsor, jurisdiction)
                    VALUES (:title, :description, :bill_number, :introduced_date, :sponsor, :jurisdiction)
                """), bill)
            
            for mp in data['mps']:
                db_session.execute(text("""
                    INSERT INTO politicians_politician (name, party, constituency, jurisdiction)
                    VALUES (:name, :party, :constituency, :jurisdiction)
                """), mp)
            
            db_session.commit()
        
        # Verify: Data is in database
        result = db_session.execute(text("SELECT COUNT(*) FROM bills_bill WHERE bill_number = 'C-001'"))
        bill_count = result.fetchone()[0]
        assert bill_count == 1, "Bill not stored in database"
        
        result = db_session.execute(text("SELECT COUNT(*) FROM politicians_politician WHERE name = 'Test MP 1'"))
        mp_count = result.fetchone()[0]
        assert mp_count == 1, "MP not stored in database"
    
    def test_database_to_api_flow(self, client, db_session):
        """Test data flow from database to API"""
        
        # Setup: Insert test data in database
        db_session.execute(text("""
            INSERT INTO bills_bill (title, description, bill_number, introduced_date, sponsor, jurisdiction)
            VALUES ('Test Bill 1', 'Test Description 1', 'C-001', '2024-01-01', 'Test Sponsor', 'federal')
        """))
        
        db_session.execute(text("""
            INSERT INTO politicians_politician (name, party, constituency, jurisdiction)
            VALUES ('Test MP 1', 'Test Party', 'Test Riding', 'federal')
        """))
        
        db_session.commit()
        
        # Execute: Query data through API
        response = client.get("/api/policies")
        
        # Verify: API returns data from database
        assert response.status_code == 200
        data = response.json()
        assert "bills" in data
        assert len(data["bills"]) >= 1
        
        # Find our test bill
        test_bill = None
        for bill in data["bills"]:
            if bill["bill_number"] == "C-001":
                test_bill = bill
                break
        
        assert test_bill is not None, "Test bill not found in API response"
        assert test_bill["title"] == "Test Bill 1"
        assert test_bill["sponsor"] == "Test Sponsor"
        
        # Test representatives API
        response = client.get("/api/representatives")
        
        # Verify: API returns representative data
        assert response.status_code == 200
        data = response.json()
        assert "representatives" in data
        assert len(data["representatives"]) >= 1
        
        # Find our test MP
        test_mp = None
        for mp in data["representatives"]:
            if mp["name"] == "Test MP 1":
                test_mp = mp
                break
        
        assert test_mp is not None, "Test MP not found in API response"
        assert test_mp["party"] == "Test Party"
        assert test_mp["constituency"] == "Test Riding"
    
    def test_api_to_frontend_flow(self, client, db_session):
        """Test data flow from API to frontend"""
        
        # Setup: Insert test data and create authenticated user
        db_session.execute(text("""
            INSERT INTO bills_bill (title, description, bill_number, introduced_date, sponsor, jurisdiction)
            VALUES ('Test Bill 1', 'Test Description 1', 'C-001', '2024-01-01', 'Test Sponsor', 'federal')
        """))
        
        db_session.execute(text("""
            INSERT INTO auth_user (username, email, password, is_active, is_staff)
            VALUES ('testuser', 'test@example.com', 'hashed_password', true, false)
        """))
        
        db_session.commit()
        
        # Execute: Login to get authentication token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        access_token = token_data["access_token"]
        
        # Execute: Access frontend endpoints with authentication
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test bills page data
        response = client.get("/api/policies", headers=headers)
        assert response.status_code == 200
        bills_data = response.json()
        
        # Test search functionality
        search_data = {
            "query": "Test Bill",
            "jurisdiction": "federal"
        }
        
        response = client.post("/api/policies/search", json=search_data, headers=headers)
        assert response.status_code == 200
        search_results = response.json()
        
        # Verify: Search returns relevant results
        assert "results" in search_results
        assert len(search_results["results"]) >= 1
        
        # Test filtering functionality
        filter_data = {
            "jurisdiction": "federal",
            "status": "introduced"
        }
        
        response = client.post("/api/policies/filter", json=filter_data, headers=headers)
        assert response.status_code == 200
        filter_results = response.json()
        
        # Verify: Filter returns relevant results
        assert "results" in filter_results
        assert len(filter_results["results"]) >= 1
    
    def test_user_input_validation_flow(self, client, db_session):
        """Test user input validation throughout the system"""
        
        # Setup: Create test user
        db_session.execute(text("""
            INSERT INTO auth_user (username, email, password, is_active, is_staff)
            VALUES ('testuser', 'test@example.com', 'hashed_password', true, false)
        """))
        db_session.commit()
        
        # Execute: Test invalid login input
        invalid_login_data = {
            "username": "",  # Empty username
            "password": "short"  # Short password
        }
        
        response = client.post("/api/auth/login", json=invalid_login_data)
        
        # Verify: Input validation catches errors
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
        
        # Execute: Test invalid bill creation
        invalid_bill_data = {
            "title": "",  # Empty title
            "bill_number": "invalid",  # Invalid bill number format
            "jurisdiction": "invalid_jurisdiction"  # Invalid jurisdiction
        }
        
        response = client.post("/api/policies", json=invalid_bill_data)
        
        # Verify: Input validation catches errors
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Execute: Test valid input
        valid_bill_data = {
            "title": "Valid Bill Title",
            "description": "Valid description",
            "bill_number": "C-123",
            "introduced_date": "2024-01-01",
            "sponsor": "Valid Sponsor",
            "jurisdiction": "federal"
        }
        
        response = client.post("/api/policies", json=valid_bill_data)
        
        # Verify: Valid input is accepted
        assert response.status_code in [200, 201]
        
        # Verify: Data is stored correctly
        result = db_session.execute(text("""
            SELECT title, bill_number, jurisdiction 
            FROM bills_bill 
            WHERE bill_number = 'C-123'
        """))
        bill = result.fetchone()
        assert bill is not None
        assert bill.title == "Valid Bill Title"
        assert bill.jurisdiction == "federal"
    
    def test_error_handling_flow(self, client, db_session):
        """Test error handling throughout the system"""
        
        # Setup: Create test user
        db_session.execute(text("""
            INSERT INTO auth_user (username, email, password, is_active, is_staff)
            VALUES ('testuser', 'test@example.com', 'hashed_password', true, false)
        """))
        db_session.commit()
        
        # Execute: Test database connection error
        with patch('sqlalchemy.orm.Session.execute') as mock_execute:
            mock_execute.side_effect = Exception("Database connection error")
            
            response = client.get("/api/policies")
            
            # Verify: Error is handled gracefully
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Internal server error" in data["detail"]
        
        # Execute: Test authentication error
        invalid_token = "invalid_token"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        # Verify: Authentication error is handled
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid token" in data["detail"]
        
        # Execute: Test rate limiting
        for i in range(100):  # Make many requests
            response = client.get("/api/policies")
        
        # Verify: Rate limiting is enforced
        if response.status_code == 429:  # Rate limit exceeded
            data = response.json()
            assert "detail" in data
            assert "rate limit" in data["detail"].lower()
        
        # Execute: Test validation error
        invalid_data = {
            "invalid_field": "invalid_value"
        }
        
        response = client.post("/api/policies", json=invalid_data)
        
        # Verify: Validation error is handled
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Execute: Test not found error
        response = client.get("/api/policies/999999")  # Non-existent ID
        
        # Verify: Not found error is handled
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
