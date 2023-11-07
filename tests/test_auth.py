import pytest, os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from jose import JWTError
from fastapi import HTTPException

from src.main import app
from src.constants import errorMessages
from src.model import userModel
from src.utils import security, dotenv, send_mail
from src.database import get_db, engine, Base

valid_user_active = {"name": "NameA", "email": "valid@email.com", "connection": "COMUNIDADE", "password": "123456"}
duplicated_user = {"name": "NameB", "email": "valid@email.com", "connection": "COMUNIDADE", "password": "123456"} 
valid_user_not_active = {"name": "NameA", "email": "valid2@email.com", "connection": "COMUNIDADE", "password": "123456"}
invalid_connection = {"name": "NameC", "email": "invalid@email.com", "connection": "INVALID", "password": "123456"}
invalid_pass_length = {"name": "NameD", "email": "invalid@email.com", "connection": "COMUNIDADE", "password": "123"}
invalid_pass = {"name": "NameE", "email": "invalid@email.com", "connection": "COMUNIDADE", "password": "123abc"}

client = TestClient(app)

class TestAuth:
  __token__ = None
  
  @pytest.fixture(scope="session", autouse=True)
  def setup(self, session_mocker):
    session_mocker.patch('utils.security.generate_six_digit_number_code', return_value=123456)
    session_mocker.patch('utils.send_mail.send_verification_code', return_value=JSONResponse(status_code=200, content={ "status": "success" }))
    session_mocker.patch('utils.send_mail.send_reset_password_code', return_value=JSONResponse(status_code=200, content={ "status": "success" }))
  
    # /register - ok
    response = client.post("/api/auth/register", json=valid_user_active)
    data = response.json()
    assert response.status_code == 201
    assert data['status'] == 'success'
    
    response = client.post("/api/auth/register", json=valid_user_not_active)
    data = response.json()
    assert response.status_code == 201
    assert data['status'] == 'success'
    
    # /activate-account: ok 
    response = client.patch("/api/auth/activate-account", json={"email": valid_user_active['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == 'success'

    # /login: ok
    response = client.post("/api/auth/login", json={"email": valid_user_active['email'], "password": valid_user_active['password']})
    data = response.json()
    assert response.status_code == 200
    assert data['token_type'] == 'bearer'
    assert security.verify_token(data['access_token'])['email'] == valid_user_active['email']

    TestAuth.__token__ = data['access_token']

    yield

    userModel.Base.metadata.drop_all(bind=engine)

  # REGISTER
  def test_auth_register_connection_invalid(self, setup):
    response = client.post("/api/auth/register", json=invalid_connection)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_CONNECTION

  def test_auth_register_password_invalid_length(self, setup):
    response = client.post("/api/auth/register", json=invalid_pass_length)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_PASSWORD

  def test_auth_register_password_invalid_characters(self, setup):
    response = client.post("/api/auth/register", json=invalid_pass)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_PASSWORD

  def test_auth_register_duplicate_email(self, setup):
    response = client.post("/api/auth/register", json=duplicated_user)
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.EMAIL_ALREADY_REGISTERED

  # LOGIN
  def test_auth_login_wrong_password(self, setup):
    response = client.post("/api/auth/login", json={ "email": valid_user_active['email'], "password": "PASSWORD" })
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.PASSWORD_NO_MATCH

  def test_auth_login_not_found(self, setup):
    response = client.post("/api/auth/login", json=invalid_connection)
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND

  def test_auth_login_not_active(self, setup):
    # /login - nao ativo
    response = client.post("/api/auth/login", json={"email": valid_user_not_active['email'], "password": valid_user_not_active['password']})
    data = response.json()
    assert response.status_code == 401
    assert data['detail'] == errorMessages.ACCOUNT_IS_NOT_ACTIVE

  # RESEND CODE
  def test_auth_resend_code_user_not_found(self, setup):
    response = client.post("/api/auth/resend-code", json={"email": invalid_connection['email']})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_auth_resend_code_already_active(self, setup):
    response = client.post("/api/auth/resend-code", json={"email": valid_user_active['email']})
    data = response.json()
    assert response.status_code == 400
    assert data['status'] == 'error'
    assert data['message'] == errorMessages.ACCOUNT_ALREADY_ACTIVE

  def test_auth_resend_code_success(self, setup):
    response = client.post("/api/auth/resend-code", json={"email": valid_user_not_active['email']})
    data = response.json()
    assert response.status_code == 201
    assert data['status'] == 'success'

  # ACTIVATE ACCOUNT
  def test_auth_activate_account_user_not_found(self, setup):
    response = client.patch("/api/auth/activate-account", json={"email": invalid_connection['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
  
  def test_auth_activate_account_already_active(self, setup):
    response = client.patch("/api/auth/activate-account", json={"email": valid_user_active['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == 'error'
    assert data['message'] == errorMessages.ACCOUNT_ALREADY_ACTIVE
  
  def test_auth_activate_account_invalid_code(self, setup):
    response = client.patch("/api/auth/activate-account", json={"email": valid_user_not_active['email'], "code": 000000})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.INVALID_CODE
    
  # RESET PASSWORD - REQUEST
  def test_auth_reset_password_request_user_not_found(self, setup):
    response = client.post("/api/auth/reset-password/request", json={"email": invalid_connection['email']})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_auth_reset_password_request_not_active(self, setup):
    response = client.post("/api/auth/reset-password/request", json={"email": valid_user_not_active['email']})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.ACCOUNT_IS_NOT_ACTIVE
    
  # RESET PASSWORD - VERIFY
  def test_auth_reset_password_verify_user_not_found(self, setup):
    response = client.post("/api/auth/reset-password/verify", json={"email": invalid_connection['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  # RESET PASSWORD - CHANGE
  def test_auth_reset_password_change_user_not_found(self, setup):
    response = client.patch("/api/auth/reset-password/change", json={"email": invalid_connection['email'], "password": "123456", "code": 123456})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.USER_NOT_FOUND
    
  def test_auth_reset_password_change_invalid_password(self, setup):
    # Senha inválida
    response = client.patch("/api/auth/reset-password/change", json={"email": valid_user_active['email'], "password": "ABC", "code": 123456})
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_PASSWORD

  # RESET PASSWORD - Fluxo de troca
  def test_auth_reset_password_flow(self, setup):
    response = client.post("/api/auth/reset-password/verify", json={"email": valid_user_active['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 404
    assert data['detail'] == errorMessages.NO_RESET_PASSWORD_CODE
    
    # Requisitar troca de senha
    response = client.post("/api/auth/reset-password/request", json={"email": valid_user_active['email']})
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == 'success'
    
    # Solicitação inválido
    response = client.patch("/api/auth/reset-password/change", json={"email": valid_user_not_active['email'], "password": "123456", "code": 123456})
    data = response.json()
    assert response.status_code == 401
    assert data['detail'] == errorMessages.INVALID_REQUEST
    
    # Código inválido - verify
    response = client.post("/api/auth/reset-password/verify", json={"email": valid_user_active['email'], "code": 000000})
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_RESET_PASSWORD_CODE
    
    # Código inválido - change
    response = client.patch("/api/auth/reset-password/change", json={"email": valid_user_active['email'], "password": "123456", "code": 000000})
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == errorMessages.INVALID_RESET_PASSWORD_CODE
    
    # Código válido
    response = client.post("/api/auth/reset-password/verify", json={"email": valid_user_active['email'], "code": 123456})
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == 'success'
    
    # Troca de senha
    response = client.patch("/api/auth/reset-password/change", json={"email": valid_user_active['email'], "password": "123456", "code": 123456})
    data = response.json()
    assert response.status_code == 200
    assert data['name'] == valid_user_active['name']
    assert data['connection'] == valid_user_active['connection']
    assert data['email'] == valid_user_active['email']
    assert data['is_active'] == True
    


  def test_root_request(self, setup):
    response = client.get('/')
    data = response.json()
    assert response.status_code == 200
    assert data['message'] == 'UnB-TV!'
  
  def test_security_generate_six_digit_number_code(self):
    for _ in range(3):
      number = security.generate_six_digit_number_code()
      assert 100000 <= number <= 999999
      
  def test_security_verify_token_invalid_token(self):
    with pytest.raises(HTTPException) as exc_info:
      security.verify_token("invalid_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == errorMessages.INVALID_TOKEN
    
  def test_utils_validate_dotenv(self):
    environment_secret_value = os.environ['SECRET']
    del os.environ['SECRET']
    
    with pytest.raises(EnvironmentError) as exc_info:
      dotenv.validate_dotenv()
      
    assert str(exc_info.value) == "SOME ENVIRONMENT VALUES WERE NOT DEFINED (missing: SECRET)"
    
    os.environ["SECRET"] = environment_secret_value