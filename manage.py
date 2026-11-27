#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    venv_dir = os.path.join(BASE_DIR, 'venv')
    venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
    if os.name == 'nt' and os.path.exists(venv_python):
        if os.path.normcase(os.path.abspath(sys.prefix)) != os.path.normcase(os.path.abspath(venv_dir)):
            import subprocess
            try:
                sys.exit(subprocess.call([venv_python] + sys.argv))
            except KeyboardInterrupt:
                sys.exit(0)

    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onizouka.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
