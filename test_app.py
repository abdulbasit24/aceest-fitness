import pytest
from app import app, calculate_calories, calculate_bmi, clients, PROGRAMS


# ---------- Fixtures ----------

@pytest.fixture
def client():
    """Flask test client with fresh in-memory state."""
    app.config["TESTING"] = True
    clients.clear()
    with app.test_client() as c:
        yield c
    clients.clear()


# ---------- Unit Tests: Pure Functions ----------

class TestCalculateCalories:
    def test_fat_loss_3day(self):
        assert calculate_calories(70, "Fat Loss (FL) - 3 day") == 1540

    def test_muscle_gain(self):
        assert calculate_calories(80, "Muscle Gain (MG) - PPL") == 2800

    def test_beginner(self):
        assert calculate_calories(60, "Beginner (BG)") == 1560

    def test_zero_weight_returns_none(self):
        assert calculate_calories(0, "Beginner (BG)") is None

    def test_unknown_program_returns_none(self):
        assert calculate_calories(70, "Unknown Program") is None

    def test_fractional_weight(self):
        result = calculate_calories(72.5, "Fat Loss (FL) - 3 day")
        assert result == int(72.5 * 22)


class TestCalculateBMI:
    def test_normal_bmi(self):
        result = calculate_bmi(70, 175)
        assert result["bmi"] == 22.9
        assert result["category"] == "Normal"

    def test_underweight(self):
        result = calculate_bmi(45, 170)
        assert result["category"] == "Underweight"

    def test_overweight(self):
        result = calculate_bmi(85, 170)
        assert result["category"] == "Overweight"

    def test_obese(self):
        result = calculate_bmi(120, 170)
        assert result["category"] == "Obese"

    def test_zero_weight_returns_none(self):
        assert calculate_bmi(0, 170) is None

    def test_zero_height_returns_none(self):
        assert calculate_bmi(70, 0) is None

    def test_bmi_value_rounded(self):
        result = calculate_bmi(70, 175)
        assert isinstance(result["bmi"], float)


# ---------- Integration Tests: API Endpoints ----------

class TestIndexRoute:
    def test_status_ok(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_response_contains_status(self, client):
        data = client.get("/").get_json()
        assert data["status"] == "running"


class TestProgramsRoute:
    def test_returns_all_programs(self, client):
        data = client.get("/programs").get_json()
        assert len(data["programs"]) == len(PROGRAMS)

    def test_fat_loss_in_list(self, client):
        data = client.get("/programs").get_json()
        assert "Fat Loss (FL) - 3 day" in data["programs"]


class TestClientsRoute:
    def test_get_empty_clients(self, client):
        r = client.get("/clients")
        assert r.status_code == 200
        assert client.get("/clients").get_json()["clients"] == []

    def test_add_valid_client(self, client):
        payload = {
            "name": "Arjun",
            "age": 28,
            "weight": 75,
            "height": 175,
            "program": "Muscle Gain (MG) - PPL"
        }
        r = client.post("/clients", json=payload)
        assert r.status_code == 201
        data = r.get_json()
        assert data["client"]["name"] == "Arjun"
        assert data["client"]["calories"] == 2625

    def test_add_client_missing_name(self, client):
        r = client.post("/clients", json={"weight": 70})
        assert r.status_code == 400

    def test_add_client_no_body(self, client):
        r = client.post("/clients", data="not json",
                        content_type="application/json")
        assert r.status_code == 400

    def test_add_client_unknown_program(self, client):
        r = client.post("/clients", json={"name": "X", "program": "Ghost Program"})
        assert r.status_code == 400

    def test_get_existing_client(self, client):
        client.post("/clients", json={"name": "Priya", "weight": 60,
                                       "height": 160, "program": "Beginner (BG)"})
        r = client.get("/clients/Priya")
        assert r.status_code == 200
        assert r.get_json()["client"]["name"] == "Priya"

    def test_get_missing_client_404(self, client):
        r = client.get("/clients/Ghost")
        assert r.status_code == 404

    def test_delete_client(self, client):
        client.post("/clients", json={"name": "Ravi", "weight": 80,
                                       "program": "Fat Loss (FL) - 3 day"})
        r = client.delete("/clients/Ravi")
        assert r.status_code == 200
        assert client.get("/clients/Ravi").status_code == 404

    def test_delete_nonexistent_client(self, client):
        r = client.delete("/clients/Nobody")
        assert r.status_code == 404

    def test_bmi_included_in_client(self, client):
        client.post("/clients", json={"name": "Meena", "weight": 65,
                                       "height": 165, "program": "Beginner (BG)"})
        data = client.get("/clients/Meena").get_json()
        assert data["client"]["bmi"] is not None
        assert "category" in data["client"]["bmi"]


class TestCaloriesEndpoint:
    def test_valid_query(self, client):
        r = client.get("/calories?weight=70&program=Beginner (BG)")
        assert r.status_code == 200
        assert r.get_json()["calories"] == 1820

    def test_missing_weight(self, client):
        r = client.get("/calories?program=Beginner (BG)")
        assert r.status_code == 400

    def test_unknown_program(self, client):
        r = client.get("/calories?weight=70&program=Ghost")
        assert r.status_code == 400


class TestBMIEndpoint:
    def test_valid_bmi(self, client):
        r = client.get("/bmi?weight=70&height=175")
        assert r.status_code == 200
        assert "bmi" in r.get_json()

    def test_missing_height(self, client):
        r = client.get("/bmi?weight=70")
        assert r.status_code == 400

    def test_missing_weight(self, client):
        r = client.get("/bmi?height=175")
        assert r.status_code == 400