"""
Development tasks for the cad_widgets project.
Run with: invoke <task-name>
"""

from invoke import task


@task
def typecheck(c):
    """Run mypy type checking."""
    print("Running mypy type checker...")
    c.run("mypy src/cad_widgets", pty=True)


@task
def lint(c):
    """Run ruff linter."""
    print("Running ruff linter...")
    c.run("ruff check src tests examples", pty=True)


@task
def format(c):
    """Format code with ruff."""
    print("Formatting code with ruff...")
    c.run("ruff format src tests examples", pty=True)


@task
def test(c, verbose=False):
    """Run pytest tests."""
    print("Running tests...")
    cmd = "pytest"
    if verbose:
        cmd += " -v"
    c.run(cmd, pty=True)


@task
def test_cov(c):
    """Run pytest with coverage report."""
    print("Running tests with coverage...")
    c.run("pytest --cov=cad_widgets --cov-report=term-missing", pty=True)


@task(pre=[lint, typecheck, test])
def check(c):
    """Run all checks (lint, typecheck, test)."""
    print("All checks passed! ✓")


@task
def clean(c):
    """Clean up generated files."""
    print("Cleaning up...")
    c.run("rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache", pty=True)
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +", warn=True, pty=True)
    c.run("find . -type f -name '*.pyc' -delete", pty=True)
