from sqlalchemy import Column, ForeignKey, Enum, Integer, String, DateTime, UUID
from sqlalchemy.orm import Relationship, relationship
from common.session import Base
from modules.auth.domain.entities.user import User
from modules.auth.domain.entities.user import UserStateEnum
from modules.auth.infrastructure.database.models.base_entity import BaseEntitySQLAlchemy
from modules.auth.infrastructure.database.models.roles import RoleSQLAlchemy


class UserSQLAlchemy(Base, BaseEntitySQLAlchemy):
    __tablename__ = "Users"
    __table_args__ = {"schema": "custom_auth"}

    email: str | Column[str] = Column(String(255), unique=True, nullable=False)
    hash_password: str | Column[str] = Column(String(255), nullable=False)
    state: UserStateEnum | Column[UserStateEnum] = Column(
        Enum(UserStateEnum), nullable=False
    )
    role_id: int | Column[int] = Column(
        Integer, ForeignKey("custom_auth.Roles.id"), nullable=False
    )
    user_code: str | Column[str] = Column(String(255), unique=True, nullable=False)

    role: Relationship["RoleSQLAlchemy"] = relationship(
        "RoleSQLAlchemy", back_populates="users"
    )  # Assuming RoleSQLAlchemy has a users relationship
