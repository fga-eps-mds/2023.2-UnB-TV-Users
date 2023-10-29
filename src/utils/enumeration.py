from enum import Enum

class UserConnection(Enum):
  ALUNO = "ALUNO"
  PROFESSOR = "PROFESSOR"
  COMUNIDADE = "COMUNIDADE"
  EXTERNO = "EXTERNO"

  @classmethod
  def has_value(cls, value):
    return value in cls._value2member_map_
  
class UserRole(Enum):
  ADMIN = "ADMINISTRADOR"
  USER = "USUARIO"

  @classmethod
  def has_value(cls, value):
    return value in cls._value2member_map_