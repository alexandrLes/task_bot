from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Float,
    DateTime, Boolean, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship, declarative_base
from uuid import uuid4

Base = declarative_base()

class UserRole(str, Enum):
    AUTHOR = "author"
    EXECUTOR = "executor"

class TaskStatus(str, Enum):
    PENDING = "pending"       # Ожидает исполнителя
    IN_PROGRESS = "in_progress"  # В работе
    COMPLETED = "completed"   # Завершено успешно
    REJECTED = "rejected"     # Отклонено автором

class User(Base):
    """Модель пользователя (автор или исполнитель)."""
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)  # Telegram ID
    username = Column(String(64), nullable=True)    # @username
    role = Column(SQLEnum(UserRole), nullable=False)
    rating = Column(Float, default=0.0)            # Средний рейтинг
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи (для SQLAlchemy)
    tasks_created = relationship("Task", back_populates="author")  # Задания, которые создал
    tasks_assigned = relationship("TaskAssignment", back_populates="executor")  # Задания, которые взял
    feedbacks_given = relationship("Feedback", foreign_keys="Feedback.from_user_id", back_populates="from_user")
    feedbacks_received = relationship("Feedback", foreign_keys="Feedback.to_user_id", back_populates="to_user")

class Task(Base):
    """Модель задания."""
    __tablename__ = "tasks"

    task_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))  # UUID
    author_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    reward = Column(Float, nullable=True)          # Вознаграждение (необязательно)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    deadline = Column(DateTime, nullable=False)    # Срок выполнения
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    author = relationship("User", back_populates="tasks_created")
    assignments = relationship("TaskAssignment", back_populates="task")
    submissions = relationship("TaskSubmission", back_populates="task")

class TaskAssignment(Base):
    """Назначение задания исполнителю."""
    __tablename__ = "task_assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.task_id"), nullable=False)
    executor_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # Заполняется при подтверждении

    # Связи
    task = relationship("Task", back_populates="assignments")
    executor = relationship("User", back_populates="tasks_assigned")

class TaskSubmission(Base):
    """Результат выполнения задания (скриншот)."""
    __tablename__ = "task_submissions"

    submission_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), ForeignKey("tasks.task_id"), nullable=False)
    executor_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    screenshot_url = Column(String(255), nullable=False)  # Путь в S3/Firebase
    submitted_at = Column(DateTime, default=datetime.utcnow)
    rejection_reason = Column(Text, nullable=True)       # Причина отказа

    # Связи
    task = relationship("Task", back_populates="submissions")
    executor = relationship("User")

class Feedback(Base):
    """Отзыв о сотрудничестве."""
    __tablename__ = "feedbacks"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)  # Кто оставил
    to_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)    # О ком
    task_id = Column(String(36), ForeignKey("tasks.task_id"), nullable=False)
    rating = Column(Integer, nullable=False)       # 1-5
    comment = Column(Text, nullable=True)         # Текст отзыва
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="feedbacks_given")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="feedbacks_received")
    task = relationship("Task")

