# User Profile API with Redis Caching

## Description

This Python Flask application provides a RESTful API for managing user profiles. It stores user data in a MySQL database and utilizes Redis for caching to improve performance and reduce database load. The API allows you to create, retrieve, and update user profiles.

## Prerequisites

Before you can run this application, you need to have the following installed and configured:

* **Python 3.x:** Ensure you have Python 3 installed on your system (if running locally).
* **pip:** Python package installer (usually included with Python) if running locally.
* **Docker:** If you plan to run the application using Docker, you need to have Docker installed on your system.
* **Docker Compose:** If using Docker Compose (recommended for managing multi-container Docker applications), ensure it is installed.

## Installation

You can run this application either locally (without Docker) or using Docker.

### Local Installation (without Docker)

1.  **Clone the repository (if applicable):**
    ```bash
    git clone your_repository_url
    cd your_project_directory
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install dependencies:**
    Create a `requirements.txt` file in your project directory with the following content:
    ```
    redis
    mysql-connector-python
    Flask
    ```
    Then, install the dependencies using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    You need to configure the application by setting environment variables for the MySQL and Redis connections. You can do this directly in your terminal before running the application, or by creating a `.env` file.

    **Example of setting environment variables in the terminal:**
    ```bash
    export REDIS_HOST="your_redis_host" (default: redis)
    export REDIS_PORT=your_redis_port (default: 6379)
    export MYSQL_HOST="your_mysql_host" (default: mysql)
    export MYSQL_USER="your_mysql_user" (default: your_user)
    export MYSQL_PASSWORD="your_mysql_password" (default: Liberty10)
    export MYSQL_DATABASE="your_mysql_database" (default: plague_rats_wip)
    ```
    Replace the placeholder values with your actual MySQL and Redis server details.

### Docker Installation

If you have Docker and Docker Compose installed, you can run the entire application stack (API, MySQL, Redis) using the provided `docker-compose.yml` file.

1.  **Clone the repository (if applicable):**
    ```bash
    git clone your_repository_url
    cd your_project_directory
    ```

2.  **Place the `Dockerfile` and `docker-compose.yml` in the root of your project directory.**

3.  **Run Docker Compose:**
    ```bash
    docker-compose up -d --build
    ```
    This command will build the Docker image for the application and start the MySQL, Redis, and application containers in the background.

## Configuration

The application is configured using environment variables. When running with Docker Compose, these environment variables are defined in the `docker-compose.yml` file for each service. When running locally, you need to set them in your environment.

**Environment Variables:**

* `REDIS_HOST`: The hostname or IP address of your Redis server. Defaults to `redis` when not using Docker, and is set to `redis` (the name of the Redis service) when using Docker Compose.
* `REDIS_PORT`: The port number of your Redis server. Defaults to `6379`.
* `MYSQL_HOST`: The hostname or IP address of your MySQL server. Defaults to `mysql` when not using Docker, and is set to `mysql` (the name of the MySQL service) when using Docker Compose.
* `MYSQL_USER`: The username for connecting to your MySQL database. Defaults to `your_user` when not using Docker, and is set to `root` in the `docker-compose.yml`.
* `MYSQL_PASSWORD`: The password for the MySQL user. Defaults to `Liberty10` in both local setup and `docker-compose.yml`.
* `MYSQL_DATABASE`: The name of the MySQL database to use. Defaults to `plague_rats_wip` in both local setup and `docker-compose.yml`.

## Database Setup (Docker)

When using Docker Compose, the MySQL service is initialized with the database name `plague_rats_wip` and a root user with the password `Liberty10` as defined in the `docker-compose.yml` file and the `MYSQL_ROOT_PASSWORD` and `MYSQL_DATABASE` environment variables.

The `volumes` section in the `docker-compose.yml` mounts `./mysql_data` to `/var/lib/mysql` inside the container, which means your database data will be persisted even if you stop or remove the container.

The line `- ./.venv/application/init:/docker-entrypoint-initdb.d/` suggests you might have SQL initialization scripts in the `./.venv/application/init` directory that will be executed when the MySQL container starts. Ensure your `players` table creation script is located there if you are relying on this for automatic setup. Otherwise, you might need to connect to the MySQL container and create the table manually.

**Example SQL to create the `players` table (if not using initialization scripts):**

```sql
CREATE TABLE players (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(255)
);