import pytest


def test_root_redirect(client):
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9
    
    # Check structure of an activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_for_activity(client, reset_activities):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Basketball%20Team/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]


def test_signup_activity_not_found(client):
    """Test signing up for non-existent activity"""
    response = client.post(
        "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_already_registered(client, reset_activities):
    """Test signing up for activity when already registered"""
    # First signup should succeed
    response1 = client.post(
        "/activities/Chess%20Club/signup?email=test@mergington.edu"
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Chess%20Club/signup?email=test@mergington.edu"
    )
    assert response2.status_code == 400
    assert "already" in response2.json()["detail"].lower()


def test_unregister_from_activity(client, reset_activities):
    """Test unregistering a participant from an activity"""
    # First, sign up
    signup_response = client.post(
        "/activities/Basketball%20Team/signup?email=test@mergington.edu"
    )
    assert signup_response.status_code == 200
    
    # Then unregister
    response = client.delete(
        "/activities/Basketball%20Team/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]
    
    # Verify participant is removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "test@mergington.edu" not in activities_data["Basketball Team"]["participants"]


def test_unregister_not_found(client):
    """Test unregistering from non-existent activity"""
    response = client.delete(
        "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_not_registered(client, reset_activities):
    """Test unregistering when not registered for activity"""
    response = client.delete(
        "/activities/Basketball%20Team/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_participant_capacity(client, reset_activities):
    """Test that participant count is tracked correctly"""
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    chess = activities_data["Chess Club"]
    # Chess Club has 2 participants initially
    assert len(chess["participants"]) == 2
    assert "michael@mergington.edu" in chess["participants"]
    assert "daniel@mergington.edu" in chess["participants"]


def test_unregister_existing_participant(client, reset_activities):
    """Test unregistering an existing participant"""
    # First verify michael is in Chess Club
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    # Unregister michael
    response = client.delete(
        "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    # Verify michael is removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
