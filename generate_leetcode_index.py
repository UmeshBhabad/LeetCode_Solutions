#!/usr/bin/env python3
"""
generate_leetcode_index.py

Scans this repository for LeetSync-generated problem folders (named
"<number>-<problem-slug>"), extracts the problem title, difficulty, and
solution language from each, and rewrites the "Problems Solved" table
in README.md between the LEETCODE_TABLE_START / LEETCODE_TABLE_END
markers.

Run this any time after new problems have been synced, or wire it into
a GitHub Action to run automatically on every push (see the README
usage instructions for that setup).
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(REPO_ROOT, "README.md")

DSA_START_MARKER = "<!-- DSA_TABLE_START -->"
DSA_END_MARKER = "<!-- DSA_TABLE_END -->"

SQL_START_MARKER = "<!-- SQL_TABLE_START -->"
SQL_END_MARKER = "<!-- SQL_TABLE_END -->"

# Folder name pattern LeetSync uses: "11-container-with-most-water"
FOLDER_PATTERN = re.compile(r"^(\d+)-(.+)$")

# Map file extensions to display language names
LANGUAGE_MAP = {
    ".java": "Java",
    ".py": "Python",
    ".cpp": "C++",
    ".c": "C",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rb": "Ruby",
    ".cs": "C#",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".sql": "SQL",
}

# Extensions that count as "SQL" category for table grouping purposes
SQL_EXTENSIONS = {".sql"}

# Folders that are NOT LeetCode problem folders and should be skipped
SKIP_FOLDERS = {"Classwork", "Assignments", "LeetCode", ".git", ".github"}


def extract_title_and_difficulty(problem_readme_path):
    """Parse a LeetSync-generated per-problem README.md for the title,
    problem URL, and difficulty badge."""
    with open(problem_readme_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    title_match = re.search(
        r'<h2><a href="([^"]+)">([^<]+)</a></h2>', content
    )
    difficulty_match = re.search(
        r"Difficulty-(\w+)-", content
    )

    url = title_match.group(1) if title_match else None
    title = title_match.group(2) if title_match else "Unknown"
    difficulty = difficulty_match.group(1) if difficulty_match else "Unknown"

    return title, url, difficulty


def find_solution_language(folder_path):
    """Find the solution file in a problem folder (anything that isn't
    README.md) and map its extension to a display language, plus a
    coarse category ("SQL" or "DSA") used to split the summary tables."""
    for filename in os.listdir(folder_path):
        if filename == "README.md":
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in LANGUAGE_MAP:
            category = "SQL" if ext in SQL_EXTENSIONS else "DSA"
            return LANGUAGE_MAP[ext], category
    return "Unknown", "DSA"


def collect_problems():
    problems = []

    for entry in os.listdir(REPO_ROOT):
        full_path = os.path.join(REPO_ROOT, entry)

        if not os.path.isdir(full_path):
            continue
        if entry in SKIP_FOLDERS:
            continue

        match = FOLDER_PATTERN.match(entry)
        if not match:
            continue

        problem_number = int(match.group(1))
        readme_path = os.path.join(full_path, "README.md")

        if not os.path.isfile(readme_path):
            continue

        title, url, difficulty = extract_title_and_difficulty(readme_path)
        language, category = find_solution_language(full_path)

        problems.append({
            "number": problem_number,
            "title": title,
            "url": url,
            "difficulty": difficulty,
            "language": language,
            "category": category,
            "folder": entry,
        })

    problems.sort(key=lambda p: p["number"])
    return problems


def build_table_for_category(problems, category):
    filtered = [p for p in problems if p["category"] == category]

    if not filtered:
        return "<p><i>No problems solved in this category yet.</i></p>"

    rows = [
        "<table>",
        "<tr><th>#</th><th>Problem</th><th>Difficulty</th><th>Language</th></tr>",
    ]

    for p in filtered:
        rows.append(
            f'<tr><td>{p["number"]}</td>'
            f'<td><a href="{p["folder"]}/">{p["title"]}</a></td>'
            f'<td>{p["difficulty"]}</td>'
            f'<td>{p["language"]}</td></tr>'
        )

    rows.append("</table>")
    return "\n".join(rows)


def replace_section(content, start_marker, end_marker, table_html):
    if start_marker not in content or end_marker not in content:
        print(
            f"ERROR: Could not find {start_marker} / {end_marker} "
            "markers in README.md."
        )
        sys.exit(1)

    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{table_html}\n{end_marker}"
    return pattern.sub(replacement, content)


def update_readme(dsa_table_html, sql_table_html):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    content = replace_section(content, DSA_START_MARKER, DSA_END_MARKER, dsa_table_html)
    content = replace_section(content, SQL_START_MARKER, SQL_END_MARKER, sql_table_html)

    if content == original:
        print("No changes needed - tables are already up to date.")
        return False

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("README.md updated.")
    return True


if __name__ == "__main__":
    problems = collect_problems()
    dsa_table_html = build_table_for_category(problems, "DSA")
    sql_table_html = build_table_for_category(problems, "SQL")
    changed = update_readme(dsa_table_html, sql_table_html)

    if changed:
        print("Done. Review the changes, then commit and push:")
        print("  git add README.md")
        print('  git commit -m "docs: update problem tables"')
        print("  git push")