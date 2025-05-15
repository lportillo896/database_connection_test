# Plague Rats API - README

This document provides a summary of the core files that make up the Plague Rats API application.

## Overview

The Plague Rats API is a backend application built using Flask and SQLAlchemy, designed to manage data for the Plague Rats game. It interacts with a MySQL database for persistent storage and utilizes Redis for caching to enhance performance. The application is containerized using Docker for easy deployment and management.

## File Summaries

### `app.py`

This file serves as the main entry point for the Flask application. It initializes the Flask app instance, registers the API routes defined in `getroutes.py`, configures the connection to the MySQL database using environment variables, and starts the Flask development server. It also defines a basic welcome route.

### `db_utils.py`

This utility file handles the setup and management of database connections. It retrieves connection details for both the MySQL database and the Redis server from environment variables. It creates a Redis client instance and a SQLAlchemy engine for interacting with the MySQL database. Additionally, it defines the base class for SQLAlchemy models and creates a session maker for database operations.

### `docker-compose.yml`

This Docker Compose configuration file defines and orchestrates the multi-container Docker application. It sets up three services:
- `mysql`: A MySQL database container with configured root password, database, port mapping, data volume, and initialization scripts. It also includes a health check.
- `redis`: A Redis server container with defined port mapping.
- `app`: The Flask application container, built from the current directory. It specifies environment variables for database and Redis connections, defines dependencies on the other services, maps the application port, mounts the application code, and sets a restart policy. All services are connected to a common network (`appnet`).

### `getroutes.py`

This file defines the API routes for the Plague Rats application using a Flask blueprint. It handles incoming HTTP GET requests to retrieve data from the MySQL database (using SQLAlchemy) and leverages Redis for caching to improve performance. The routes allow fetching lists and details of various game entities such as players, colonies, battles, items, and achievements. It includes logic for querying the database, serializing the results (to JSON), and potentially handling basic errors.

### `models.py`

This file defines the SQLAlchemy models that represent the tables in the MySQL database. Each class within this file maps to a specific database table (e.g., `Battle`, `Colony`, `Player`). The models specify the columns of each table with their data types and constraints, as well as define relationships between different tables using SQLAlchemy's ORM capabilities. Many models include a `serialize()` method to convert object instances into dictionaries for API responses.

### `requirements.txt`

This file lists the Python packages that are necessary for the Plague Rats API application to run correctly. These dependencies include:
- `redis`: A Python client for interacting with the Redis server.
- `Flask`: The micro web framework used to build the API.
- `SQLAlchemy`: A SQL toolkit and Object-Relational Mapper for database interaction.
- `PyMySQL`: A MySQL client library for Python.
- `cryptography`: A library providing cryptographic functionalities.

This file is used by `pip` to install all the required libraries and their dependencies.