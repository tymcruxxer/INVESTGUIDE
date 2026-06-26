"""Single-command development launcher tests."""

import subprocess
import sys

from scripts import dev
from scripts.bootstrap_dev import BootstrapSummary


def test_missing_docker_returns_clear_failure(monkeypatch, capsys) -> None:
    """Launcher fails clearly when Docker is not installed."""
    monkeypatch.setattr(dev.shutil, "which", lambda command: None)

    assert dev.main(["--no-server"]) == 1
    assert "Docker is not installed" in capsys.readouterr().out


def test_docker_daemon_unavailable_returns_clear_failure(monkeypatch, capsys) -> None:
    """Launcher fails clearly when Docker daemon is not running."""
    monkeypatch.setattr(dev.shutil, "which", lambda command: "docker")

    def fake_run_command(args, *, cwd, check=True):
        return subprocess.CompletedProcess(args, returncode=1)

    monkeypatch.setattr(dev, "run_command", fake_run_command)

    assert dev.main(["--no-server"]) == 1
    assert "Docker daemon is not running" in capsys.readouterr().out


def test_docker_compose_command_construction(monkeypatch) -> None:
    """Docker Compose startup uses the repository root and expected command."""
    calls: list[tuple[list[str], object, bool]] = []

    def fake_run_command(args, *, cwd, check=True):
        calls.append((list(args), cwd, check))
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(dev, "run_command", fake_run_command)

    dev.start_docker_compose()

    assert calls == [(["docker", "compose", "up", "-d"], dev.REPO_ROOT, True)]


def test_wait_for_postgresql_success(monkeypatch) -> None:
    """PostgreSQL wait delegates to bootstrap readiness helper."""
    monkeypatch.setattr(dev.bootstrap_dev, "wait_for_database", lambda: True)

    dev.wait_for_postgresql()


def test_wait_for_postgresql_failure(monkeypatch) -> None:
    """PostgreSQL wait failure raises launcher error."""
    monkeypatch.setattr(dev.bootstrap_dev, "wait_for_database", lambda: False)

    try:
        dev.wait_for_postgresql()
    except dev.DevLauncherError as exc:
        assert "PostgreSQL did not become reachable" in str(exc)
    else:
        raise AssertionError("Expected DevLauncherError")


def test_bootstrap_command_delegates_to_existing_bootstrap(monkeypatch) -> None:
    """Launcher reuses the existing bootstrap command."""
    summary = BootstrapSummary(
        database_connected=True,
        migrations_applied=True,
        seed_completed=True,
        asset_count=9,
    )
    monkeypatch.setattr(dev.bootstrap_dev, "bootstrap_development_database", lambda: summary)

    assert dev.run_bootstrap() == summary


def test_uvicorn_command_construction(monkeypatch) -> None:
    """Uvicorn command uses backend cwd and configured port."""
    captured: dict[str, object] = {}

    def fake_run_command(args, *, cwd, check=True):
        captured["args"] = list(args)
        captured["cwd"] = cwd
        captured["check"] = check
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr(dev, "run_command", fake_run_command)

    assert dev.start_uvicorn(8001) == 0
    assert captured["args"] == [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        "8001",
    ]
    assert captured["cwd"] == dev.BACKEND_DIR
    assert captured["check"] is False


def test_no_server_behavior(monkeypatch) -> None:
    """--no-server prepares environment without starting Uvicorn."""
    calls: list[str] = []
    monkeypatch.setattr(dev, "require_docker_installed", lambda: calls.append("docker-installed"))
    monkeypatch.setattr(dev, "require_docker_daemon", lambda: calls.append("docker-daemon"))
    monkeypatch.setattr(dev, "start_docker_compose", lambda: calls.append("compose"))
    monkeypatch.setattr(dev, "wait_for_postgresql", lambda: calls.append("wait-db"))
    monkeypatch.setattr(
        dev,
        "run_bootstrap",
        lambda: calls.append("bootstrap")
        or BootstrapSummary(True, True, True, 9),
    )
    monkeypatch.setattr(dev, "start_uvicorn", lambda port: calls.append("uvicorn") or 0)

    assert dev.launch_dev_environment(dev.DevOptions(no_server=True)) == 0
    assert calls == ["docker-installed", "docker-daemon", "compose", "wait-db", "bootstrap"]


def test_skip_docker_behavior(monkeypatch) -> None:
    """--skip-docker bypasses Docker checks and startup."""
    calls: list[str] = []
    monkeypatch.setattr(dev, "require_docker_installed", lambda: calls.append("docker-installed"))
    monkeypatch.setattr(dev, "require_docker_daemon", lambda: calls.append("docker-daemon"))
    monkeypatch.setattr(dev, "start_docker_compose", lambda: calls.append("compose"))
    monkeypatch.setattr(dev, "wait_for_postgresql", lambda: calls.append("wait-db"))
    monkeypatch.setattr(
        dev,
        "run_bootstrap",
        lambda: calls.append("bootstrap")
        or BootstrapSummary(True, True, True, 9),
    )

    assert dev.launch_dev_environment(dev.DevOptions(no_server=True, skip_docker=True)) == 0
    assert calls == ["bootstrap"]


def test_skip_bootstrap_behavior(monkeypatch) -> None:
    """--skip-bootstrap bypasses migrations and seed command."""
    calls: list[str] = []
    monkeypatch.setattr(dev, "require_docker_installed", lambda: calls.append("docker-installed"))
    monkeypatch.setattr(dev, "require_docker_daemon", lambda: calls.append("docker-daemon"))
    monkeypatch.setattr(dev, "start_docker_compose", lambda: calls.append("compose"))
    monkeypatch.setattr(dev, "wait_for_postgresql", lambda: calls.append("wait-db"))
    monkeypatch.setattr(dev, "run_bootstrap", lambda: calls.append("bootstrap"))

    assert dev.launch_dev_environment(dev.DevOptions(no_server=True, skip_bootstrap=True)) == 0
    assert calls == ["docker-installed", "docker-daemon", "compose", "wait-db"]