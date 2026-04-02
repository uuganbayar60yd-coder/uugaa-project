from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-12345")


# -----------------------------
# Home
# -----------------------------
GAMES = [
    {
        "title": "1. Санасан тоог таах",
        "slug": "guess-number",
        "description": "1-100 хооронд компьютерийн санасан тоог таа."
    },
    {
        "title": "2. Хайч, Чулуу, Даавуу",
        "slug": "rps",
        "description": "Компьютертэй өрсөлдөнө."
    },
    {
        "title": "3. Зураг таах",
        "slug": "image-guess",
        "description": "Зураг хараад зөв хариултыг сонго."
    },
    {
        "title": "4. Фибоначчигийн таавар",
        "slug": "fibonacci",
        "description": "Дараагийн тоог зөв ол."
    },
    {
        "title": "5. Төөрдөг байшин",
        "slug": "maze",
        "description": "⬅️ ⬆️ ⬇️ ➡️ товчоор гарц руу хүр."
    },
]

@app.route("/")
def home():
    return render_template("index.html", games=GAMES)


# -----------------------------
# 1. Guess the number
# -----------------------------
@app.route("/guess-number", methods=["GET", "POST"])
def guess_number():
    if "guess_target" not in session:
        session["guess_target"] = random.randint(1, 100)
        session["guess_tries"] = 0
        session["guess_message"] = "1-100 хооронд тоо оруулна уу."

    if request.method == "POST":
        if "reset" in request.form:
            session["guess_target"] = random.randint(1, 100)
            session["guess_tries"] = 0
            session["guess_message"] = "Шинэ тоглоом эхэллээ. Дахин таагаарай."
            return redirect(url_for("guess_number"))

        raw = request.form.get("guess", "").strip()
        try:
            num = int(raw)
            session["guess_tries"] += 1
            target = session["guess_target"]

            if num < target:
                session["guess_message"] = f"{num} хэт бага байна."
            elif num > target:
                session["guess_message"] = f"{num} хэт их байна."
            else:
                tries = session["guess_tries"]
                session["guess_message"] = f"🎉 Зөв! {tries} оролдлогоор таалаа."
        except ValueError:
            session["guess_message"] = "Зөвхөн бүхэл тоо оруулна уу."

        return redirect(url_for("guess_number"))

    return render_template(
        "guess_number.html",
        message=session.get("guess_message", ""),
        tries=session.get("guess_tries", 0)
    )


# -----------------------------
# 2. Rock Paper Scissors
# -----------------------------
@app.route("/rps", methods=["GET", "POST"])
def rps():
    result = None
    player_choice = None
    computer_choice = None
    score = session.get("rps_score", {"win": 0, "lose": 0, "draw": 0})

    if request.method == "POST":
        if "reset" in request.form:
            session["rps_score"] = {"win": 0, "lose": 0, "draw": 0}
            return redirect(url_for("rps"))

        player_choice = request.form.get("choice")
        choices = ["Хайч", "Чулуу", "Даавуу"]
        computer_choice = random.choice(choices)

        if player_choice == computer_choice:
            result = "Тэнцлээ"
            score["draw"] += 1
        elif (
            (player_choice == "Хайч" and computer_choice == "Даавуу") or
            (player_choice == "Чулуу" and computer_choice == "Хайч") or
            (player_choice == "Даавуу" and computer_choice == "Чулуу")
        ):
            result = "Та хожлоо!"
            score["win"] += 1
        else:
            result = "Компьютер хожлоо."
            score["lose"] += 1

        session["rps_score"] = score

    return render_template(
        "rps.html",
        result=result,
        player_choice=player_choice,
        computer_choice=computer_choice,
        score=score
    )


# -----------------------------
# 3. Image guess
# -----------------------------
IMAGE_QUESTIONS = [
    {"file": "apple.svg", "answer": "Алим", "options": ["Алим", "Жүрж", "Гүзээлзгэнэ", "Лийр"]},
    {"file": "cat.svg", "answer": "Муур", "options": ["Нохой", "Муур", "Туулай", "Үнэг"]},
    {"file": "car.svg", "answer": "Машин", "options": ["Дугуй", "Машин", "Онгоц", "Галт тэрэг"]},
    {"file": "house.svg", "answer": "Байшин", "options": ["Сургууль", "Мод", "Байшин", "Шүхэр"]},
    {"file": "star.svg", "answer": "Од", "options": ["Нар", "Сар", "Од", "Цэцэг"]},
]

@app.route("/image-guess", methods=["GET", "POST"])
def image_guess():
    if "image_question" not in session:
        session["image_question"] = random.choice(IMAGE_QUESTIONS)
        session["image_score"] = session.get("image_score", 0)

    feedback = None
    q = session["image_question"]

    if request.method == "POST":
        chosen = request.form.get("option")
        if chosen == q["answer"]:
            feedback = "🎉 Зөв хариуллаа!"
            session["image_score"] = session.get("image_score", 0) + 1
        else:
            feedback = f"Буруу. Зөв хариулт: {q['answer']}"

        session["image_question"] = random.choice(IMAGE_QUESTIONS)
        q = session["image_question"]

    return render_template(
        "image_guess.html",
        question=q,
        feedback=feedback,
        score=session.get("image_score", 0)
    )


# -----------------------------
# 4. Fibonacci puzzle
# -----------------------------
def make_fib_question():
    fib = [0, 1]
    for _ in range(8):
        fib.append(fib[-1] + fib[-2])

    start = random.randint(0, 4)
    seq = fib[start:start+5]
    answer = fib[start+5]
    return {"sequence": seq, "answer": answer}

@app.route("/fibonacci", methods=["GET", "POST"])
def fibonacci():
    if "fib_question" not in session:
        session["fib_question"] = make_fib_question()
        session["fib_score"] = 0

    feedback = None
    q = session["fib_question"]

    if request.method == "POST":
        if "reset" in request.form:
            session["fib_score"] = 0
            session["fib_question"] = make_fib_question()
            return redirect(url_for("fibonacci"))

        raw = request.form.get("answer", "").strip()
        try:
            ans = int(raw)
            if ans == q["answer"]:
                feedback = "✅ Зөв!"
                session["fib_score"] = session.get("fib_score", 0) + 1
            else:
                feedback = f"❌ Буруу. Зөв хариулт: {q['answer']}"
            session["fib_question"] = make_fib_question()
            q = session["fib_question"]
        except ValueError:
            feedback = "Бүхэл тоо оруулна уу."

    return render_template(
        "fibonacci.html",
        question=q,
        feedback=feedback,
        score=session.get("fib_score", 0)
    )


# -----------------------------
# 5. Maze page
# -----------------------------
@app.route("/maze")
def maze():
    return render_template("maze.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
