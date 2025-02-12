from tortoise.models import Model
from tortoise import fields
from enum import Enum

class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    
    
class User(Model):
    id = fields.IntField(pk=True)  # Primary key
    name = fields.CharField(max_length=255, index=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    password = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    role = fields.CharEnumField(RoleEnum, default=RoleEnum.USER)


class Contact(Model):
    id = fields.IntField(pk=True)
    phone_number = fields.CharField(max_length=20, index=True)  # Renamed from phoneNumber
    email = fields.CharField(max_length=255, index=True)
    link_precedence = fields.CharField(max_length=50, default="primary")  # Renamed from linkPrecedence 
    link_id = fields.IntField(null=True)  # Allow nulls
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)  # Allow nulls
