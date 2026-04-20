import argparse
from pathlib import Path

ROOT = Path('/Users/heomin/.hermes/hermes-agent/tinker-atropos')


def parse_fill_sheet(text: str) -> dict[str, dict[str, str]]:
    data: dict[str, dict[str, str]] = {}
    current_project = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith('## '):
            current_project = line[3:].strip()
            data.setdefault(current_project, {})
            continue
        if not current_project or not line.startswith('- '):
            continue
        label, sep, value = line[2:].partition(':')
        if not sep:
            continue
        data[current_project][label.strip()] = value.strip()
    return data


def apply_project_values(metrics_path: Path, values: dict[str, str]):
    lines = metrics_path.read_text(encoding='utf-8').splitlines()
    updated = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            label, sep, _ = stripped[2:].partition(':')
            if sep and label.strip() in values:
                prefix = line[: len(line) - len(line.lstrip())]
                updated.append(f"{prefix}- {label.strip()}: {values[label.strip()]}")
                continue
        updated.append(line)
    metrics_path.write_text('\n'.join(updated) + '\n', encoding='utf-8')


def apply_fill_sheet(root: Path, date: str, sheet_path: Path):
    data = parse_fill_sheet(sheet_path.read_text(encoding='utf-8'))
    for project, values in data.items():
        metrics_path = root / 'feedback' / date / project / 'metrics.md'
        if metrics_path.exists():
            apply_project_values(metrics_path, values)
    return data


def main():
    parser = argparse.ArgumentParser(description='Apply a bulk feedback fill sheet into per-project metrics files.')
    parser.add_argument('--date', default='2026-04-17')
    parser.add_argument('--sheet', required=True)
    args = parser.parse_args()

    apply_fill_sheet(root=ROOT, date=args.date, sheet_path=Path(args.sheet))
    print(Path(args.sheet))


if __name__ == '__main__':
    main()
