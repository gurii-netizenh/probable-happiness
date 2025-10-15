from flask import Flask, render_template, request, redirect, url_for
import random
import statistics
import csv
import os

app = Flask(__name__)


# Core logic functions (from CLI, adapted)
def get_mood_score(form_data):
    questions = [
        ("sleep", "How many hours did you sleep? (1-10 scale)", 0.2),
        ("exercise", "Did you exercise? (yes=5, no=1)", 0.25),
        ("connections", "Connected with friends/family? (1-5)", 0.3),  # Harvard factor
        ("gratitude", "Practiced gratitude? (yes=5, no=1)", 0.15),
        ("overall", "Overall day rating? (1-10)", 0.1),
    ]

    scores = []
    for field, _, weight in questions:
        try:
            score = float(form_data.get(field, 1))  # Default low
            scores.append(score * weight)
        except (ValueError, TypeError):
            scores.append(1 * weight)

    total = sum(scores) * 100
    return round(total, 1)


def get_tip(score):
    tips = {
        (0, 40): [
            "Rough day? Start small: List 3 things you're grateful for.",
            "Feeling low? A deep breath and one kind act can shift things.",
        ],
        (41, 70): [
            "Room to grow! Try a 10-min walk or call a buddy.",
            "Solid base—add a gratitude journal for that extra boost.",
        ],
        (71, 100): [
            "You're glowing! Keep nurturing those connections.",
            "High vibes! Share your win with someone to amplify it.",
        ],
    }
    for (low, high), tip_list in tips.items():
        if low <= score <= high:
            return random.choice(tip_list)
    return "Keep going—you've got this!"


def log_score(score):
    if not os.path.exists("happiness_log.csv"):
        with open("happiness_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["score", "date"])  # Header

    with open("happiness_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([score, random.randint(1, 365)])  # Dummy day-of-year for demo


def get_logs():
    if not os.path.exists("happiness_log.csv"):
        return []
    with open("happiness_log.csv", "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        score = get_mood_score(request.form)
        tip = get_tip(score)
        logged = False
        if request.form.get("log") == "on":
            log_score(score)
            logged = True
        return render_template("result.html", score=score, tip=tip, logged=logged)
    return render_template("index.html")


@app.route("/logs")
def logs():
    log_entries = get_logs()
    avg_score = (
        statistics.mean([float(entry["score"]) for entry in log_entries])
        if log_entries
        else 0
    )
    return render_template("logs.html", logs=log_entries, avg=avg_score)


if __name__ == "__main__":
    app.run(debug=True)
