"""Tests for the Mergington High School Activities API"""

import pytest


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that getting activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that getting activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_required_activities(self, client):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Basketball Team",
            "Tennis Club",
            "Programming Class",
            "Debate Club",
            "Science Olympiad",
            "Drama Club",
            "Painting & Drawing",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(activity_data.keys())
    
    def test_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200(self, client):
        """Test that signup returns a 200 status code"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        test_email = "newstudent@mergington.edu"
        
        # Get activities before signup
        activities_before = client.get("/activities").json()
        participants_before = activities_before["Basketball Team"]["participants"].copy()
        
        # Signup
        response = client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Get activities after signup
        activities_after = client.get("/activities").json()
        participants_after = activities_after["Basketball Team"]["participants"]
        
        # Verify participant was added
        assert test_email in participants_after
        assert len(participants_after) == len(participants_before) + 1
    
    def test_signup_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Basketball Team/signup?email=test2@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "test2@mergington.edu" in data["message"]
    
    def test_signup_duplicate_email_fails(self, client):
        """Test that signing up with same email twice returns 400"""
        test_email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200(self, client):
        """Test that unregister returns a 200 status code"""
        test_email = "unreg@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        
        # Then unregister
        response = client.post(
            f"/activities/Basketball Team/unregister?email={test_email}"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        test_email = "remove@mergington.edu"
        
        # Signup
        client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        
        # Verify participant was added
        activities_before = client.get("/activities").json()
        assert test_email in activities_before["Basketball Team"]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/Basketball Team/unregister?email={test_email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert test_email not in activities_after["Basketball Team"]["participants"]
    
    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns a success message"""
        test_email = "msg@mergington.edu"
        
        # Signup
        client.post(
            f"/activities/Basketball Team/signup?email={test_email}"
        )
        
        # Unregister
        response = client.post(
            f"/activities/Basketball Team/unregister?email={test_email}"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonregistered_email_fails(self, client):
        """Test that unregistering non-registered email returns 400"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
