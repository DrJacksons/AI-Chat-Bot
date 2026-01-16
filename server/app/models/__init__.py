import datetime
import uuid
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    Integer,
    Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.core.database import Base


class DataframeLoadStatus(Enum):
    DONE = "DONE"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"


class ConnectorType(Enum):
    CSV = "CSV"
    DB = "DB"


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), index=True, unique=True)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    password = Column(String(255))
    verified = Column(Boolean, default=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission.id"), nullable=True)
    features = Column(JSON, nullable=True)
    
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    datasets = relationship("Dataset", back_populates="user")
    connectors = relationship("Connector", back_populates="user")
    spaces = relationship("Workspace", back_populates="user")
    user_spaces = relationship("UserSpace", back_populates="user")
    logs = relationship("Logs", back_populates="user")
    permission = relationship("Permission", back_populates="users", foreign_keys=[permission_id])


class Department(Base):
    __tablename__ = "department"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)

    users = relationship("User", back_populates="department")


class Permission(Base):
    __tablename__ = "permission"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(String(255))
    resource = Column(String(255), nullable=True)
    action = Column(String(255), nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    users = relationship("User", back_populates="permission")

    __table_args__ = (UniqueConstraint("code", name="uq_permission_code"),)


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String)
    table_name = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    head = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    connector_id = Column(UUID(as_uuid=True), ForeignKey("connector.id"))
    field_descriptions = Column(JSON, nullable=True)
    filterable_columns = Column(JSON, nullable=True)

    user = relationship("User", back_populates="datasets")
    connector = relationship("Connector", back_populates="datasets", lazy="joined")
    dataset_spaces = relationship("DatasetSpace", back_populates="dataset")


class Connector(Base):
    __tablename__ = "connector"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

    user = relationship("User", back_populates="connectors")
    datasets = relationship("Dataset", back_populates="connector")

    __table_args__ = (UniqueConstraint("id", name="uq_connector_id"),)


class Workspace(Base):
    __tablename__ = "workspace"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="spaces")
    dataset_spaces = relationship("DatasetSpace", back_populates="workspace")
    user_spaces = relationship("UserSpace", back_populates="workspace")


class UserSpace(Base):
    __tablename__ = "user_space"
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace.id"), primary_key=True
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)

    workspace = relationship("Workspace", back_populates="user_spaces", lazy="joined")
    user = relationship("User", back_populates="user_spaces", lazy="joined")


class UserConversation(Base):
    __tablename__ = "user_conversation"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    type_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    valid = Column(Boolean, default=True)

    workspace = relationship("Workspace")
    user = relationship("User")
    messages = relationship(
        "ConversationMessage",
        back_populates="user_conversation",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_message"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("user_conversation.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)
    query = Column(String)
    response = Column(JSON, nullable=True)
    intent = Column(String, nullable=True)
    code_generated = Column(String, nullable=True)
    label = Column(String, nullable=True)
    log_id = Column(UUID(as_uuid=True), ForeignKey("logs.id"))
    settings = Column(JSON, nullable=True)
    valid = Column(Boolean, default=True)

    user_conversation = relationship("UserConversation", back_populates="messages")
    log = relationship("Logs", back_populates="conversation_messages")


class DatasetSpace(Base):
    __tablename__ = "dataset_space"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("dataset.id"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"))

    dataset = relationship("Dataset", back_populates="dataset_spaces")
    workspace = relationship("Workspace", back_populates="dataset_spaces")


class Logs(Base):
    __tablename__ = "logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)
    query = Column(String, default="")
    execution_time = Column(Float, default=2.0)
    exhausted_tokens = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    json_log = Column(JSON, nullable=True)

    user = relationship("User", back_populates="logs")
    conversation_messages = relationship("ConversationMessage", back_populates="log")
