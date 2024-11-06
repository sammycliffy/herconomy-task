# Transaction Service API

This is a simple API built with Django and Django Rest Framework (DRF) to handle basic financial transactions between users. It supports operations like deposit, withdrawal, and transfer, with background task processing using Celery.

## Features

- **User registration and login** with JWT authentication.
- **Role-based access control** (admin, user).
- **Basic financial transactions**: deposit, withdrawal, and transfer.
- **Background task processing** with Celery (e.g., transaction verification).
- **Docker support** for easy setup and deployment.

## Prerequisites

Before you start, ensure you have the following installed on your local machine:

- Docker
- Docker Compose
- Python 3.8 or higher
- PostgreSQL (Docker will be used for database setup)

## Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/sammycliffy/herconomy-task.git
   cd finance_project
   ```

2. **Install required dependencies**:

   Make sure you have the necessary Python dependencies installed:

   ```bash
   pip install -r requirements.txt
   ```

   This will install Django, Django REST Framework (DRF), Celery, PostgreSQL, and other dependencies required for the application.

3. **Docker Setup**:

   The project includes a `Dockerfile` and `docker-compose.yml` for containerizing the Django app and PostgreSQL database.

   Build and start the Docker containers:

   ```bash
   docker-compose up --build
   ```

   This will:

   - Build the Docker containers for the Django app and PostgreSQL.
   - Start the services defined in `docker-compose.yml`.

4. **Run database migrations**:

   After the containers are up, apply database migrations:

   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser for the admin**:

   To create an admin user for the app:

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Celery Setup**:

   Celery is used to handle background task processing, such as transaction verification.

   Start the Celery worker:

   ```bash
   docker-compose exec web celery -A transaction_service worker --loglevel=info
   ```

   Start the Celery Beat scheduler (for periodic tasks, if applicable):

   ```bash
   docker-compose exec web celery -A transaction_service beat --loglevel=info
   ```

7. **Access the Django Admin**:

   After setting up the containers, you can access the Django admin panel at:

   ```bash
   http://localhost:8000/admin/
   ```

   Log in with the superuser credentials created during the `createsuperuser` step.

## API Endpoints

### Authentication

- **POST** `/api/users/register/`: User registration (JWT authentication) role can be admin or user.

  - Request Body: `{"username": "example", "email": "example@example.com", "password": "password", "role":"admin"}`

- **POST** `/api/users/login/`: User login (JWT authentication).
  - Request Body: `{"username": "example", "password": "password"}`
  - Response: Includes access and refresh JWT tokens.

### Transactions

- **GET** `/api/transactions/`: View all transactions for the authenticated user (Admin can view all transactions).
- **GET** `/api/transactions/?username=username`: View all transactions for a particular user (Admin can view all transactions for a particular user).

- **POST** `/api/transactions/`: Create a deposit transaction.
  - Request Body: `{"amount": 100, "transaction_type": "deposit"}`
- **POST** `/api/transactions/`: Create a withdrawal transaction.
  - Request Body: `{"amount": 50, "transaction_type": "withdrawal"}`
- **POST** `/api/transactions/`: Create a transfer transaction.
  - Request Body: `{"amount": 30, "transaction_type": "transfer", "recipient": "username_of_recipient"}`

## Role-Based Access

- **Admin**: Can view all transactions.
- **User**: Can only view and manage their own transactions.

## Docker Compose Commands

In the project directory, you’ll find the `docker-compose.yml` file that orchestrates the Django app and PostgreSQL database containers. Here's how to interact with it:

- **Start the application**:

  ```bash
  docker-compose up
  ```

- **Stop the application**:

  ```bash
  docker-compose down
  ```

- **Run migrations inside the Docker container**:

  ```bash
  docker-compose exec web python manage.py migrate
  ```

- **Access the Django shell**:

  ```bash
  docker-compose exec web python manage.py shell
  ```

## Testing

To test the API locally, you can use tools like Postman or Insomnia to send HTTP requests to the endpoints. Make sure to include the JWT Authorization header when accessing authenticated routes.

## Additional Commands

- **View logs** (for debugging or monitoring):

  ```bash
  docker-compose logs -f
  ```

- **Stop the Celery worker**:

  ```bash
  docker-compose exec web pkill -f 'celery worker'
  ```

- **Run the test suite** (if you have test cases set up):

  ```bash
  docker-compose exec web python manage.py test
  ```

## Conclusion

This setup allows you to run a complete transaction service with Django, DRF, and Celery for background processing, all containerized with Docker. The service supports basic financial operations like deposits, withdrawals, and transfers, with role-based access control and JWT authentication for secure API endpoints.
