"""Single-command backend development launcher."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from scripts import bootstrap_dev  # noqa: E402


class DevLauncherError(RuntimeError):
    """Raised when the development launcher cannot continue safely."""


@dataclass(frozen=True)
class DevOptions:
    """Developer launcher options."""

    no_server: bool = False
    port: int = 8000
    skip_docker: bool = False
    skip_bootstrap: bool = False


def parse_args(argv: Sequence[str] | None = None) -> DevOptions:
    """Parse CLI arguments for the development launcher."""
    parser = argparse.ArgumentParser(
        description="Prepare and launch the InvestGuide backend development environment."
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Prepare Docker/database state but do not start FastAPI.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Uvicorn port for the backend development server.",
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Do not start Docker Compose; assume the database already exists.",
    )
    parser.add_argument(
        "--skip-bootstrap",
        action="store_true",
        help="Do not run Alembic migrations or development seeding.",
    )
    args = parser.parse_args(argv)
    return DevOptions(
        no_server=args.no_server,
        port=args.port,
        skip_docker=args.skip_docker,
        skip_bootstrap=args.skip_bootstrap,
    )


def run_command(args: Sequence[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run an operator command without shell interpolation."""
    return subprocess.run(list(args), cwd=cwd, check=check)


def require_docker_installed() -> None:
    """Fail clearly if Docker is not installed or not on PATH."""
    if shutil.which("docker") is None:
        raise DevLauncherError(
            "Docker is not installed or not available on PATH. "
            "Install Docker Desktop or another Docker Compose runtime, then retry."
        )


def require_docker_daemon() -> None:
    """Fail clearly if the Docker daemon is unavailable."""
    result = run_command(["docker", "info"], cwd=REPO_ROOT, check=False)
    if result.returncode != 0:
        raise DevLauncherError(
            "Docker is installed, but the Docker daemon is not running. "
            "Start Docker Desktop or your Docker service, then retry."
        )


def start_docker_compose() -> None:
    """Start the repository Docker Compose development services."""
    print("Starting Docker Compose services...")
    run_command(["docker", "compose", "up", "-d"], cwd=REPO_ROOT)


def wait_for_postgresql() -> None:
    """Wait for PostgreSQL to accept the configured application connection."""
    print("Waiting for PostgreSQL readiness...")
    if not bootstrap_dev.wait_for_database():
        raise DevLauncherError(
            "PostgreSQL did not become reachable with the configured DATABASE_URL. "
            "Check Docker health, port 5432, and backend/.env."
        )


def run_bootstrap() -> bootstrap_dev.BootstrapSummary:
    """Run migrations and development seed data through the existing bootstrap flow."""
    print("Running backend bootstrap...")
    return bootstrap_dev.bootstrap_development_database()


def start_uvicorn(port: int) -> int:
    """Start the FastAPI development server with Uvicorn."""
    print(f"Starting FastAPI on http://127.0.0.1:{port}")
    result = run_command(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", str(port)],
        cwd=BACKEND_DIR,
        check=False,
    )
    return int(result.returncode)


def launch_dev_environment(options: DevOptions) -> int:
    """Prepare and optionally launch the backend development environment."""
    print("InvestGuide backend development launcher")
    print(f"Repository: {REPO_ROOT}")

    if options.skip_docker:
        print("Skipping Docker Compose startup by request.")
    else:
        require_docker_installed()
        require_docker_daemon()
        start_docker_compose()
        wait_for_postgresql()

    summary: bootstrap_dev.BootstrapSummary | None = None
    if options.skip_bootstrap:
        print("Skipping backend bootstrap by request.")
    else:
        summary = run_bootstrap()

    print("Development environment prepared.")
    if summary is not None:
        print(f"Database connected: {summary.database_connected}")
        print(f"Migrations current: {summary.migrations_applied}")
        print(f"Seed data present: {summary.seed_completed}")
        print(f"Asset count: {summary.asset_count}")

    if options.no_server:
        print("No server started because --no-server was provided.")
        return 0

    return start_uvicorn(options.port)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    try:
        return launch_dev_environment(parse_args(argv))
    except (DevLauncherError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"Development launcher failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())