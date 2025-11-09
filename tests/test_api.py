import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", 
                             "Soccer Team", "Basketball Club", "Art Workshop", 
                             "Drama Club", "Math Olympiad", "Science Club"]
        
        for activity_name in expected_activities:
            assert activity_name in data
            
        # Verify structure of each activity
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct data structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Test a specific activity structure
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test cases for the activity signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        # First, get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = len(initial_data["Chess Club"]["participants"])
        
        # Sign up a new participant
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
        
        # Verify participant was added
        response = client.get("/activities")
        updated_data = response.json()
        updated_participants = updated_data["Chess Club"]["participants"]
        
        assert len(updated_participants) == initial_participants + 1
        assert "newstudent@mergington.edu" in updated_participants
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            data={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 404
        error = response.json()
        assert error["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant(self, client):
        """Test signup when participant is already registered."""
        # Get an existing participant
        response = client.get("/activities")
        data = response.json()
        existing_email = data["Chess Club"]["participants"][0]
        
        # Try to sign up the same participant
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": existing_email}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert error["detail"] == "Student already signed up for this activity"
    
    def test_signup_missing_email(self, client):
        """Test signup without providing email."""
        response = client.post(
            "/activities/Chess Club/signup",
            data={}
        )
        
        assert response.status_code == 422
    
    def test_signup_url_encoded_activity_name(self, client):
        """Test signup with URL-encoded activity name."""
        response = client.post(
            "/activities/Programming%20Class/signup",
            data={"email": "programmer@mergington.edu"}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "Programming Class" in result["message"]


class TestDeleteParticipantEndpoint:
    """Test cases for the delete participant endpoint."""
    
    def test_delete_participant_success(self, client):
        """Test successful removal of a participant."""
        # First add a participant to remove
        client.post(
            "/activities/Chess Club/signup",
            data={"email": "temporary@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "temporary@mergington.edu" in data["Chess Club"]["participants"]
        
        # Remove the participant
        response = client.delete("/activities/Chess Club/participants/temporary@mergington.edu")
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "temporary@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        assert "temporary@mergington.edu" not in updated_data["Chess Club"]["participants"]
    
    def test_delete_participant_activity_not_found(self, client):
        """Test deletion from non-existent activity."""
        response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
        
        assert response.status_code == 404
        error = response.json()
        assert error["detail"] == "Activity not found"
    
    def test_delete_participant_not_found(self, client):
        """Test deletion of non-existent participant."""
        response = client.delete("/activities/Chess Club/participants/nonexistent@mergington.edu")
        
        assert response.status_code == 404
        error = response.json()
        assert error["detail"] == "Participant not found in this activity"
    
    def test_delete_participant_url_encoded(self, client):
        """Test deletion with URL-encoded email and activity name."""
        # Add a participant first
        test_email = "test+user@mergington.edu"
        client.post(
            "/activities/Programming Class/signup",
            data={"email": test_email}
        )
        
        # Delete with URL encoding
        response = client.delete("/activities/Programming%20Class/participants/test%2Buser%40mergington.edu")
        
        assert response.status_code == 200
        result = response.json()
        assert test_email in result["message"]


class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_complete_workflow(self, client):
        """Test a complete signup and removal workflow."""
        activity_name = "Art Workshop"
        test_email = "integration.test@mergington.edu"
        
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": test_email}
        )
        assert response.status_code == 200
        
        # Verify addition
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == initial_count + 1
        assert test_email in data[activity_name]["participants"]
        
        # Remove participant
        response = client.delete(f"/activities/{activity_name}/participants/{test_email}")
        assert response.status_code == 200
        
        # Verify removal
        response = client.get("/activities")
        final_data = response.json()
        assert len(final_data[activity_name]["participants"]) == initial_count
        assert test_email not in final_data[activity_name]["participants"]
    
    def test_multiple_signups_different_activities(self, client):
        """Test signing up the same email for different activities."""
        test_email = "multi.activity@mergington.edu"
        activities_to_test = ["Chess Club", "Programming Class"]
        
        for activity in activities_to_test:
            response = client.post(
                f"/activities/{activity}/signup",
                data={"email": test_email}
            )
            assert response.status_code == 200
        
        # Verify participant is in both activities
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities_to_test:
            assert test_email in data[activity]["participants"]
    
    def test_capacity_constraints(self, client):
        """Test that we can track participants correctly against capacity."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            participant_count = len(details["participants"])
            max_participants = details["max_participants"]
            
            # Verify we're not over capacity
            assert participant_count <= max_participants
            
            # Verify data types
            assert isinstance(participant_count, int)
            assert isinstance(max_participants, int)
            assert max_participants > 0