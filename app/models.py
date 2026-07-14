from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """SQLAlchemy model for an authenticated user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="owner", cascade="all, delete-orphan")


class Folder(Base):
    """SQLAlchemy model for a folder/group containing todo items."""

    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="folders")
    todos = relationship("Todo", back_populates="folder", cascade="all, delete-orphan")


class Todo(Base):
    """SQLAlchemy model for a todo item (task)."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)

    owner = relationship("User", back_populates="todos")
    folder = relationship("Folder", back_populates="todos")
    checklist_items = relationship("ChecklistItem", back_populates="todo", cascade="all, delete-orphan")


class ChecklistItem(Base):
    """SQLAlchemy model for a checklist/tick-box item inside a todo (task)."""

    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    todo_id = Column(Integer, ForeignKey("todos.id"), nullable=False)

    todo = relationship("Todo", back_populates="checklist_items")

