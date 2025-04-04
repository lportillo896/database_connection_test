import json
import logging
import os
import time

import mysql.connector
import redis
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "your_user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Liberty10")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "plague_rats_wip")

# Redis Configuration
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# MySQL Configuration
MYSQL_CONFIG = {
    'host': MYSQL_HOST,
    'port': 3306,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'database': MYSQL_DATABASE
}

app = Flask(__name__)

def connect_with_retry(config, max_retries=5, retry_delay=2):
    """Connects to MySQL with retry logic."""
    connection = None
    for i in range(max_retries):
        try:
            connection = mysql.connector.connect(**config)
            logger.debug(f"Successfully connected to MySQL on attempt {i + 1}")
            return connection
        except mysql.connector.Error as err:
            logger.error(f"Attempt {i + 1} failed to connect to MySQL: {err}")
            if i < max_retries - 1:
                time.sleep(retry_delay)
    logger.error("Failed to connect to MySQL after multiple retries.")
    return None

class DatabaseConnection:
    """A context manager for handling MySQL database connections."""
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __enter__(self):
        self.connection = connect_with_retry(self.config)
        if self.connection is None:
            raise Exception("Failed to connect to the database after multiple retries.")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.debug("MySQL connection closed.")

"""@app.route("/env")
def get_env():
    Returns environment variables related to database and Redis.
    return jsonify({
        "MYSQL_HOST": os.environ.get("MYSQL_HOST"),
        "MYSQL_USER": os.environ.get("MYSQL_USER"),
        "MYSQL_PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "MYSQL_DATABASE": os.environ.get("MYSQL_DATABASE"),
        "REDIS_HOST": os.environ.get("REDIS_HOST")
    })"""

@app.route("/")
def welcome():
    """Returns a simple welcome message."""
    return "<p>Welcome.  Query a user by typing a User ID in the address bar.<p>"

@app.route("/user/create/<user_id>/<username>", methods=['POST'])
def create_user_profile(user_id,username):
    """Creates a user profile in MySQL and caches it in Redis."""
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400

    redis_key = f"user:{user_id}"
    profile = {"id": user_id, "name": username}
    profile_json = json.dumps(profile)

    try:
        with DatabaseConnection(MYSQL_CONFIG) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO players (player_id, player_name) VALUES (%s, %s)"
            cursor.execute(query, (user_id, username))
            connection.commit()
            logger.info(f"User {user_id} created in MySQL.")

            # Write to Redis cache (write-through)
            redis_client.set(redis_key, profile_json, ex=60)
            logger.info(f"User {user_id} cached in Redis.")
            return jsonify(profile), 201  # Return 201 Created
    except mysql.connector.Error as err:
        logger.error(f"MySQL error creating user {user_id}: {err}")
        return jsonify({"error": "Database error creating user"}), 500
    except Exception as e:
        logger.error(f"Error creating user {user_id}: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@app.route("/users/<user_id>")
def get_user_profile(user_id):
    """Retrieves user profile using user_id, caching in Redis."""
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400

    redis_key = f"user:{user_id}"

    # Check Redis cache
    cached_profile = redis_client.get(redis_key)
    if cached_profile:
        logger.info(f"Retrieved user:{user_id} from Redis cache")
        return cached_profile.decode('utf-8')

    # If not in cache, fetch from MySQL
    try:
        with DatabaseConnection(MYSQL_CONFIG) as connection:
            cursor = connection.cursor()
            query = "SELECT player_name FROM players WHERE player_id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                profile = result[0]
                # Store in Redis with an expiration (e.g., 60 seconds)
                redis_client.set(redis_key, profile, ex=60)
                logger.info(f"Retrieved user:{user_id} from MySQL and cached")
                return jsonify({"player_name": profile})
            else:
                logger.warning(f"User with ID {user_id} not found in MySQL.")
                return jsonify({"error": "User not found"}), 404

    except mysql.connector.Error as err:
        logger.error(f"MySQL error while fetching user {user_id}: {err}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching user {user_id}: {e}")
        return jsonify({"error": "Failed to connect to the database"}), 503

@app.route("/users/<user_id>", methods=['PUT'])
def update_user_profile(user_id):
    """Updates an existing user's profile in MySQL and updates the cache in Redis."""
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400

    # Get the updated data from the request (assuming JSON body)
    try:
        updated_data = request.get_json()
        updated_username = updated_data.get('username')
        if not updated_username:
            return jsonify({"error": "Missing 'username' in request body"}), 400
    except Exception as e:
        logger.error(f"Error parsing request body for user update: {e}")
        return jsonify({"error": "Invalid request body"}), 400

    redis_key = f"user:{user_id}"

    try:
        with DatabaseConnection(MYSQL_CONFIG) as connection:
            cursor = connection.cursor()
            query = "UPDATE players SET player_name = %s WHERE player_id = %s"
            cursor.execute(query, (updated_username, user_id))
            connection.commit()

            if cursor.rowcount > 0:
                logger.info(f"User {user_id} updated in MySQL to username: {updated_username}")
                updated_profile = {"id": user_id, "name": updated_username}
                redis_client.set(redis_key, json.dumps(updated_profile), ex=60)
                logger.info(f"User {user_id} cache updated in Redis to: {updated_username}")
                return jsonify(updated_profile)
            else:
                logger.warning(f"User with ID {user_id} not found in MySQL for update.")
                return jsonify({"error": "User not found"}), 404

    except mysql.connector.Error as err:
        logger.error(f"MySQL error updating user {user_id}: {err}")
        return jsonify({"error": "Database error updating user"}), 500
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return jsonify({"error": "Failed to update user"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
