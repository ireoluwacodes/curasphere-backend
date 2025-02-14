from fastapi import Depends
from src.database import get_session
from src.api.user.models import User
from sqlmodel import select, Session
from src.api.user.schema import UserCreateInput, UserUpdateInput


class UserService:
    def __init__(self, session: Session = Depends(get_session)) -> None:
        self.session = session

    def get_users(self):
        statement = select(User)
        users = self.session.exec(statement).all()
        return users

    def create_user(self, user_create_input: UserCreateInput):
        user = User(**user_create_input.model_dump())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user(self, user_id: int):
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).one_or_none()
        if user is None:
            raise Exception("User not found")
        return user

    def update_user(self, user_id: int, user_update_input: UserUpdateInput):
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).one()
        for key, value in user_update_input.dict().items():
            setattr(user, key, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    def delete_user(self, user_id):
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).one()
        self.session.delete(user)
        self.session.commit()
        return user
