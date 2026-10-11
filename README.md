# ACEest Fitness Gym

ACEest Fitness Gym is a desktop-based fitness management application built with Python and Tkinter. It helps personal trainers or gym staff manage client records, track weekly adherence, log workouts, generate AI-style training plans, and export membership/client reports.

## Features

- Secure login for admins/users
- Client profile management
- Program generation based on fitness goals
- Weekly adherence tracking and visual charts
- Workout logging
- PDF client report generation
- Membership status checks
- SQLite-based local data persistence

## Project Structure

- `app.py` — main application logic and GUI
- `tests/test_app.py` — Pytest suite covering critical app behavior
- `Dockerfile` — container setup for local or CI execution
- `.github/workflows/ci.yml` — GitHub Actions automation for tests and Docker build
- `Jenkinsfile` — Jenkins pipeline for dependency installation, tests, and Docker image build
- `requirements.txt` — Python dependencies

## Local Setup

### Prerequisites

- Python 3.11+
- pip
- Git
- Optional: Docker

### 1. Clone the repository

```bash
git clone <repository-url>
cd ACEest-Fitness-Gym
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

The application will open a login window. Use the default admin account:

- Username: `admin`
- Password: `admin`

## Manual Test Execution

To run the test suite locally:

```bash
python -m pytest tests/test_app.py -q
```

You can also run the full directory test suite if additional tests are added later:

```bash
python -m pytest -q
```

## Docker Usage

### Build the Docker image

```bash
docker build -t aceest-fitness .
```

### Run the container

```bash
docker run --rm aceest-fitness
```

This container is configured to run the project tests by default.

## CI/CD Overview

### GitHub Actions integration

This repository includes a GitHub Actions workflow in `.github/workflows/ci.yml`.

The workflow:

1. Triggers on push to `main` or `master`, and on pull requests.
2. Checks out the repository.
3. Sets up Python 3.11.
4. Installs dependencies from `requirements.txt`.
5. Runs the Pytest suite using:
   ```bash
   python -m pytest tests/test_app.py -q
   ```
6. Builds the Docker image using:
   ```bash
   docker build -t aceest-fitness .
   ```

This ensures every code change is validated automatically before merge.

### Jenkins pipeline

The root-level `Jenkinsfile` defines a Declarative Pipeline with these stages:

1. **Checkout** the configured SCM revision.
2. **Set Up Python Environment** by creating a virtual environment with `python3`.
3. **Build** by upgrading pip and installing dependencies from `requirements.txt`.
4. **Run Tests** with pytest and generate `reports/pytest.xml`.
5. **Build Docker Image** as `aceest-fitness`.

Jenkins polls the configured SCM every minute (`* * * * *`) and triggers the
pipeline when it detects changes. Progress messages are printed as the stages
run, and the JUnit test report is published even if a test fails.

To run it, configure a Linux Jenkins agent with Python 3.11 or newer available
as `python3`, plus Docker, and grant the agent permission to access the Docker
daemon. Ensure the Jenkins Git and JUnit plugins are installed. Create a
Pipeline job pointing to this repository and select **Pipeline script from
SCM**; Jenkins will discover the `Jenkinsfile` from the repository root.

## Notes

- The app uses a local SQLite database file named `aceest_fitness.db`.
- The database is created automatically when the app starts.
- This project is intended for learning, local development, and CI/CD demonstration purposes.

## License

This project is provided for educational and demonstration purposes.
