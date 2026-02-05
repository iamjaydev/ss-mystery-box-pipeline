import csv
import re
import os
import sys
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT.joinpath("state").mkdir(exist_ok=True)
REPO_ROOT.joinpath("data").mkdir(exist_ok=True)

REWARD_MAP = {
    "hoverboard": "hoverboard",
    "hoverboards": "hoverboard",
    "headstart": "headstart",
    "head start": "headstart",
    "coin": "coins",
    "coins": "coins",
    "score booster": "scoreBooster",
    "score boosters": "scoreBooster",
    "ulg": "key",
}


def clean_rewards_csv(input_csv):
    base, _ = os.path.splitext(input_csv)
    cleaned_csv = Path(f"{base}_cleaned.csv")

    if cleaned_csv.exists():
        return cleaned_csv

    with open(input_csv, newline="", encoding="utf-8") as infile, \
            open(cleaned_csv, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(["qty", "type"])

        for row in reader:
            raw = row.get("reward", "")
            if not raw:
                writer.writerow([0, ""])
                continue

            text = raw.lower().strip()
            text = re.sub(r"[^a-z0-9 ]", "", text)
            text = re.sub(r"\s+", " ", text)

            m = re.search(r"(\d+)", text)
            qty = int(m.group(1)) if m else 1

            reward_type = ""
            for k, v in REWARD_MAP.items():
                if k in text:
                    reward_type = v
                    break

            if not reward_type:
                text = re.sub(r"\d+", "", text).strip()
                parts = text.split(" ")
                reward_type = parts[0] + "".join(
                    p.capitalize() for p in parts[1:]
                ) if parts else ""

            writer.writerow([qty, reward_type])

    return cleaned_csv


def analyze_and_plot(cleaned_csv):
    reward_counts = Counter()
    coin_values = Counter()
    hoverboard_values = Counter()

    PRICE_MAP = {
        "hoverboard": 300,
        "headstart": 2000,
        "coins": 1,
        "scoreBooster": 3000,
        "key": 0,
    }

    COST_PER_ROW = 500

    row_count = 0
    item_value = Counter()

    with open(cleaned_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_count += 1
            qty = int(row["qty"])
            t = row["type"]

            reward_counts[t] += 1
            item_value[t] += qty * PRICE_MAP.get(t, 0)

            if t == "coins":
                coin_values[qty] += 1
            elif t == "hoverboard":
                hoverboard_values[qty] += 1

    total_cost = COST_PER_ROW * row_count
    total_gain = sum(item_value.values())
    net = total_gain - total_cost

    print(f"Invested amount: {total_cost}")
    print(f"Total gained value: {total_gain}")

    if net > 0:
        print(f"Profit: {net}")
    elif net < 0:
        print(f"Loss: {-net}")
    else:
        print("Break-even")

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    labels = list(reward_counts.keys())
    values = list(reward_counts.values())
    probs = [v / sum(values) for v in values]

    axes[0, 0].pie(
        probs,
        labels=labels,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        startangle=90,
    )
    axes[0, 0].set_title("Reward Types")

    axes[0, 1].bar(labels, probs)
    axes[0, 1].set_title("Reward Probabilities")
    axes[0, 1].set_ylim(0, max(probs) * 1.2)

    coin_labels = sorted(coin_values)
    coin_probs = [
        coin_values[v] / sum(coin_values.values())
        for v in coin_labels
    ]

    axes[1, 0].bar([str(v) for v in coin_labels], coin_probs)
    axes[1, 0].set_title("Coin Value Distribution")

    hb_labels = sorted(hoverboard_values)
    hb_probs = [
        hoverboard_values[v] / sum(hoverboard_values.values())
        for v in hb_labels
    ]

    axes[1, 1].bar([str(v) for v in hb_labels], hb_probs)
    axes[1, 1].set_title("Hoverboard Quantity Distribution")

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "No csv path provided.\n"
            "Usage: python visualize_results.py <path_to_rewards_csv>")

    input_csv = Path(sys.argv[1]).expanduser().resolve()
    cleaned = clean_rewards_csv(input_csv)
    analyze_and_plot(cleaned)
