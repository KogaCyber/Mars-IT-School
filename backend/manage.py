#!/usr/bin/env python
"""Django boshqaruv buyruqlari uchun kirish nuqtasi."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Django topilmadi. Virtual muhit faollashtirilganini tekshiring."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
