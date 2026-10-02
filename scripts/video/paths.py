"""Relative-path helpers that keep records portable."""
from __future__ import annotations

import copy
import os
from pathlib import Path


def relative_path(path, base):
    """Return a path relative to base; reject another drive before saving."""
    try:
        return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()
    except ValueError as error:
        raise ValueError('Keep assets and records on the same drive so relative paths can reference them.') from error


def portable_probe(info, base):
    result = copy.deepcopy(info)
    if 'filename' in result.get('format', {}):
        result['format']['filename'] = relative_path(result['format']['filename'], base)
    return result


def portable_command(command, base):
    """Convert command file arguments to paths relative to the record destination."""
    result = list(command)
    executable = Path(result[0])
    if executable.is_absolute() or executable.parent != Path('.'):
        result[0] = relative_path(executable, base)
    for index, token in enumerate(command[:-1]):
        if token == '-i':
            result[index + 1] = relative_path(command[index + 1], base)
    result[-1] = relative_path(command[-1], base)
    return result
