from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from server.core.fastapi.dependencies.authentication import AuthenticationRequired
from server.app.controllers.department import DepartmentController
from server.app.schemas.requests.department import CreateDepartmentRequest, UpdateDepartmentRequest
from server.app.schemas.responses.department import DepartmentBase
from server.app.schemas.responses.users import UserResponse
from server.core.factory import Factory, app_logger
from server.core.fastapi.dependencies.current_user import get_current_user
from server.app.models import User


department_router = APIRouter()


@department_router.post("/", response_model=DepartmentBase)
async def create_department(
    department_request: CreateDepartmentRequest,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    # only admin user can create departments
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can create departments")
    app_logger.info(f"Into create department interface(user={user.id}). Request params: {department_request}")
    return await department_controller.create_department(
        name=department_request.name,
        description=department_request.description,
        settings=department_request.settings
    )


@department_router.get("/", dependencies=[Depends(AuthenticationRequired)], response_model=List[DepartmentBase])
async def list_departments(
    department_controller: DepartmentController = Depends(Factory().get_department_controller)
):
    return await department_controller.repository.get_all()


@department_router.get("/{department_id}", dependencies=[Depends(AuthenticationRequired)], response_model=DepartmentBase)
async def get_department(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
):
    app_logger.info(f"Into get department interface. Request params: department_id={department_id}")
    return await department_controller.repository.get_by_id(department_id)


@department_router.patch("/{department_id}", dependencies=[Depends(AuthenticationRequired)], response_model=DepartmentBase)
async def update_department(
    department_id: UUID,
    request: UpdateDepartmentRequest,
    user: User = Depends(get_current_user),
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
):
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can update departments")
    app_logger.info(f"Into update department interface. Request params: department_id={department_id}, {request}")
    return await department_controller.update_department(
        department_id=department_id,
        **request.dict(exclude_unset=True)
    )


@department_router.delete("/{department_id}", dependencies=[Depends(AuthenticationRequired)], status_code=204)
async def delete_department(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can delete departments")
    app_logger.info(f"Into delete department interface. Request params: department_id={department_id}")
    await department_controller.delete_department(department_id)


@department_router.post("/{department_id}/users/{user_id}", status_code=201)
async def add_user_to_department(
    department_id: UUID,
    user_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can add users to departments")
    app_logger.info(f"Into add user to department interface. Request params: department_id={department_id}, user_id={user_id}")
    await department_controller.add_user(department_id, user_id)


@department_router.delete("/{department_id}/users/{user_id}", status_code=204)
async def remove_user_from_department(
    department_id: UUID,
    user_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can remove users from departments")
    app_logger.info(f"Into remove user from department interface. Request params: department_id={department_id}, user_id={user_id}")
    await department_controller.remove_user(department_id, user_id)


@department_router.get("/{department_id}/users", response_model=List[UserResponse])
async def get_department_users(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    if not user.permissions.code == "admin.all":
        raise HTTPException(status_code=403, detail="Only admin user can get users in departments")
    app_logger.info(f"Into get department users interface. Request params: department_id={department_id}")
    users = await department_controller.repository.get_users(department_id)
    return users
