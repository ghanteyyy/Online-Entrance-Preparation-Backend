# Online Entrance Preparation System (Backend)

Backend API for the **Online Entrance Preparation System**, a platform
designed to help students prepare for entrance examinations through
practice tests, question banks, performance analytics, and secure
authentication.

This backend provides REST APIs for user management, exam handling,
question banks, result evaluation, and administrative controls.

------------------------------------------------------------------------

## Tech Stack

  | Technology              | Purpose |
  | ----------------------- | ------------------------------ |
  | Django                  | Web framework |
  | Django REST Framework   | API development |
  | PostgreSQL              | Primary database |
  | JWT                     | Authentication |

------------------------------------------------------------------------

## Installation with Docker
**Requirements:** Docker and Docker Compose installed

### 1. Clone the repository

``` bash
git clone https://github.com/ghanteyyy/Online-Entrance-Preparation-Backend.git
cd Online-Entrance-Preparation-Backend
```

### 2. Build and start containers
``` bash
docker-compose up --build
```

### 3. Access the application
The backend will be avilable at:

``` bash
http://localhost:8000/
```

### 4. Stop containers
``` bash
docker-compose down
```

## Running without Docker

### 1. Clone the repository

``` bash
git clone https://github.com/ghanteyyy/Online-Entrance-Preparation-Backend.git
cd Online-Entrance-Preparation-Backend
```

### 2. Create a virtual environment

``` bash
python -m venv .venv
```

#### Activate environment

Windows:

``` bash
.venv\Scripts\activate
```

Linux / Mac:

``` bash
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Migrate Databases

``` bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the server

``` bash
python manage.py runserver
```
