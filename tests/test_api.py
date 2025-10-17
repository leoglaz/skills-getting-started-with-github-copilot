"""
Tests for the Mergington High School Activities API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client, reset_activities):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoints."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Club", "Drama Society", "Math Olympiad", "Science Club"
        ]
        
        for activity_name in expected_activities:
            assert activity_name in data
            activity = data[activity_name]
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
            assert isinstance(activity["max_participants"], int)
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test the structure of activity data."""
        response = client.get("/activities")
        data = response.json()
        
        # Test Chess Club specifically
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test the signup functionality."""
    
    def test_signup_for_existing_activity_success(self, client, reset_activities):
        """Test successful signup for an existing activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity."""
        # Try to sign up a student who is already registered
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_at_capacity(self, client, reset_activities):
        """Test signup when activity is at full capacity."""
        # Fill up Math Olympiad (max 10 participants, currently has 2)
        for i in range(8):  # Add 8 more to reach capacity
            response = client.post(
                f"/activities/Math Olympiad/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Now try to add one more (should fail)
        response = client.post(
            "/activities/Math Olympiad/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Activity is at full capacity"
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities."""
        email = "multistudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister functionality."""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test successful unregistration of an existing participant."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]  # Other participant should remain
    
    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from a non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_participant(self, client, reset_activities):
        """Test unregistration of a student who is not registered."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test the complete workflow of signing up and then unregistering."""
        email = "workflow@mergington.edu"
        activity = "Art Club"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then, unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_activity_name_with_spaces_and_special_chars(self, client, reset_activities):
        """Test handling of activity names with spaces."""
        # Chess Club has a space in the name
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_email_formats(self, client, reset_activities):
        """Test various email formats."""
        valid_emails = [
            "test@mergington.edu",
            "test.student@mergington.edu",
            "test_student@mergington.edu",
            "test-student@mergington.edu",
            "test123@mergington.edu"
        ]
        
        for i, email in enumerate(valid_emails):
            response = client.post(
                f"/activities/Programming Class/signup?email={email}"
            )
            # Each should succeed as they're all different emails
            assert response.status_code == 200, f"Failed for email: {email}"
    
    def test_case_sensitivity_activity_names(self, client, reset_activities):
        """Test that activity names are case sensitive."""
        # This should fail because "chess club" != "Chess Club"
        response = client.post(
            "/activities/chess club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404