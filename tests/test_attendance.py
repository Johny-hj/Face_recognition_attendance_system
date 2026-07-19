def test_attendance_list_requires_login(client):
    response = client.get('/attendance')
    assert response.status_code == 308 or response.status_code == 302 # redirect to login

def test_attendance_list_accessible(auth_client):
    response = auth_client.get('/attendance/')
    assert response.status_code == 200
    assert b'Attendance' in response.data

def test_attendance_camera_accessible(auth_client):
    response = auth_client.get('/attendance/start')
    assert response.status_code == 200
    assert b'Face Recognition' in response.data

def test_attendance_download(auth_client):
    response = auth_client.get('/attendance/download')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'attachment' in response.headers['Content-Disposition']

def test_attendance_export(auth_client):
    response = auth_client.get('/attendance/export?type=today&format=csv')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    assert 'attachment' in response.headers['Content-Disposition']
