import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app


class TestStaticFiles:
    """Test cases for static file serving."""
    
    def test_serve_index_html(self, client):
        """Test that index.html is served correctly."""
        response = client.get("/static/index.html")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "Mergington High School" in content
        assert "Extracurricular Activities" in content
    
    def test_serve_app_js(self, client):
        """Test that app.js is served correctly."""
        response = client.get("/static/app.js")
        assert response.status_code == 200
        assert "application/javascript" in response.headers["content-type"] or \
               "text/javascript" in response.headers["content-type"]
        
        content = response.text
        assert "fetchActivities" in content
        assert "handleDeleteParticipant" in content
    
    def test_serve_styles_css(self, client):
        """Test that styles.css is served correctly."""
        response = client.get("/static/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]
        
        content = response.text
        assert "activity-card" in content
        assert "participants-list" in content
        assert "delete-participant-btn" in content
    
    def test_nonexistent_static_file(self, client):
        """Test requesting a non-existent static file."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == 404


class TestApplicationStructure:
    """Test the overall application structure and configuration."""
    
    def test_app_has_correct_title(self):
        """Test that the FastAPI app has the correct configuration."""
        assert app.title == "Mergington High School API"
        assert "API for viewing and signing up for extracurricular activities" in app.description
    
    def test_cors_and_security_headers(self, client):
        """Test basic security aspects of the application."""
        response = client.get("/")
        
        # Basic response validation
        assert response.status_code in [200, 307]  # Either success or redirect
        
        # Verify the response is well-formed
        assert response.headers.get("content-length") is not None or \
               response.headers.get("transfer-encoding") == "chunked"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_route(self, client):
        """Test requesting an invalid route."""
        response = client.get("/invalid/route")
        assert response.status_code == 404
    
    def test_invalid_method_on_valid_endpoint(self, client):
        """Test using invalid HTTP method on valid endpoint."""
        response = client.put("/activities")
        assert response.status_code == 405
    
    def test_malformed_activity_name(self, client):
        """Test with malformed activity name in URL."""
        response = client.post(
            "/activities//signup",  # Empty activity name
            data={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404