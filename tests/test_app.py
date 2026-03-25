import pytest
from fastapi import HTTPException


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Should return all available activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) >= 3
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Should include all required fields for each activity"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_returns_participants(self, client, reset_activities):
        """Should return current participants for each activity"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        actual_participants = data["Chess Club"]["participants"]
        
        # Assert
        for participant in expected_participants:
            assert participant in actual_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client, reset_activities):
        """Should successfully sign up a new student"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_email in response.json()["message"]
    
    def test_signup_adds_to_participants_list(self, client, reset_activities):
        """Should add the student to the activity's participant list"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "test@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        response = client.get("/activities")
        actual_participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert new_email in actual_participants
    
    def test_signup_fails_for_nonexistent_activity(self, client, reset_activities):
        """Should return 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_fails_for_duplicate_signup(self, client, reset_activities):
        """Should prevent duplicate signups for the same student"""
        # Arrange
        activity_name = "Chess Club"
        existing_participant = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_participant}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, client, reset_activities):
        """Should handle URL-encoded activity names correctly"""
        # Arrange
        encoded_activity = "Chess%20Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{encoded_activity}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
    
    def test_signup_with_url_encoded_email(self, client, reset_activities):
        """Should handle URL-encoded email addresses"""
        # Arrange
        activity_name = "Chess Club"
        encoded_email = "test%2B1@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={encoded_email}"
        )
        
        # Assert
        assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_successfully(self, client, reset_activities):
        """Should successfully remove a participant"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
    
    def test_remove_participant_removes_from_list(self, client, reset_activities):
        """Should remove the participant from the activity's list"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        response = client.get("/activities")
        actual_participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert email_to_remove not in actual_participants
    
    def test_remove_participant_from_nonexistent_activity(self, client, reset_activities):
        """Should return 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant(self, client, reset_activities):
        """Should return 404 if participant not in activity"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notinactivity@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_with_url_encoded_email(self, client, reset_activities):
        """Should handle URL-encoded email addresses"""
        # Arrange
        activity_name = "Chess Club"
        special_email = "test+1@mergington.edu"
        encoded_email = "test%2B1@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={special_email}")
        response = client.delete(
            f"/activities/{activity_name}/participants/{encoded_email}"
        )
        
        # Assert
        assert response.status_code == 200


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Should redirect to static/index.html"""
        # Arrange
        expected_redirect = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect
