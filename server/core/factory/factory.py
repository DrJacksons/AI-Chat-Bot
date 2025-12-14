from functools import partial

from fastapi import Depends

from server.app.controllers import UserController, LogsController, WorkspaceController, AuthController, DepartmentController, RoleController
from server.app.models import (
    Dataset,
    Department,
    Workspace,
    User,
    UserConversation,
    Logs,
    Role
)
from server.app.repositories import UserRepository, WorkspaceRepository, LogsRepository, DatasetRepository, ConversationRepository, DepartmentRepository, RoleRepository
from server.core.database import get_session


class Factory:
    """
    工厂容器，实例化所有的Controller和Repository，这些都可以被应用程序的其他部分所调用。
    """

    # Repositories
    user_repository = partial(UserRepository, User)
    department_repository = partial(DepartmentRepository, Department)
    space_repository = partial(WorkspaceRepository, Workspace)
    dataset_repository = partial(DatasetRepository, Dataset)
    conversation_repository = partial(ConversationRepository, UserConversation)
    logs_repository = partial(LogsRepository, Logs)
    role_repository = partial(RoleRepository, Role)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
        )

    def get_department_controller(self, db_session=Depends(get_session)):
        return DepartmentController(
            department_repository=self.department_repository(db_session=db_session),
        )

    def get_role_controller(self, db_session=Depends(get_session)):
        return RoleController(
            role_repository=self.role_repository(db_session=db_session),
        )

    def get_space_controller(self, db_session=Depends(get_session)):
        return WorkspaceController(
            space_repository=self.space_repository(db_session=db_session),
            dataset_repository=self.dataset_repository(db_session=db_session),
        )

    def get_auth_controller(self, db_session=Depends(get_session)):
        return AuthController(
            user_repository=self.user_repository(db_session=db_session),
        )

    def get_chat_controller(self, db_session=Depends(get_session)):
        return ChatController(
            user_repository=self.user_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session),
            conversation_repository=self.conversation_repository(db_session=db_session),
            logs_repository=self.logs_repository(db_session=db_session),
        )
    
    def get_datasets_controller(self, db_session=Depends(get_session)):
        return DatasetController(
            dataset_repository=self.dataset_repository(db_session=db_session),
            space_repository=self.space_repository(db_session=db_session)
        )

    def get_conversation_controller(self, db_session=Depends(get_session)):
        return ConversationController(
            user_repository=self.user_repository(db_session=db_session),
            conversation_repository=self.conversation_repository(db_session=db_session),
        )
    
    def get_logs_controller(self, db_session=Depends(get_session)):
        return LogsController(
            logs_repository=self.logs_repository(db_session=db_session),
        )