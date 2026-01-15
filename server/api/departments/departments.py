from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Body, HTTPException

from server.core.fastapi.dependencies.authentication import AuthenticationRequired
from server.app.controllers.department import DepartmentController
from server.app.schemas.requests.department import CreateDepartmentRequest, UpdateDepartmentRequest
from server.app.schemas.responses.department import DepartmentBase
from server.app.schemas.responses.users import UserResponse
from server.core.factory import Factory
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
    return await department_controller.create_department(
        name=department_request.name,
        description=department_request.description,
        settings=department_request.settings
    )


@department_router.get("/", response_model=List[DepartmentBase])
async def list_departments(
    department_controller: DepartmentController = Depends(Factory().get_department_controller)
):
    return await department_controller.repository.get_all()


@department_router.get("/{department_id}", dependencies=[Depends(AuthenticationRequired)], response_model=DepartmentBase)
async def get_department(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
):
    return await department_controller.repository.get_by_id(department_id)


@department_router.patch("/{department_id}", dependencies=[Depends(AuthenticationRequired)], response_model=DepartmentBase)
async def update_department(
    department_id: UUID,
    request: UpdateDepartmentRequest,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
):
    # TODO: Add permission check
    return await department_controller.update_department(
        department_id=department_id,
        **request.dict(exclude_unset=True)
    )


@department_router.delete("/{department_id}", dependencies=[Depends(AuthenticationRequired)], status_code=204)
async def delete_department(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
):
    # TODO: Add permission check
    await department_controller.delete_department(department_id)


@department_router.post("/{department_id}/users/{user_id}", status_code=201)
async def add_user_to_department(
    department_id: UUID,
    user_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    await department_controller.add_user(department_id, user_id)


@department_router.delete("/{department_id}/users/{user_id}", status_code=204)
async def remove_user_from_department(
    department_id: UUID,
    user_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    # TODO: Add permission check
    await department_controller.remove_user(department_id, user_id)


@department_router.get("/{department_id}/users", response_model=List[UserResponse])
async def get_department_users(
    department_id: UUID,
    department_controller: DepartmentController = Depends(Factory().get_department_controller),
    user: User = Depends(get_current_user),
):
    users = await department_controller.repository.get_users(department_id)
    return users
