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

### Jenkins integration logic

A Jenkins pipeline can be added to perform similar validation in an on-premise or self-hosted environment. The typical Jenkins flow would be:

1. Pull the source code from Git.
2. Set up the Python environment.
3. Install dependencies.
4. Run the test suite.
5. Build the Docker image.
6. Optionally deploy or archive the image.

Example Jenkins pipeline steps:

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/ACEest-Fitness-Gym.git'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'python -m pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'python -m pytest tests/test_app.py -q'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness .' 
            }
        }
    }
}
```

## Notes

- The app uses a local SQLite database file named `aceest_fitness.db`.
- The database is created automatically when the app starts.
- This project is intended for learning, local development, and CI/CD demonstration purposes.

## License

This project is provided for educational and demonstration purposes.
