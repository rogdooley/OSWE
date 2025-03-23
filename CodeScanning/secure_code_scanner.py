import argparse
import os
import re
import json
import yaml
import subprocess
from pathlib import Path
from rich.console import Console
from rich.text import Text

console = Console()
results = []


def load_rules_from_yaml(yaml_file):
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def load_dir_list(file_path):
    if not file_path or not os.path.exists(file_path):
        return set()
    with open(file_path, 'r') as f:
        return set(line.strip() for line in f if line.strip())


def get_git_tracked_files(base_dir):
    try:
        result = subprocess.run(['git', '-C', base_dir, 'ls-files'], capture_output=True, text=True, check=True)
        return set(result.stdout.splitlines())
    except subprocess.CalledProcessError:
        console.print("[red]Git command failed. Is this a git repository?[/]")
        return set()


def should_include(filepath, include_dirs, exclude_dirs):
    filepath = Path(filepath).resolve()
    for ex in exclude_dirs:
        if ex in str(filepath):
            return False
    if not include_dirs:
        return True
    return any(inc in str(filepath) for inc in include_dirs)


def find_matches(base_dir, rules, include_dirs, exclude_dirs, git_only):
    tracked_files = get_git_tracked_files(base_dir) if git_only else None
    for root, _, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            if git_only and rel_path not in tracked_files:
                continue
            if not should_include(full_path, include_dirs, exclude_dirs):
                continue
            ext = Path(file).suffix
            for lang, patterns in rules.items():
                if 'extensions' not in patterns:
                    continue
                if ext not in patterns['extensions']:
                    continue
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for lineno, line in enumerate(f, start=1):
                            for rule in patterns['rules']:
                                if re.search(rule['pattern'], line):
                                    text = Text(f"[{lang.upper()}] {full_path}:{lineno}: ", style="cyan")
                                    text.append(line.strip(), style="yellow")
                                    console.print(text)
                                    results.append({
                                        'language': lang,
                                        'file': str(full_path),
                                        'line': lineno,
                                        'pattern': rule['pattern'],
                                        'description': rule.get('description', ''),
                                        'code': line.strip()
                                    })
                except Exception as e:
                    console.print(f"[red]Error reading {full_path}: {e}[/]")


def parse_args():
    parser = argparse.ArgumentParser(description="Advanced source code pattern scanner.")
    parser.add_argument('--directory', '-d', required=True, help="Directory to scan")
    parser.add_argument('--rules', '-r', required=True, help="YAML rule file")
    parser.add_argument('--json-output', '-o', help="Write results to JSON file")
    parser.add_argument('--include', help="File listing directories to include")
    parser.add_argument('--exclude', help="File listing directories to exclude")
    parser.add_argument('--git', action='store_true', help="Only scan files tracked by git")
    return parser.parse_args()


def main():
    args = parse_args()
    rules = load_rules_from_yaml(args.rules)
    include_dirs = load_dir_list(args.include)
    exclude_dirs = load_dir_list(args.exclude)

    find_matches(
        base_dir=args.directory,
        rules=rules,
        include_dirs=include_dirs,
        exclude_dirs=exclude_dirs,
        git_only=args.git
    )

    if args.json_output:
        with open(args.json_output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]Results written to {args.json_output}[/]")


if __name__ == "__main__":
    main()
