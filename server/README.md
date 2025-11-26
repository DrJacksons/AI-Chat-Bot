# 概述
web后端，基于Fastapi构建


# 功能模块
1、用户管理模块：包含登录注册、信息维护、权限管控等
2、聊天模块：包含用户与机器人的交互、消息记录等
3、数据集管理模块：包含数据集的上传、下载、管理等，每个用户对应一个个人空间
4、任务队列等


# Fastapi 中间件服务
## 数据库操作中间件
数据库orm操作
使用sqlalchemy+异步的连接方式，提高数据库操作的异步效率
对数据库增删改操作的commit事务进行管理，确保数据的一致性

## 权限验证中间件
对每个请求进行权限验证，判断用户是否有访问该接口的权限
如果用户没有权限，则返回403 Forbidden错误


# 数据库模型表
权限管理设计说明

- 核心实体
  - Role ：组织内角色，支持 organization_id + name 唯一，便于不同组织定义同名或不同名角色
  - Permission ：权限原子项，采用 code 唯一（例如 dataset.read , workspace.manage ），并提供可选的 resource 、 action 字段以满足细粒度
  - RolePermission ：角色与权限多对多关联
  - MembershipRole ：组织成员与角色多对多关联（通过 organization_membership 绑定组织上下文）
- 兼容性
  - 保留 OrganizationMembership.role 的字符串字段以兼容旧逻辑；你可以逐步迁移到 membership.roles 集合
- 关系导航
  - Organization.roles ：组织下的所有角色
  - OrganizationMembership.roles ：某成员在所在组织拥有的所有角色
  - Role.permissions / Permission.roles ：角色与权限的双向多对多

示例用法

- 赋权
  - 为组织 A 创建角色 ADMIN ，绑定权限 workspace.manage 、 dataset.write
  - 将成员 u 的 OrganizationMembership 关联到角色 ADMIN （通过 MembershipRole ）
- 校验
  - 在业务检查处，聚合成员所有 roles 的 permissions ，检验是否包含目标 Permission.code