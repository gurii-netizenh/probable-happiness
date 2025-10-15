from datetime import datetime
import csv
import os

from flask import current_app
from models import Log, db


# Scoring (from before, normalized)
def get_mood_score(form_data):
    questions = [
        ("sleep", 0.2, 10),
        ("exercise", 0.25, 5),
        ("connections", 0.3, 5),
        ("gratitude", 0.15, 5),
        ("overall", 0.1, 10),
    ]
    weighted_scores = []
    for field, weight, max_scale in questions:
        try:
            raw_score = float(form_data.get(field, 0))
            normalized = max(0, min(1, raw_score / max_scale))
            weighted_scores.append(normalized * weight)
        except (ValueError, TypeError):
            weighted_scores.append(0)
    return round(sum(weighted_scores) * 100, 1)


# Tips (unchanged)
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
            from random import choice

            return choice(tip_list)
    return "Keep going—you've got this!"


# Log score to DB
def log_score(user_id, score):
    log = Log(score=score, user_id=user_id)
    db.session.add(log)
    db.session.commit()


# Get user logs for charts
def get_user_logs(user_id):
    logs = Log.query.filter_by(user_id=user_id).order_by(Log.date).all()
    return [{"date": l.date.strftime("%Y-%m-%d"), "score": l.score} for l in logs]


# Export CSV
def export_logs(user_id, filename="logs.csv"):
    logs = get_user_logs(user_id)
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Score"])
        writer.writerows([(log["date"], log["score"]) for log in logs])
    return filename


# Send email (optional)
from flask_mail import Mail, Message


def send_summary(user_email, avg_score):
    if not current_app.config["MAIL_USERNAME"]:
        return
    msg = Message(
        "Your Weekly Happiness Summary",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email],
    )
    msg.body = f"Your avg score: {avg_score}. Keep shining! 🌟"
    Mail.send(msg)
