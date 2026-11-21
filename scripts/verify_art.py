#!/usr/bin/env python3
"""Validate gallery artwork: plain ASCII, no tabs/ANSI, bounded width."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'


def check(path: Path) -> list[str]:
    errors = []
    raw = path.read_bytes()
    if not raw.endswith(b'\n'):
        errors.append('missing final newline')
    if b'\r' in raw:
        errors.append('CR / CRLF found: use LF newlines')
    if b'\x1b' in raw:
        errors.append('ANSI escape character found')
    try:
        content = raw.decode('ascii')
    except UnicodeDecodeError:
        return errors + ['non-ASCII character found']
    max_width = 48 if 'mobile' in path.relative_to(ART).parts else 120
    for i, line in enumerate(content.splitlines(), 1):
        if '\t' in line:
            errors.append(f'line {i}: tab found')
        if any(ord(ch) < 32 or ord(ch) > 126 for ch in line):
            errors.append(f'line {i}: nonprintable ASCII character')
        if len(line) > max_width:
            errors.append(f'line {i}: {len(line)} columns > {max_width}')
    return errors


def main() -> int:
    files = sorted(ART.rglob('*.txt'))
    if not files:
        print('ERROR: no artwork found')
        return 1
    failures = 0
    for path in files:
        issues = check(path)
        label = str(path.relative_to(ROOT))
        if issues:
            failures += len(issues)
            for issue in issues:
                print(f'FAIL {label}: {issue}')
        else:
            print(f'PASS {label}')
    print(f'{len(files)} artworks checked; {failures} issue(s).')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
