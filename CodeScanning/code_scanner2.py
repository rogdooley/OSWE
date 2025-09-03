import argparse
import os
import re
import json
import yaml
import subprocess
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.table import Table
from collections import Counter, defaultdict

console = Console()
results = []

severity_colors = {
    "critical": "bold red",
    "high": "dark_orange",
    "medium": "yellow",
    "info": "blue",
}

severities = ["info", "medium", "high", "critical"]


def load_rules_from_multiple_yamls(yaml_files):
    merged_rules = {}
    for file in yaml_files:
        with open(file, "r") as f:
            rule_set = yaml.safe_load(f)
            for lang, lang_data in rule_set.items():
                if lang not in merged_rules:
                    merged_rules[lang] = {"extensions": set(), "rules": []}
                merged_rules[lang]["extensions"].update(lang_data.get("extensions", []))
                merged_rules[lang]["rules"].extend(lang_data.get("rules", []))
    for lang in merged_rules:
        merged_rules[lang]["extensions"] = list(merged_rules[lang]["extensions"])
    return merged_rules


def load_dir_list(file_path):
    if not file_path or not os.path.exists(file_path):
        return set()
    with open(file_path, "r") as f:
        return set(line.strip() for line in f if line.strip())


def get_git_tracked_files(base_dir):
    try:
        result = subprocess.run(
            ["git", "-C", base_dir, "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        return set(result.stdout.splitlines())
    except subprocess.CalledProcessError:
        console.print("[red]Git command failed. Is this a git repository?[/]")
        return set()


def load_exceptions_yaml(file_path):
    if not file_path or not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return yaml.safe_load(f).get("exclude_paths", [])


def is_excluded_by_pattern(filepath, exclude_patterns):
    for pattern in exclude_patterns:
        if re.fullmatch(pattern, str(filepath)):
            return True
    return False


def should_include(filepath, include_dirs, exclude_dirs, exclude_patterns):
    filepath = Path(filepath).resolve()
    if is_excluded_by_pattern(filepath, exclude_patterns):
        return False
    for ex in exclude_dirs:
        if ex in str(filepath):
            return False
    if not include_dirs:
        return True
    return any(inc in str(filepath) for inc in include_dirs)


def line_is_suppressed(line, rule_id=None):
    if "# nosec" in line or "# skip-scan" in line:
        return True
    if rule_id and f"# skip-{rule_id}" in line:
        return True
    return False


def find_matches(
    base_dir,
    rules,
    include_dirs,
    exclude_dirs,
    git_only,
    context_lines,
    min_severity,
    exclude_patterns,
):
    tracked_files = get_git_tracked_files(base_dir) if git_only else None
    pattern_counter = defaultdict(int)
    for root, _, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir)
            if git_only and rel_path not in tracked_files:
                continue
            if not should_include(
                full_path, include_dirs, exclude_dirs, exclude_patterns
            ):
                continue
            ext = Path(file).suffix
            for lang, patterns in rules.items():
                if "extensions" not in patterns:
                    continue
                if ext not in patterns["extensions"]:
                    continue
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        full_text = "".join(lines)
                        for rule in patterns["rules"]:
                            severity = rule.get("severity", "info")
                            if severities.index(severity) < severities.index(
                                min_severity
                            ):
                                continue
                            for match in re.finditer(
                                rule["pattern"],
                                full_text,
                                re.MULTILINE | re.DOTALL | re.IGNORECASE,
                            ):
                                lineno = full_text[: match.start()].count("\n") + 1
                                if lineno - 1 < len(lines) and line_is_suppressed(
                                    lines[lineno - 1], rule.get("id")
                                ):
                                    continue
                                snippet_lines = lines[
                                    max(0, lineno - 1 - context_lines) : min(
                                        len(lines), lineno + context_lines
                                    )
                                ]
                                code_snippet = "".join(snippet_lines).strip()
                                style = severity_colors.get(severity, "white")
                                text = Text(
                                    f"[{lang.upper()}] [{severity.upper()}] {full_path}:{lineno}: ",
                                    style=style,
                                )
                                text.append(code_snippet, style="yellow")
                                recommendation = rule.get("recommendation")
                                if recommendation:
                                    text.append(
                                        f"\nSuggestion: {recommendation}", style="cyan"
                                    )
                                console.print(text)
                                pattern_counter[rule["pattern"]] += 1
                                results.append(
                                    {
                                        "language": lang,
                                        "file": str(full_path),
                                        "line": lineno,
                                        "pattern": rule["pattern"],
                                        "description": rule.get("description", ""),
                                        "severity": severity,
                                        "category": rule.get("category", ""),
                                        "recommendation": recommendation or "",
                                        "code": code_snippet,
                                    }
                                )
                except Exception as e:
                    console.print(f"[red]Error reading {full_path}: {e}[/]")
    return pattern_counter


def print_summary_stats(results):
    counter = Counter(r["severity"] for r in results)
    console.print("\n[b]Scan Summary:[/b]")
    for level in severities[::-1]:
        count = counter.get(level, 0)
        color = severity_colors.get(level, "white")
        console.print(f"{level.title()}: [bold {color}]{count}[/]")


def print_top_patterns(pattern_counter, rules, top_n):
    pattern_meta = {}
    for lang, rule_data in rules.items():
        for rule in rule_data["rules"]:
            pattern_meta[rule["pattern"]] = {
                "description": rule.get("description", ""),
                "severity": rule.get("severity", ""),
            }

    top = sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
    table = Table(title=f"Top {top_n} Matched Patterns", show_lines=True)
    table.add_column("Pattern")
    table.add_column("Matches", justify="right")
    table.add_column("Severity")
    table.add_column("Description")
    for pattern, count in top:
        meta = pattern_meta.get(pattern, {})
        table.add_row(
            pattern, str(count), meta.get("severity", ""), meta.get("description", "")
        )
    console.print(table)


def determine_exit_code(results, threshold="high"):
    for r in results:
        if severities.index(r["severity"]) >= severities.index(threshold):
            return 1
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description="Advanced source code pattern scanner."
    )
    parser.add_argument("--directory", "-d", required=True, help="Directory to scan")
    parser.add_argument(
        "--rules", "-r", required=True, nargs="+", help="One or more YAML rule files"
    )
    parser.add_argument("--json-output", "-o", help="Write results to JSON file")
    parser.add_argument("--include", help="File listing directories to include")
    parser.add_argument("--exclude", help="File listing directories to exclude")
    parser.add_argument("--exceptions", help="YAML file with exclude_patterns list")
    parser.add_argument(
        "--git", action="store_true", help="Only scan files tracked by git"
    )
    parser.add_argument(
        "--context",
        type=int,
        default=0,
        help="Number of context lines to show before and after matches",
    )
    parser.add_argument(
        "--min-severity",
        choices=severities,
        default="info",
        help="Minimum severity to display",
    )
    parser.add_argument(
        "--fail-on",
        choices=severities,
        default="high",
        help="Exit with code 1 if findings at or above this severity",
    )
    parser.add_argument(
        "--top", type=int, default=0, help="Show top N patterns by match frequency"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rules = load_rules_from_multiple_yamls(args.rules)
    include_dirs = load_dir_list(args.include)
    exclude_dirs = load_dir_list(args.exclude)
    exclude_patterns = load_exceptions_yaml(args.exceptions)

    pattern_counter = find_matches(
        base_dir=args.directory,
        rules=rules,
        include_dirs=include_dirs,
        exclude_dirs=exclude_dirs,
        git_only=args.git,
        context_lines=args.context,
        min_severity=args.min_severity,
        exclude_patterns=exclude_patterns,
    )

    print_summary_stats(results)

    if args.top:
        print_top_patterns(pattern_counter, rules, args.top)

    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]Results written to {args.json_output}[/]")

    exit(determine_exit_code(results, threshold=args.fail_on))


if __name__ == "__main__":
    main()
