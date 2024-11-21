from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from argon2 import PasswordHasher
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Index, JSON
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship
import string
import random
import enum


# Initialize SQLAlchemy and Password hasher
db = SQLAlchemy()
password_hasher = PasswordHasher()


# Class Model to return queries as dict
class ModelMixin:
    def to_dict(self):
        """Automatically converts all columns of the model to a dictionary."""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


def gen_unique_login_id(length=8, max_attempts=10):
    """Generate a unique login_id for a new User using UPPERCASE letters and 0-9 digits."""
    attempts = 0
    characters = string.ascii_uppercase + string.digits
    while attempts < max_attempts:
        login_id = ''.join(random.choice(characters) for _ in range(length))
        if not User.query.filter_by(login_id=login_id).first():
            return login_id
        attempts += 1
    raise Exception("Failed to generate a unique login_id after maximum attempts.")


#######################################################################
#                                                                     #
#                          DATABASE TABLES                            #
#                                                                     #
#######################################################################

# The user table
class User(UserMixin, ModelMixin, db.Model):
    """
    An new User instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param login_id: Unique identifier for the user's login, generated by
        `gen_unique_login_id()`.
        :type login_id: str
        :param username: The user's login username.
        :type username: str
        :param password: The user's login password.
        :type password: str
        :param canvas_id: Unique identifier for the user on Canvas.
        :type canvas_id: str
        :param canvas_name: The user's name on Canvas.
        :type canvas_name: str
        :param canvas_token_password: The encrypted Canvas token, encrypted using the user's
        unencrypted password.
        :type canvas_token_password: str
        :param todoist_token_password: The encrypted Todoist token, encrypted using the user's
        unencrypted password.
        :type todoist_token_password: str
    """
    __tablename__ = 'users'

    # Table primary key
    id = Column(Integer, primary_key=True)

    # Info for login
    login_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), unique=False, nullable=False)

    # Canvas info for user
    canvas_id = Column(String(150), unique=False, nullable=False)
    canvas_name = Column(String(150), unique=False, nullable=False)

    # Tokens encrypted with password
    canvas_token_password = Column(String(200), unique=False, nullable=False)
    todoist_token_password = Column(String(200), unique=False, nullable=False)

    # Tokens encrypted with session key
    canvas_token_session = None         # Placeholder for encrypted token with session key
    todoist_token_session = None        # Placeholder for encrypted token with session key

    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")
    conversations = relationship('Conversation', back_populates='user', cascade="all, delete-orphan")
    invitations_received = relationship('SubTaskInvitation', foreign_keys='SubTaskInvitation.recipient_id', back_populates='recipient', cascade="all, delete-orphan")

    # When the `login_manager.user_loader` is run for the login, this is the parameter it will use
    def get_id(self):
        return str(self.login_id)


# A representation of the different types of tasks
class TaskType(enum.Enum):
    assignment = 0


# A representation of the different types of tasks
class TaskStatus(enum.Enum):
    Incomplete = 0
    Completed = 1

    @classmethod
    def from_integer(cls, value):
        """
        Returns the corresponding SubStatus enum member based on the provided integer.

        :param value: An integer representing the status (0 for Incomplete, 1 for Completed).
        :return: The corresponding SubStatus enum member if valid; None if invalid.
        """
        try:
            return cls(value)
        except Exception:
            raise None


# The task table
# A representation of a Canvas assignment and the connected Todoist task
# This primarily exists to link tasks in Canvas and Todoist
class Task(ModelMixin, db.Model):
    """
    A new Task instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param owner: The ID of the User that owns the task.
        :type owner: int
        :param task_type: The type of the task.
        :type task_type: TaskType
        :param canvas_id: The ID of the task in Canvas.
        :type canvas_id: str
        :param todoist_id: The ID of the task in Todoist, if one exists.
        :type todoist_id: str | None
        :param due_date: The due date of the task in format `%Y-%m-%d %H:%M:%S`, if one exists.
        :type due_date: str | None
    """
    __tablename__ = 'tasks'
    __table_args__ = (
        Index('idx_canvas_owner', 'canvas_id', 'owner'),
    )

    # Table primary key
    id = Column(Integer, primary_key=True)
    # Foreign key to owner
    owner = Column(Integer, ForeignKey('users.id'), unique=False, nullable=False)
    # Type of the task
    task_type = Column(Enum(TaskType), unique=False, nullable=False)
    # IDs for Canvas and Todoist
    canvas_id = Column(Integer, unique=False, nullable=True)
    todoist_id = Column(String(15), unique=False, nullable=True)
    due_date = Column(String(12), unique=False, nullable=True)
    # If it's complete
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.Incomplete)

    # Name and description for if the task is not associated with a Canvas assignment
    name = Column(String(100), unique=False, nullable=True)
    description = Column(String(500), unique=False, nullable=True)

    user = relationship('User', back_populates='tasks')
    subtasks = relationship('SubTask', back_populates='task', cascade="all, delete-orphan")


class SubTask(ModelMixin, db.Model):
    """
    A new SubTask instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param owner: The ID of the User that owns the task.
        :type owner: int
        :param task_id: The ID of the Task this SubTask belongs to.
        :type task_id: int
        :param name: The name of the SubTask.
        :type name: str
        :param description: A description of the SubTask (optional).
        :type description: str | None
        :param status: The status of the SubTask, as defined by `SubTaskStatus`.
        :type status: SubTaskStatus
        :param due_date: The due date of the task in format `%Y-%m-%d %H:%M:%S`, if one exists.
        :type due_date: str | None
    """
    __tablename__ = 'subtasks'
    __table_args__ = (
        Index('idx_task_id_owner', 'task_id', 'owner'),
    )

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    todoist_id = Column(String(15), unique=False, nullable=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.Incomplete)
    due_date = Column(String(12), nullable=True)
    shared_with = Column(JSON, nullable=True, default=[])

    task = relationship('Task', back_populates='subtasks')
    
    
class SubTaskShared(ModelMixin, db.Model):
    """
    A new SubTaskShared instance.
    :param id: The auto-generated table ID.
    :type id: int
    :param owner: The ID of the User that owns the shared subtask.
    :type owner: int
    :param subtask_id: The ID of the SubTask that is shared.
    :type subtask_id: int
    :param todoist_original: The ID of the original task in Todoist, if one exists.
    :type todoist_original: str
    :param todoist_id: The ID of the task in Todoist, if one exists.
    :type todoist_id: str
    """
    __tablename__ = 'shared_subtasks'
    __table_args__ = (
        Index('idx_owner_subtask_id', 'subtask_id', 'owner'),
    )
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    subtask_id = Column(Integer, ForeignKey('subtasks.id', ondelete='CASCADE'), nullable=False)
    todoist_original = Column(String(15), unique=False, nullable=False)
    todoist_id = Column(String(15), unique=False, nullable=False)
    
    subtask = relationship('SubTask')
    

class Conversation(ModelMixin, db.Model):
    """
    A new Conversation instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param owner: The ID of the User that owns the conversation.
        :type owner: int
        :param conversation_id: The ID of the conversation.
        :type conversation_id: int
        :param canvas_id: The ID of the Canvas assignment.
        :type canvas_id: int
    """
    __tablename__ = 'conversations'
    __table_args__ = (
        Index('idx_conv_owner', 'canvas_id', 'owner'),
    )

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(Integer, nullable=False)
    canvas_id = Column(Integer, nullable=False)

    user = relationship('User', back_populates='conversations')
    
    
class SubTaskInvitation(ModelMixin, db.Model):
    """
    A new SubTaskInvitation instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param owner: The ID of the User that owns the invitation.
        :type owner: int
        :param recipient_id: The ID of the User that the invitation is for.
        :type recipient_id: int
        :param subtask_id: The ID of the SubTask that the invitation is for.
        :type subtask_id: int | None
    """
    __tablename__ = 'subtask_invitations'
    __table_args__ = (
        Index('idx_task_id_recipient', 'subtask_id', 'recipient_id'),
    )

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subtask_id = Column(Integer, ForeignKey('subtasks.id', ondelete='SET NULL'), nullable=True)
    
    recipient = relationship('User', foreign_keys=[recipient_id], back_populates='invitations_received')
    


class Filter(ModelMixin, db.Model):
    """
    A new Filter instance.
        :param id: The auto-generated table ID.
        :type id: int
        :param owner: The ID of the User that owns the filter.
        :type owner: int
        :param filter: The word or phrase to filter.
        :type filter: str
    """
    __tablename__ = 'filters'
    __table_args__ = (
        db.UniqueConstraint('owner', 'filter'),
    )

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    filter = Column(String(50), nullable=False)
