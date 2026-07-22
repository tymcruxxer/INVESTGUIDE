# Admin Platform Architecture

Sprint 052 establishes the Owner and Administration Foundation for InvestGuide. The admin platform is intentionally separate from the investor experience while sharing the same authentication system.

## Purpose

The administration layer is the operating system for InvestGuide. Future modules such as user management, data source management, ingestion operations, analytics administration, feature flags, and AI provider configuration should plug into this foundation rather than creating separate authorization systems.

## Authentication Boundary

InvestGuide continues to use one JWT authentication system. Administrative access is not a second login system. A signed-in user enters Admin Mode only when the backend confirms that the user has administrative permissions.

Frontend checks are convenience only. Every admin API endpoint enforces authorization server-side.

## RBAC Model

The RBAC schema contains:

* `roles`
* `permissions`
* `role_permissions`
* `user_roles`

Roles describe identity groups. Permissions describe granular actions. Role permissions connect roles to permissions. User roles assign active roles to users.

The initial system roles are:

* Owner
* Administrator
* User

Future roles can include Operations Admin, Finance Admin, Support Admin, and Moderator without changing the schema.

## Permission Model

Permissions are granular strings grouped by category. Bootstrap permissions include:

* `users.read`
* `users.update`
* `users.delete`
* `roles.read`
* `roles.update`
* `sources.read`
* `sources.update`
* `ingestion.read`
* `ingestion.manage`
* `analytics.read`
* `system.read`
* `system.configure`
* `audit.read`
* `audit.export`

Future admin APIs should use the reusable `require_permission()` dependency.

## Owner Protections

The Owner role is protected:

* exactly one active Owner assignment is expected after bootstrap
* Owner cannot be deleted through normal workflows
* Owner cannot be suspended through normal workflows
* Owner cannot be demoted through normal workflows
* ownership transfer requires a dedicated future workflow
* Owner bypasses normal permission checks while still being audited

The reusable Owner protection helper exists for future user and role management workflows.

## Admin APIs

The initial secure admin APIs are:

* `GET /api/v1/admin/me`
* `GET /api/v1/admin/navigation`
* `GET /api/v1/admin/permissions`

These endpoints return only information appropriate to the authenticated administrator.

## Audit Foundation

Privileged operations can record:

* actor
* action
* target
* timestamp
* IP address
* request ID
* result
* reason
* metadata

Audit viewing and export are not implemented in this sprint.

## Sensitive Actions

The `sensitive_action_requests` table prepares future workflows for:

* re-authentication
* MFA compatibility
* explicit confirmations
* expiring confirmation tokens

MFA itself is not implemented.

## Frontend Admin Routing

The frontend has a dedicated admin surface:

* `/admin`
* `/admin/dashboard`
* `/admin/settings`

The admin interface uses a separate shell, sidebar, loading state, unauthorized state, Admin Mode indicator, environment badge, and a clear switch back to User View.

## Development and Production

Development bootstrap can create a default Owner account through `python -m app.database.seed` using `ADMIN_OWNER_EMAIL` and `ADMIN_OWNER_PASSWORD` from local environment settings.

Production owner creation must be handled securely and should not rely on committed credentials.

## Future Extensions

Future admin sprints can add:

* user management
* role editor
* audit views
* data source registry
* ingestion dashboard
* analytics administration
* feature flags
* AI provider configuration
* billing and subscription management
