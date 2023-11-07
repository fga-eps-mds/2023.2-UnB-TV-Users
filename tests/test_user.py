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

client = TestClient(app)

class TestUser:  
  
  def test_user_read_users(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 2 
    assert data[0]['name'] == valid_user_not_active['name']
    assert data[0]['connection'] == valid_user_not_active['connection']
    assert data[0]['email'] == valid_user_not_active['email']
    assert data[0]['is_active'] == False
    assert data[1]['name'] == valid_user_active['name']
    assert data[1]['connection'] == valid_user_active['connection']
    assert data[1]['email'] == valid_user_active['email']
    assert data[1]['is_active'] == True
    
  def test_user_read_users_limit(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/?limit=1", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == test_auth.valid_user_not_active['name']
    assert data[0]['connection'] == test_auth.valid_user_not_active['connection']
    assert data[0]['email'] == test_auth.valid_user_not_active['email']
    assert data[0]['is_active'] == False
    
  def test_user_read_users_skip(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/?skip=1", headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == test_auth.valid_user_active['name']
    assert data[0]['connection'] == test_auth.valid_user_active['connection']
    assert data[0]['email'] == test_auth.valid_user_active['email']
    assert data[0]['is_active'] == True
    
  def test_user_read_users_limit_skip(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.get("/api/users/?limit=1&skip=1", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == test_auth.valid_user_active['name']
    assert data[0]['connection'] == test_auth.valid_user_active['connection']
    assert data[0]['email'] == test_auth.valid_user_active['email']
    assert data[0]['is_active'] == True
    
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
    response = client.get("/api/users/3", headers=headers)
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
    response = client.patch(f"/api/users/3", json=valid_user_active, headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_user_partial_update_user(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    valid_user_active = {"name": "NameZ", "email": "valid@email.com", "connection": "COMUNIDADE"}
    response = client.patch(f"/api/users/1", json=valid_user_active, headers=headers)
    data = response.json()
    
    assert response.status_code == 200
    assert valid_user_active['name'] == data['name'] 
    assert valid_user_active['email'] == data['email'] 
    assert valid_user_active['connection'] == data['connection'] 
    
  def test_user_delete_user_not_found(self):
    headers={'Authorization': f'Bearer {test_auth.TestAuth.__token__}'}
    response = client.delete(f"/api/users/3", headers=headers)
    data = response.json()
    
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND