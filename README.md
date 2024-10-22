My Flask Web Application Messenger
This is a web application built with Flask, Docker, Redis, Nginx and PostgreSQL. Below are the steps to set up and run the application locally.

Getting Started
1. Clone the Repository

2. .env file
In the root directory of the project, put a .env file with the necessary environment variables.

3. Build and Run Docker Containers
Build and start the application using Docker Compose: docker-compose up --build

This command will:

Build the Docker images for the web application and the database.
Start the containers for the web app, database, and any other necessary services.
The application will be accessible at http://localhost:8000.

4. Apply Database Migrations
Once the Docker containers are up and running, apply the database migrations to ensure the database schema is up to date:
docker-compose exec web flask db upgrade


5. Access the Application
The web application should now be running on port 8000. Open your browser and go to:
http://localhost:8000


6. Stopping the Application
To stop the application, run the following command:
docker-compose down
