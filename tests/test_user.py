import pytest, os, asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.constants import errorMessages
from src.database import get_db, engine, Base
from tests import test_auth

valid_user_active_admin = test_auth.valid_user_active_admin
valid_user_active_user = test_auth.valid_user_active_user
duplicated_user = test_auth.duplicated_user
valid_user_not_active = test_auth.valid_user_not_active
invalid_connection = test_auth.invalid_connection
invalid_pass_length = test_auth.invalid_pass_length
invalid_pass = test_auth.invalid_pass
valid_user_to_be_deleted = test_auth.valid_user_to_be_deleted

total_registed_users = test_auth.total_registed_users

client = TestClient(app)

class TestUser: 
  
  @pytest.fixture(scope="session", autouse=True)
  def setup(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}

    # Get Users - Sem Filtro
    response = client.get("/api/users/", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == total_registed_users
    assert response.headers['x-total-count'] == str(total_registed_users)
    
    # Get Users - Offset
    response = client.get("/api/users/?offset=1", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 4
    assert response.headers['x-total-count'] == str(total_registed_users)
    
    # Get Users - Limit
    response = client.get("/api/users/?limit=1", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert response.headers['x-total-count'] == str(total_registed_users)
    
    # Get Users - Filtrar Name
    response = client.get(f"/api/users/?name={valid_user_active_admin['name']}", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == valid_user_active_admin['name']
    assert data[0]['email'] == valid_user_active_admin['email']
    assert data[0]['connection'] == valid_user_active_admin['connection']
    assert response.headers['x-total-count'] == '1'
    
    # Get Users - Filtrar Email
    response = client.get(f"/api/users/?email={valid_user_active_admin['email']}", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == valid_user_active_admin['name']
    assert data[0]['email'] == valid_user_active_admin['email']
    assert data[0]['connection'] == valid_user_active_admin['connection']
    assert response.headers['x-total-count'] == '1'    
    
    # Get Users - Filtrar Name ou Email
    response = client.get(f"/api/users/?name_or_email={valid_user_active_admin['name'][0:2]}", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == valid_user_active_admin['name']
    assert data[0]['email'] == valid_user_active_admin['email']
    assert data[0]['connection'] == valid_user_active_admin['connection']
    assert response.headers['x-total-count'] == '1'
  
    # Get Users - Filtrar Connection
    response = client.get(f"/api/users/?connection=PROFESSOR", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert response.headers['x-total-count'] == '1'
        
  # Read User
  def test_user_read_user_not_found(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.get("/api/users/10", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_user_read_user_by_email_not_found(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.get(f"/api/users/email/{invalid_connection['email']}", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_user_read_user(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.get("/api/users/1", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_active_admin['name']
    assert data['connection'] == valid_user_active_admin['connection']
    assert data['email'] == valid_user_active_admin['email']
    assert data['is_active'] == True
    
  def test_user_read_user_by_email(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.get(f"/api/users/email/{valid_user_active_admin['email']}", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_active_admin['name']
    assert data['connection'] == valid_user_active_admin['connection']
    assert data['email'] == valid_user_active_admin['email']
    
  # Partial Update User
  def test_user_partial_update_user_invalid_connection(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/1", json={"name": "NameZ", "email": "valid@email.com", "connection": "INVALIDO"}, headers=headers)
    data = response.json()
    
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_CONNECTION
  
  def test_user_partial_update_user_not_found(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/10", json=valid_user_active_admin, headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_user_partial_update_user_already_registered_email(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/1", json={"email": valid_user_not_active['email']}, headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.EMAIL_ALREADY_REGISTERED
  
  def test_user_partial_update_user(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/1", json={"name": "NameZ"}, headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == "NameZ"
    assert data['email'] == valid_user_active_admin['email'] 
    assert data['connection'] == valid_user_active_admin['connection'] 
    
  # Update Role
  def test_user_update_role_not_authorized(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__user_access_token__}'}
    response = client.patch(f"/api/users/role/2", headers=headers)
    data = response.json()
    
    assert response.status_code == 401
    assert data['detail'] == errorMessages.NO_PERMISSION
    
  def test_user_update_role_not_found(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/role/10", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_user_update_role_success(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.patch(f"/api/users/role/2", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    
  # Delete User
  def test_user_delete_user_not_found(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.delete(f"/api/users/10", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_user_delete_user_success(self, setup):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__admin_access_token__}'}
    response = client.delete(f"/api/users/4", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_to_be_deleted['name']
    assert data['connection'] == valid_user_to_be_deleted['connection']
    assert data['email'] == valid_user_to_be_deleted['email']
    assert data['role'] == 'USER'
    assert data['is_active'] == False
  