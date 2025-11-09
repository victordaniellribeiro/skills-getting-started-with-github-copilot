import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


class TestDataValidation:
    """Test data validation and edge cases."""
    
    def test_email_validation_patterns(self, client):
        """Test various email patterns for signup."""
        valid_emails = [
            "student@mergington.edu",
            "test.email@mergington.edu",
            "student+tag@mergington.edu",
            "123student@mergington.edu"
        ]
        
        for email in valid_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": email}
            )
            # Should either succeed (200) or fail because already registered (400)
            assert response.status_code in [200, 400]
    
    def test_activity_name_with_special_characters(self, client):
        """Test activity names are handled correctly in URLs."""
        # Test with spaces (should work)
        response = client.get("/activities")
        data = response.json()
        
        # Verify activities with spaces exist and can be accessed
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Test URL encoding
        response = client.post(
            "/activities/Chess%20Club/signup",
            data={"email": "urlencoded@mergington.edu"}
        )
        assert response.status_code in [200, 400]  # Success or already registered
    
    def test_empty_and_whitespace_email(self, client):
        """Test handling of empty and whitespace-only emails."""
        invalid_emails = ["", "   ", "\t", "\n"]
        
        for email in invalid_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": email}
            )
            # FastAPI Form(...) accepts empty strings, so we get 200
            # In a real application, you might want additional validation
            assert response.status_code in [200, 400, 422]


class TestDataConsistency:
    """Test data consistency and state management."""
    
    def test_activities_data_integrity(self, client):
        """Test that activities data maintains integrity."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            # Check required fields exist
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            
            # Check data types
            assert isinstance(details["description"], str)
            assert isinstance(details["schedule"], str)
            assert isinstance(details["max_participants"], int)
            assert isinstance(details["participants"], list)
            
            # Check constraints
            assert details["max_participants"] > 0
            assert len(details["description"]) > 0
            assert len(details["schedule"]) > 0
            
            # Check participants are unique
            participants = details["participants"]
            assert len(participants) == len(set(participants))
    
    def test_concurrent_operations_simulation(self, client):
        """Test simulated concurrent operations."""
        test_email = "concurrent.test@mergington.edu"
        activity = "Science Club"
        
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = set(initial_data[activity]["participants"])
        
        # Simulate multiple signup attempts (would be concurrent in real scenario)
        responses = []
        for i in range(3):
            response = client.post(
                f"/activities/{activity}/signup",
                data={"email": test_email}
            )
            responses.append(response)
        
        # First should succeed, others should fail with "already registered"
        success_count = sum(1 for r in responses if r.status_code == 200)
        duplicate_count = sum(1 for r in responses if r.status_code == 400)
        
        assert success_count == 1
        assert duplicate_count == 2
        
        # Verify final state
        response = client.get("/activities")
        final_data = response.json()
        final_participants = set(final_data[activity]["participants"])
        
        # Should have exactly one new participant
        assert len(final_participants) == len(initial_participants) + 1
        assert test_email in final_participants


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_email(self, client):
        """Test handling of very long email addresses."""
        long_email = "a" * 100 + "@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": long_email}
        )
        # Should handle gracefully (either accept or reject with proper error)
        assert response.status_code in [200, 400, 422]
    
    def test_unicode_characters_in_email(self, client):
        """Test handling of unicode characters."""
        unicode_emails = [
            "tëst@mergington.edu",
            "测试@mergington.edu",
            "test@mërgington.edu"
        ]
        
        for email in unicode_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": email}
            )
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]
    
    def test_case_sensitivity_in_emails(self, client):
        """Test case sensitivity handling in email addresses."""
        base_email = "CaseTest@Mergington.EDU"
        lower_email = base_email.lower()
        
        # Sign up with original case
        response1 = client.post(
            "/activities/Art Workshop/signup",
            data={"email": base_email}
        )
        
        # Try to sign up with different case
        response2 = client.post(
            "/activities/Art Workshop/signup",
            data={"email": lower_email}
        )
        
        # At least one should succeed
        assert response1.status_code == 200 or response2.status_code == 200


class TestPerformance:
    """Test performance-related aspects."""
    
    def test_response_times(self, client):
        """Test that API responses are reasonably fast."""
        import time
        
        # Test GET /activities
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
        
        # Test POST signup
        start_time = time.time()
        response = client.post(
            "/activities/Basketball Club/signup",
            data={"email": "performance.test@mergington.edu"}
        )
        end_time = time.time()
        
        assert response.status_code in [200, 400]
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_repeated_requests(self, client):
        """Test handling of repeated requests."""
        # Make multiple requests to ensure stability
        for i in range(10):
            response = client.get("/activities")
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, dict)
            assert len(data) > 0