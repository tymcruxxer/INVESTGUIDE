# User, Role & Permission Management

## Purpose

Sprint 053 adds the controlled administration layer for inspecting users, roles, effective permissions, and account status. It builds on the Owner/Admin foundation without introducing editable permission management or production ownership transfer.

The module answers three operational questions:

* Who has access to InvestGuide?
* Which roles and permissions do they inherit?
* Which privileged user changes happened, why, and who performed them?

## Core Model

Users remain the identity source. Roles describe administrative responsibility. Permissions remain read-only metadata inherited through role assignments.

Current relationships:

```text
User
  -> UserRole
      -> Role
          -> RolePermission
              -> Permission
```

Additional audit/history records:

```text
UserRoleHistory
PrivilegeChangeHistory
AuditLog
SensitiveActionRequest
```

## Built-In Roles

* `owner`: protected platform owner with audited permission bypass.
* `administrator`: broad system administrator role.
* `operations-admin`: ingestion/source operations role.
* `finance-admin`: analytics and financial intelligence review role.
* `support-admin`: user support and account status role.
* `moderator`: read-only user/audit inspection role.
* `user`: default authenticated user role with no admin permissions.

## Owner Invariants

The Owner role is protected by service rules:

* exactly one active Owner assignment is required after RBAC bootstrap;
* Owner cannot be assigned through normal role-management endpoints;
* Owner cannot be removed through normal role-management endpoints;
* Owner cannot be suspended;
* ownership transfer is deferred to a dedicated future workflow.

The database supports the model through role/user-role tables and indexes. Cross-table Owner invariants are enforced in the service layer where transaction context is available.

## APIs

The admin API is under `/api/v1/admin` and requires JWT authentication plus server-side permissions.

* `GET /api/v1/admin/users`
* `GET /api/v1/admin/users/{id}`
* `PATCH /api/v1/admin/users/{id}/roles`
* `PATCH /api/v1/admin/users/{id}/status`
* `GET /api/v1/admin/roles`
* `GET /api/v1/admin/roles/{id}`
* `GET /api/v1/admin/permissions`

User payloads never expose password hashes or secrets.

## Sensitive Operations

Role and status changes require a reason and confirmation flag. Successful operations record:

* actor user id;
* target user id;
* previous state;
* new state;
* reason;
* request id when provided;
* result;
* timestamp.

`SensitiveActionRequest` stores confirmed sensitive-action records as a future-compatible hook for re-authentication and MFA. Sprint 053 does not implement MFA or re-authentication prompts.

## Frontend Admin UX

The frontend admin shell now includes:

* `/admin/users`: searchable/filterable user directory;
* `/admin/users/[id]`: user detail, role changes, status changes, effective permissions, and audit summary;
* `/admin/roles`: read-only role catalog;
* `/admin/roles/[id]`: role permission inspection.

Permission editing, Owner transfer, audit export, and production provisioning remain future work.

## Development Seed

`python -m app.database.seed` now seeds RBAC data and sample development admin users when development data is allowed. The seed is manual only and duplicate-aware.

## Future Work

* Production Owner provisioning and transfer workflow.
* Dedicated audit log viewer and exports.
* Optional `AuthContext` object for protected services.
* Re-authentication and MFA enforcement for sensitive actions.
* Role editor only after governance rules are finalized.
