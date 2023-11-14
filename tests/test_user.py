import pytest, os, asyncio
from fastapi.testclient import TestClient

from src.main import app
from src.constants import errorMessages
from src.database import get_db, engine, Base
from tests import test_auth

valid_user_active = test_auth.valid_user_active
duplicated_user = test_auth.duplicated_user
valid_user_not_active = test_auth.valid_user_not_active
invalid_connection = test_auth.invalid_connection
invalid_pass_length = test_auth.invalid_pass_length
invalid_pass = test_auth.invalid_pass
valid_user_to_be_deleted = test_auth.valid_user_to_be_deleted

client = TestClient(app)

class TestUser: 
  def test_user_read_users(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/", headers=headers)
    data = response.json()
    
    initial = len(data)
    assert response.status_code == 200
    assert data[initial - 1]['name'] == valid_user_active['name']
    assert data[initial - 1]['connection'] == valid_user_active['connection']
    assert data[initial - 1]['email'] == valid_user_active['email']
    assert data[initial - 1]['is_active'] == True
    
  def test_user_read_user(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/1", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_active['name']
    assert data['connection'] == valid_user_active['connection']
    assert data['email'] == valid_user_active['email']
    assert data['is_active'] == True
    
  def test_user_read_user_not_found(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/5", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_user_read_user_by_email(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get(f"/api/users/email/{valid_user_active['email']}", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_active['name']
    assert data['connection'] == valid_user_active['connection']
    assert data['email'] == valid_user_active['email']
    
  def test_user_read_user_by_email_not_found(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get(f"/api/users/email/{invalid_connection['email']}", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_user_partial_update_user_invalid_connection(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.patch(f"/api/users/1", json={"name": "NameZ", "email": "valid@email.com", "connection": "INVALIDO"}, headers=headers)
    data = response.json()
    
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_CONNECTION
  
  def test_user_partial_update_user_not_found(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.patch(f"/api/users/5", json=valid_user_active, headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_user_partial_update_user(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    valid_user_active = {"name": "NameZ", "email": "valid@email.com", "connection": "ESTUDANTE"}
    response = client.patch(f"/api/users/1", json=valid_user_active, headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert valid_user_active['name'] == data['name'] 
    assert valid_user_active['email'] == data['email'] 
    assert valid_user_active['connection'] == data['connection'] 
    
  def test_user_delete_user_not_found(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.delete(f"/api/users/5", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_user_delete_user_success(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.delete(f"/api/users/3", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert data['name'] == valid_user_to_be_deleted['name']
    assert data['connection'] == valid_user_to_be_deleted['connection']
    assert data['email'] == valid_user_to_be_deleted['email']
    assert data['role'] == 'USER'
    assert data['is_active'] == False
  