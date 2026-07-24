# Ingestion Operations Centre Architecture

## Purpose

Sprint 055 introduces the Ingestion Operations Centre: the administrative control plane for defining, observing, and controlling future ingestion jobs.

It does not execute live ingestion, call external APIs, scrape websites, run background workers, schedule jobs, parse documents, or import data. It records job definitions, execution history, metrics, failures, freshness state, and operator requests so future workers can plug into an observable foundation.

## Operational Philosophy

* Operations before automation.
* Observable systems over hidden processes.
* Immutable execution history.
* Configuration over hard-coded behavior.
* Security-first administration.
* Audit every operator action.

## Job Lifecycle

```text
Pending
  -> Queued
  -> Running
  -> Completed
        or Failed
        or Cancelled
        or Paused
```

Sprint 055 records operator requests such as run, retry, pause, resume, and cancel. It does not hand work to a queue or worker.

Each job stores:

* source registry reference;
* job name and type;
* description;
* configuration JSON;
* execution mode;
* priority;
* max retries;
* timeout;
* concurrency limit;
* future queue name;
* enabled/manual-only state;
* freshness state;
* last successful run and last run timestamps.

## Execution Lifecycle

Executions are append-only operational history rows. They record:

* job;
* status;
* trigger type;
* operator when manually requested;
* retry count;
* start and finish timestamps;
* duration;
* request id;
* result summary.

Manual actions create execution records where appropriate. Existing completed execution records should not be edited by future workers; corrections should create new history or failure records.

## Metrics Model

Each execution can have one metric row containing:

* rows processed;
* records inserted;
* records updated;
* duplicates detected;
* records rejected;
* warnings;
* errors;
* duration;
* throughput.

Sprint 055 seed data uses simulated metrics for UI validation only.

## Failure Model

Execution failures are normalized and linked to executions. Supported categories:

* network;
* authentication;
* parsing;
* validation;
* rate limit;
* timeout;
* internal;
* unknown.

Each failure records error message, safe stack-trace placeholder, retry eligibility, and failure timestamp.

## Freshness Model

Jobs track source freshness through:

* fresh;
* aging;
* stale;
* expired;
* unknown.

Future ingestion workers should update freshness based on successful execution timestamps and source-specific freshness windows from the Data Source Registry.

## Data Source Registry Integration

Every ingestion job belongs to one registered source. Future workers should discover work by joining:

```text
Source Registry
  -> Supported Capabilities
  -> Ingestion Job
  -> Connector Registry (future)
  -> Parser
  -> Worker
  -> Execution History
```

The frontend and intelligence layers should not depend on connector names or source-specific branching.

## Admin APIs

All APIs require JWT authentication and RBAC permissions.

Read permission: `ingestion.read`.
Manage permission: `ingestion.manage`.

Endpoints:

* `GET /api/v1/admin/ingestion/jobs`
* `GET /api/v1/admin/ingestion/jobs/{id}`
* `POST /api/v1/admin/ingestion/jobs`
* `PATCH /api/v1/admin/ingestion/jobs/{id}`
* `POST /api/v1/admin/ingestion/jobs/{id}/run`
* `POST /api/v1/admin/ingestion/jobs/{id}/retry`
* `POST /api/v1/admin/ingestion/jobs/{id}/pause`
* `POST /api/v1/admin/ingestion/jobs/{id}/resume`
* `POST /api/v1/admin/ingestion/jobs/{id}/cancel`
* `GET /api/v1/admin/ingestion/executions`
* `GET /api/v1/admin/ingestion/executions/{id}`

## Audit Integration

Every create, update, run, retry, pause, resume, and cancel request records an audit event with:

* actor;
* action;
* target job;
* previous state;
* new state;
* reason;
* timestamp;
* request id when provided.

## Future Worker Architecture

Future automation should consume the operations-centre job registry without changing the admin UI contract:

```text
Ingestion Job Registry
  -> Queue Adapter
  -> Connector Registry
  -> Source Connector
  -> Parser
  -> Normalizer
  -> Validator
  -> Importer
  -> Execution Metrics
  -> Failure Tracking
  -> Freshness Update
```

Celery, Redis, cron, APScheduler, or cloud queues can be introduced later behind this contract. Sprint 055 intentionally avoids coupling the product to any specific execution engine.

## Explicit Non-Goals

Sprint 055 does not implement live scraping, live APIs, background workers, Redis queues, Celery, cron execution, AI processing, connector execution, data parsing, or a scheduling engine.
