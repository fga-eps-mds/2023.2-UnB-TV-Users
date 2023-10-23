import logging
import pytest, os, asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from unittest.mock import Mock
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, declarative_base

from src.main import app
from src.constants import errorMessages
from src.database import get_db, engine, Base

log = logging.getLogger()

load_dotenv()

send_mail_address = os.getenv("MAIL_FROM")

register_users = [
  { "name": "NameA", "email": send_mail_address, "connection": "COMUNIDADE", "password": "123456" }, # Valid
  { "name": "NameB", "email": send_mail_address, "connection": "COMUNIDADE", "password": "123456" }, # Email Duplicated
  { "name": "NameC", "email": "test@test.com", "connection": "INVALID", "password": "123456" }, # Connection Invalid
  { "name": "NameD", "email": "test@test.com", "connection": "COMUNIDADE", "password": "123" }, # Password Invalid Length
  { "name": "NameE", "email": "test@test.com", "connection": "COMUNIDADE", "password": "123abc" }, # Password Invalid Characters
]

client = TestClient(app)

def test_auth_register_connection_invalid():
  response = client.post("/api/auth/register", json=register_users[2])
  data = response.json()
  
  assert response.status_code == 400
  assert data['detail'] == errorMessages.INVALID_CONNECTION

def test_auth_register_password_invalid_length():
  response = client.post("/api/auth/register", json=register_users[3])
  data = response.json()
  
  assert response.status_code == 400
  assert data['detail'] == errorMessages.INVALID_PASSWORD

def test_auth_register_password_invalid_characters():
  response = client.post("/api/auth/register",json=register_users[4])
  data = response.json()
  
  assert response.status_code == 400
  assert data['detail'] == errorMessages.INVALID_PASSWORD

def test_auth_login_not_found():
  response = client.post("/api/auth/login", json=register_users[2])
  data = response.json()

  assert response.status_code == 404
  assert data['detail'] == errorMessages.USER_NOT_FOUND

# Executar uma request antes de todos os testes OU limpar DB a cada teste

# def test_auth_register_duplicate():
#   response = client.post("/api/auth/register", json=register_users[0])
#   data = response.json()

#   assert response.status_code == 201
#   assert data['status'] == "success"

#   response = client.post("/api/auth/register", json=register_users[1])
#   data = response.json()

#   assert response.status_code == 400
#   assert data['detail'] == errorMessages.EMAIL_ALREADY_REGISTERED

# def test_auth_login_password_no_match():
#   response = client.post("/api/auth/login", json={ "email": register_users[0]['email'], "password": "654321" })
#   data = response.json()

#   assert response.status_code == 404
#   assert data['detail'] == errorMessages.PASSWORD_NO_MATCH

# def test_auth_login_notactive():
#   response = client.post("/api/auth/register", json=register_users[0])
#   assert response.status_code == 200

#   response = client.post("/api/auth/login", json={ "email": register_users[0]['email'], "password": register_users[0]['password'] })
#   data = response.json()
#   assert response.status_code == 500
#   assert data['detail'] == errorMessages.ACCOUNT_IS_NOT_ACTIVE
