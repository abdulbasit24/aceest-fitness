# ACEest Fitness & Gym – CI/CD Pipeline Project

> A Flask-based gym management REST API with a fully automated DevOps pipeline using Git, Docker, GitHub Actions, and Jenkins.

---

## Repository Structure

```
aceest-fitness/
├── app.py                          # Flask application
├── test_app.py                     # Pytest test suite
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── Jenkinsfile                     # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml                # GitHub Actions CI/CD workflow
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/programs` | List all fitness programs |
| GET | `/clients` | List all clients |
| POST | `/clients` | Add a new client |
| GET | `/clients/<name>` | Get a client by name |
| DELETE | `/clients/<name>` | Delete a client |
| GET | `/calories?weight=&program=` | Calculate daily calorie target |
| GET | `/bmi?weight=&height=` | Calculate BMI and category |

---

## Local Setup & Execution

### Prerequisites
- Python 3.12+
- Docker Desktop
- Git

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/aceest-fitness.git
cd aceest-fitness
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Flask application
```bash
python app.py
# App starts at http://localhost:5000
```

### 5. Test the API manually
```bash
# Health check
curl http://localhost:5000/

# List programs
curl http://localhost:5000/programs

# Add a client
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name":"Arjun","age":28,"weight":75,"height":175,"program":"Muscle Gain (MG) - PPL"}'

# Calculate BMI
curl "http://localhost:5000/bmi?weight=75&height=175"
```

---

## Running Tests Manually

```bash
# Run all tests with verbose output
pytest test_app.py -v

# Run with coverage report
pytest test_app.py -v --cov=app --cov-report=term-missing

# Run a specific test class
pytest test_app.py::TestCalculateBMI -v
```

---

## Docker

### Build the image
```bash
docker build -t aceest-fitness:latest .
```

### Run the container
```bash
docker run -p 5000:5000 aceest-fitness:latest
```

### Run tests inside the container
```bash
docker run --rm aceest-fitness:latest python -m pytest test_app.py -v
```

---

## Git Branching Strategy

```
main              ← stable production-ready code
├── develop       ← integration branch
│   ├── feature/flask-api
│   ├── feature/pytest-suite
│   ├── feature/docker
│   └── feature/ci-cd-pipeline
└── hotfix/       ← urgent production fixes
```

### Recommended commit message format
```
feat: add BMI calculation endpoint
fix: handle zero-weight edge case in calorie calculator
test: add integration tests for /clients DELETE route
ci: add Docker test stage to GitHub Actions workflow
docs: update README with Jenkins setup instructions
```

---

## GitHub Actions Pipeline

**File:** `.github/workflows/main.yml`  
**Trigger:** Every `push` and `pull_request` on any branch.

### Pipeline stages

```
push / pull_request
        │
        ▼
┌───────────────┐
│  Job 1: Lint  │  flake8 on app.py & test_app.py
└──────┬────────┘
       │ (on pass)
       ▼
┌───────────────┐
│  Job 2: Test  │  pytest with coverage report
└──────┬────────┘
       │ (on pass)
       ▼
┌────────────────┐
│  Job 3: Docker │  docker build + run tests inside container
└────────────────┘
```

Each job depends on the previous one passing — a lint failure prevents tests from running, and a test failure prevents the Docker build.

---

## Jenkins BUILD Pipeline

**File:** `Jenkinsfile`  
**Setup:**

1. Install Jenkins (locally or via Docker):
   ```bash
   docker run -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
   ```
2. In Jenkins → New Item → **Pipeline**
3. Under *Pipeline* → *Definition*: select **Pipeline script from SCM**
4. Set SCM to **Git** and enter your GitHub repository URL
5. Set *Script Path* to `Jenkinsfile`
6. Save and click **Build Now**

### Jenkins stage overview

| Stage | Action |
|-------|--------|
| Checkout | Pulls latest code from GitHub |
| Build Environment | Creates Python venv, installs deps |
| Lint | Runs flake8 syntax/style check |
| Unit Tests | Runs pytest, publishes JUnit XML report |
| Docker Build | Builds the Docker image |
| Docker Test | Runs pytest inside the container |
| Cleanup | Removes the venv |

Jenkins acts as a **secondary quality gate** — it validates that the code builds and tests cleanly in a controlled server environment, complementing the GitHub Actions cloud pipeline.

---

## Evaluation Checklist

| Criterion | Implementation |
|-----------|---------------|
| Application Integrity | REST API with 8 endpoints, input validation, error handling |
| VCS Maturity | Feature branches, conventional commit messages |
| Testing Coverage | 30+ test cases across unit and integration tests |
| Docker Efficiency | Multi-stage build, non-root user, slim base image |
| Jenkins BUILD | Declarative pipeline with 7 stages, JUnit report publishing |
| GitHub Actions | 3-job pipeline: Lint → Test → Docker, triggered on push/PR |
| Documentation | This README |