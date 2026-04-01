from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------- In-memory data store (mirrors ACEest DB logic) ----------
clients = {}

PROGRAMS = {
    "Fat Loss (FL) - 3 day":  {"factor": 22, "desc": "3-day full-body fat loss"},
    "Fat Loss (FL) - 5 day":  {"factor": 24, "desc": "5-day split, higher volume fat loss"},
    "Muscle Gain (MG) - PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy"},
    "Beginner (BG)":          {"factor": 26, "desc": "3-day simple beginner full-body"},
}


def calculate_calories(weight: float, program: str) -> int | None:
    """Return daily calorie target based on weight and program factor."""
    prog = PROGRAMS.get(program)
    if prog and weight > 0:
        return int(weight * prog["factor"])
    return None


def calculate_bmi(weight: float, height_cm: float) -> dict | None:
    """Return BMI value and category. Returns None on invalid input."""
    if weight <= 0 or height_cm <= 0:
        return None
    h_m = height_cm / 100.0
    bmi = round(weight / (h_m ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return {"bmi": bmi, "category": category}


# ---------- Routes ----------

@app.route("/")
def index():
    return jsonify({"message": "ACEest Fitness API", "status": "running"})


@app.route("/programs", methods=["GET"])
def get_programs():
    return jsonify({"programs": list(PROGRAMS.keys())})


@app.route("/clients", methods=["GET"])
def get_clients():
    return jsonify({"clients": list(clients.values())})


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400

    program = data.get("program", "")
    if program and program not in PROGRAMS:
        return jsonify({"error": f"Unknown program: {program}"}), 400

    weight  = float(data.get("weight", 0))
    height  = float(data.get("height", 0))
    age     = int(data.get("age", 0))

    calories = calculate_calories(weight, program)
    bmi_info = calculate_bmi(weight, height)

    client = {
        "name":     name,
        "age":      age,
        "weight":   weight,
        "height":   height,
        "program":  program,
        "calories": calories,
        "bmi":      bmi_info,
    }
    clients[name] = client
    return jsonify({"message": "Client saved", "client": client}), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    client = clients.get(name)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify({"client": client})


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    if name not in clients:
        return jsonify({"error": "Client not found"}), 404
    clients.pop(name)
    return jsonify({"message": f"Client '{name}' deleted"})


@app.route("/calories", methods=["GET"])
def calories_endpoint():
    weight  = request.args.get("weight", type=float)
    program = request.args.get("program", "")
    if weight is None:
        return jsonify({"error": "weight query param required"}), 400
    result = calculate_calories(weight, program)
    if result is None:
        return jsonify({"error": "Invalid weight or unknown program"}), 400
    return jsonify({"calories": result})


@app.route("/bmi", methods=["GET"])
def bmi_endpoint():
    weight = request.args.get("weight", type=float)
    height = request.args.get("height", type=float)
    if weight is None or height is None:
        return jsonify({"error": "weight and height query params required"}), 400
    result = calculate_bmi(weight, height)
    if result is None:
        return jsonify({"error": "Invalid weight or height"}), 400
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
    