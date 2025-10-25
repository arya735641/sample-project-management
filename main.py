#!/usr/bin/env python3
"""
grade_calculator.py

Usage:
- Interactive mode (default): run without args and follow prompts.
- CSV mode: python grade_calculator.py --csv students.csv
  CSV must have header: name,assignment,midterm,final (or match the component names you provide)

The script has default components and weights:
  - assignment: 40%
  - midterm:    30%
  - final:      30%

You can change weights interactively. Weights must sum to 100.
"""

import csv
import argparse
import sys

# Default weight configuration (percent)
DEFAULT_WEIGHTS = {
    "assignment": 40,
    "midterm": 30,
    "final": 30,
}

# Letter grade scale: (min_percentage, letter)
GRADE_SCALE = [
    (90, "A"),
    (85, "A-"),
    (80, "B+"),
    (75, "B"),
    (70, "B-"),
    (65, "C+"),
    (60, "C"),
    (50, "D"),
    (0,  "F"),
]


def percentage_to_letter(pct: float) -> str:
    """Convert numeric percentage to letter grade using GRADE_SCALE."""
    for min_pct, letter in GRADE_SCALE:
        if pct >= min_pct:
            return letter
    return "F"


def calculate_weighted_percentage(scores: dict, weights: dict) -> float:
    """
    Compute weighted percentage.

    scores: dict of component -> score (0-100)
    weights: dict of component -> weight (percent, sum should be 100)
    """
    total = 0.0
    for comp, weight in weights.items():
        score = float(scores.get(comp, 0))
        total += score * (weight / 100.0)
    return total


def parse_csv(input_path: str, components: list):
    """Read CSV file and yield (name, scores_dict)."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_fields = ["name"] + components
        for field in required_fields:
            if field not in reader.fieldnames:
                raise ValueError(f"CSV is missing required column: {field}")
        for row in reader:
            name = row["name"]
            scores = {comp: float(row[comp]) for comp in components}
            yield name, scores


def prompt_weights(defaults: dict) -> dict:
    """Prompt user to accept or change default weights. Return weights dict summing to 100."""
    print("Current/default weights (percent):")
    for k, v in defaults.items():
        print(f"  {k}: {v}%")
    ans = input("Would you like to change weights? (y/N): ").strip().lower()
    if ans != "y":
        return defaults.copy()

    weights = {}
    for comp in defaults:
        while True:
            val = input(f"Enter weight for '{comp}' (current {defaults[comp]}): ").strip()
            try:
                if val == "":
                    w = defaults[comp]
                else:
                    w = float(val)
                if w < 0:
                    raise ValueError()
                weights[comp] = w
                break
            except ValueError:
                print("Please enter a non-negative number (or leave blank).")
    total = sum(weights.values())
    if abs(total - 100.0) > 1e-6:
        print(f"Weights sum to {total}, but must sum to 100. Normalizing proportionally.")
        if total == 0:
            raise ValueError("All weights are zero; can't normalize.")
        weights = {k: (v / total) * 100.0 for k, v in weights.items()}
    return weights


def interactive_mode(weights: dict):
    """Interactively input multiple students' scores."""
    components = list(weights.keys())
    n = input("How many students to enter? (leave blank to enter until 'q'): ").strip()
    if n == "":
        # indefinite mode
        print("Enter student data. Type 'q' as name to quit.")
        while True:
            name = input("Student name (or 'q' to quit): ").strip()
            if name.lower() == "q":
                break
            scores = {}
            for comp in components:
                while True:
                    s = input(f"  {comp} score (0-100): ").strip()
                    try:
                        score = float(s)
                        if not (0 <= score <= 100):
                            raise ValueError()
                        scores[comp] = score
                        break
                    except ValueError:
                        print("  Enter a number between 0 and 100.")
            pct = calculate_weighted_percentage(scores, weights)
            letter = percentage_to_letter(pct)
            print(f"  => {name}: {pct:.2f}% -> {letter}")
    else:
        try:
            count = int(n)
        except ValueError:
            print("Invalid number, aborting.")
            return
        for i in range(count):
            name = input(f"Student #{i+1} name: ").strip()
            scores = {}
            for comp in components:
                while True:
                    s = input(f"  {comp} score (0-100): ").strip()
                    try:
                        score = float(s)
                        if not (0 <= score <= 100):
                            raise ValueError()
                        scores[comp] = score
                        break
                    except ValueError:
                        print("  Enter a number between 0 and 100.")
            pct = calculate_weighted_percentage(scores, weights)
            letter = percentage_to_letter(pct)
            print(f"  => {name}: {pct:.2f}% -> {letter}")


def csv_mode(path: str, weights: dict):
    """Process CSV and print grades."""
    components = list(weights.keys())
    try:
        for name, scores in parse_csv(path, components):
            pct = calculate_weighted_percentage(scores, weights)
            letter = percentage_to_letter(pct)
            print(f"{name}: {pct:.2f}% -> {letter}")
    except Exception as e:
        print("Error processing CSV:", e)


def main():
    parser = argparse.ArgumentParser(description="Grade calculator (weighted).")
    parser.add_argument("--csv", help="Path to CSV file with student scores (header: name and components).")
    args = parser.parse_args()

    try:
        weights = prompt_weights(DEFAULT_WEIGHTS)
    except Exception as e:
        print("Error with weights:", e)
        sys.exit(1)

    if args.csv:
        csv_mode(args.csv, weights)
    else:
        interactive_mode(weights)


if __name__ == "__main__":
    main()
