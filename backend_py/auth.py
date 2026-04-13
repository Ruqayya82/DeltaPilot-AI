from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session
from database import User, get_db
from typing import Optional
import os
import uuid

SECRET = os.getenv("SECRET_KEY", "your-secret-key-here")

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

def get_user_db(session: Session = Depends(get_db)):
    return SQLAlchemyUserDatabase(session, User)

def get_user_manager(user_db=Depends(get_user_db)):
    return UserManager(user_db)