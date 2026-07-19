def test_landing_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Smart Face Recognition' in response.data or b'FaceAttend' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_login_success(client, app, db):
    response = client.post('/login', data={'username': 'testadmin', 'password': 'testpass'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_failure(client):
    response = client.post('/login', data={'username': 'testadmin', 'password': 'wrong'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    # Should redirect to login
    assert b'Please log in to access this page' in response.data

def test_dashboard_accessible_when_logged_in(auth_client):
    response = auth_client.get('/dashboard')
    assert response.status_code == 200

def test_students_list(auth_client):
    response = auth_client.get('/students')
    assert response.status_code == 200

def test_settings_page(auth_client):
    response = auth_client.get('/settings')
    assert response.status_code == 200
