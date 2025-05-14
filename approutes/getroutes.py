import json
import logging

from flask import jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db_utils import redis_client, redis
from models import Achievement, Battle, BattleParticipant, Colony, ColonyProgress, ColonyRat, DayNightTime, Economy, \
    EffectType, Equipment, GameEvent, Item, Plague, PlagueAffected, PlagueRat, Player, PlayerAchievement, \
    PlayerEquipment, Severity, Stats, Weather, WeatherEffects, Base, engine

logger = logging.getLogger(__name__)

app = Blueprint('get_routes', __name__) # app is a Blueprint

#Get App Routes
@app.route("/achievements", methods=["GET"])
def get_achievements():
    """Retrieves all achievements, caching the results in Redis."""

    cache_key = "all_achievements"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving data from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving data from database and caching in Redis")
        session = Session(bind=engine)
        try:
            achievements = session.query(Achievement).all()
            if achievements:  # Check if the list is not empty
                logger.info(type(achievements[0]))
                result = [achievement.serialize() for achievement in achievements]
                json_result = json.dumps(result)
                redis_client.set(cache_key, json_result, ex=3600)
                return jsonify(result)
            else:
                return jsonify([])  # Return an empty list if no achievements found
        except SQLAlchemyError as e:  # Use SQLAlchemyError for database errors
            logger.error(f"Error retrieving achievements: {e}")
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()


@app.route("/achievements/<int:achievement_id>", methods=["GET"])
def get_achievement(achievement_id):
    """Retrieves a specific achievement by ID, using Redis for caching."""
    cache_key = f"achievement:{achievement_id}"

    try:
        # Try to get the achievement from Redis cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("Retrieving data from Redis cache")
            return jsonify(json.loads(cached_data.decode('utf-8')))
        else:
            print("Retrieving data from database and caching in Redis")
            session = Session(bind=engine)
            try:
                achievement = session.query(Achievement).filter_by(
                    achievement_id=achievement_id
                ).first()
                if achievement:
                    serialized_achievement = achievement.serialize()
                    json_result = json.dumps(serialized_achievement)
                    # Store in Redis cache with expiry
                    redis_client.set(cache_key, json_result, ex=3600)
                    return jsonify(serialized_achievement)
                else:
                    return jsonify({"error": "Achievement not found"}), 404
            except SQLAlchemyError as e:  # Use SQLAlchemyError for database errors
                logger.error(f"Error retrieving achievement {achievement_id}: {e}")
                session.rollback()
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            achievement = session.query(Achievement).filter_by(
                achievement_id=achievement_id
            ).first()
            if achievement:
                return jsonify(achievement.serialize())
            else:
                return jsonify({"error": "Achievement not found"}), 404
        except SQLAlchemyError as db_e:  # Use SQLAlchemyError for database errors and rename e
            logger.error(f"Database error after Redis failure: {db_e}")
            session.rollback()
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()


@app.route("/battles/<int:battle_id>", methods=['GET'])
def get_battle(battle_id):
    """Retrieves a battle by ID, using Redis for caching."""
    cache_key = f"battle:{battle_id}"

    try:
        # Try to get the battle data from Redis cache
        cached_battle = redis_client.get(cache_key)
        if cached_battle:
            logger.info(f"Cache hit for battle ID: {battle_id}")
            return jsonify(json.loads(cached_battle.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            battle = session.query(Battle).filter_by(battle_id=battle_id).first()
            if battle:
                serialized_battle = battle.serialize()
                # Store the data in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_battle), ex=3600)
                logger.info(f"Cache miss for battle ID: {battle_id}, stored in cache.")
                return jsonify(serialized_battle)
            else:
                return jsonify({"error": "Battle not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            battle = session.query(Battle).filter_by(battle_id=battle_id).first()
            if battle:
                return jsonify(battle.serialize())
            else:
                return jsonify({"error": "Battle not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()


@app.route('/battle_participants/<int:participant_id>', methods=['GET'])
def get_battle_participant(participant_id):
    """Retrieves a battle participant by their ID, using Redis for caching."""

    cache_key = f"battle_participant:{participant_id}"

    try:
        # Try to get the participant from Redis cache
        cached_participant = redis_client.get(cache_key)
        if cached_participant:
            logger.info(f"Cache hit for battle participant ID: {participant_id}")
            return jsonify(json.loads(cached_participant.decode("utf-8")))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            participant = session.query(BattleParticipant).filter_by(participant_id=participant_id).first()
            if participant:
                serialized_participant = participant.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_participant), ex=3600)
                logger.info(f"Cache miss for battle participant ID: {participant_id}, stored in cache.")
                return jsonify(serialized_participant)
            else:
                return jsonify({'error': 'Battle participant not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            participant = session.query(BattleParticipant).filter_by(participant_id=participant_id).first()
            if participant:
                return jsonify(participant.serialize())
            else:
                return jsonify({'error': 'Battle participant not found'}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route('/colonies', methods=['GET'])
def get_colonies():
    """
    Retrieves a list of all colonies, caching the results in Redis.
    Returns:
        A JSON response containing a list of serialized colony objects.
    """

    cache_key = "all_colonies"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("Retrieving colonies from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        print("Retrieving colonies from database and caching in Redis")
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            colonies = session.query(Colony).all()
            result = [colony.serialize() for colony in colonies]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except SQLAlchemyError as e:  # Use SQLAlchemyError for database errors
            logger.error(f"Error retrieving colonies: {e}")
            session.rollback()  # Rollback on database errors
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route('/colonies/<int:colony_id>', methods=['GET'])
def get_colony(colony_id):
    """
    Retrieves a specific colony by its ID, using Redis for caching.
    Args:
        colony_id: The ID of the colony to retrieve.
    Returns:
        A JSON response containing the serialized colony object, or an error message if not found.
    """
    cache_key = f"colony:{colony_id}"

    try:
        # Try to get the colony from Redis cache
        cached_colony = redis_client.get(cache_key)
        if cached_colony:
            logger.info(f"Cache hit for colony ID: {colony_id}")
            return jsonify(json.loads(cached_colony.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            colony = session.query(Colony).filter_by(colony_id=colony_id).first()
            if colony:
                serialized_colony = colony.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_colony), ex=3600)
                logger.info(f"Cache miss for colony ID: {colony_id}, stored in cache.")
                return jsonify(serialized_colony)
            else:
                return jsonify({"error": "Colony not found"}), 404
        except SQLAlchemyError as e:  # Use SQLAlchemyError for database errors
            logger.error(f"Error retrieving colony {colony_id}: {e}")
            session.rollback()  # Rollback on database errors
            return jsonify({"error": "Could not retrieve colony"}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            colony = session.query(Colony).filter_by(colony_id=colony_id).first()
            if colony:
                return jsonify(colony.serialize())
            else:
                return jsonify({"error": "Colony not found"}), 404
        except SQLAlchemyError as db_e:  # Use SQLAlchemyError for database errors
            logger.error(f"Database error: {db_e}")
            session.rollback()  # Rollback on database errors
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/colony_progress/<int:colony_id>", methods=['GET'])
def get_colony_progress(colony_id):
    """Retrieves progress data for a specific colony, caching the results in Redis."""

    cache_key = f"colony_progress:{colony_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info(f"Cache hit for colony progress ID: {colony_id}")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info(f"Cache miss for colony progress ID: {colony_id}, retrieving from database and caching.")
        session = Session(bind=engine)
        try:
            progress_data = session.query(ColonyProgress).filter_by(colony_id=colony_id).all()
            if progress_data:
                result = [p.serialize() for p in progress_data]
                json_result = json.dumps(result)
                redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                return jsonify(result)
            else:
                return jsonify({"error": "No progress data found for this colony"}), 404
        except Exception as e:
            logger.error(f"Error getting colony progress: {e}")
            return jsonify({"error": "Could not retrieve colony progress"}), 500
        finally:
            session.close()

@app.route('/colony_rats', methods=['GET'])
def get_colony_rats():
    """
    Retrieves all records from the colony_rat table, caching the results in Redis.
    Returns:
        A JSON list of all colony_rat records.
    """

    cache_key = "all_colony_rats"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving all colony rats from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving all colony rats from database and caching in Redis")
        session = Session(bind=engine)
        try:
            colony_rats = session.query(ColonyRat).all()
            result = [cr.serialize() for cr in colony_rats]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving colony_rats: {e}")
            return jsonify({"error": "Could not retrieve colony_rats"}), 500
        finally:
            session.close()

@app.route('/colony_rats/<int:colony_id>/<int:rat_id>', methods=['GET'])
def get_colony_rat(colony_id, rat_id):

    cache_key = f"colony_rat:{colony_id}:{rat_id}"

    try:
        # Try to get the colony_rat data from Redis cache
        cached_colony_rat = redis_client.get(cache_key)
        if cached_colony_rat:
            logger.info(f"Cache hit for colony_rat: colony_id={colony_id}, rat_id={rat_id}")
            return jsonify(json.loads(cached_colony_rat.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            colony_rat = session.query(ColonyRat).filter_by(colony_id=colony_id, rat_id=rat_id).first()
            if colony_rat:
                serialized_colony_rat = colony_rat.serialize()
                # Store in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_colony_rat), ex=3600)
                logger.info(f"Cache miss for colony_rat: colony_id={colony_id}, rat_id={rat_id}, stored in cache.")
                return jsonify(serialized_colony_rat)
            else:
                return jsonify({"error": "ColonyRat not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving colony_rat: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            colony_rat = session.query(ColonyRat).filter_by(colony_id=colony_id, rat_id=rat_id).first()
            if colony_rat:
                return jsonify(colony_rat.serialize())
            else:
                return jsonify({"error": "ColonyRat not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error retrieving colony_rat after Redis failure: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/day_night_times", methods=["GET"])
def get_day_night_times():
    """Retrieves all day/night time periods, caching the results in Redis."""
    cache_key = "all_day_night_times"

    try:
        # Try to get the day/nighttime from Redis cache
        cached_day_night_times = redis_client.get(cache_key)
        if cached_day_night_times:
            logger.info("Retrieving day/night times from Redis cache")
            return jsonify(json.loads(cached_day_night_times.decode('utf-8')))
        else:
            logger.info("Retrieving day/night times from database and caching in Redis")
            session = Session(bind=engine)
            try:
                day_night_times = session.query(DayNightTime).all()
                result = [dnt.serialize() for dnt in day_night_times]
                json_result = json.dumps(result)
                # Store in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json_result, ex=3600)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error retrieving day/night times: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            day_night_times = session.query(DayNightTime).all()
            return jsonify([dnt.serialize() for dnt in day_night_times])
        except Exception as db_e:
            logger.error(f"Database error retrieving day/night times after Redis failure: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/day_night_times/<int:time_id>", methods=["GET"])
def get_day_night_time(time_id):
    """Retrieves a specific day/night time period by ID, using Redis for caching."""

    cache_key = f"day_night_time:{time_id}"

    try:
        # Try to get the data from Redis cache
        cached_time = redis_client.get(cache_key)
        if cached_time:
            logger.info(f"Cache hit for day/night time ID: {time_id}")
            return jsonify(json.loads(cached_time.decode("utf-8")))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            day_night_time = session.query(DayNightTime).filter(DayNightTime.time_id == time_id).first()
            if day_night_time:
                serialized_time = day_night_time.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_time), ex=3600)  # Cache for 1 hour
                logger.info(f"Cache miss for day/night time ID: {time_id}, stored in cache.")
                return jsonify(serialized_time)
            else:
                return jsonify({"error": "Day/Night Time not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            day_night_time = session.query(DayNightTime).filter(DayNightTime.time_id == time_id).first()
            if day_night_time:
                return jsonify(day_night_time.serialize())
            else:
                return jsonify({"error": "Day/Night Time not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/economy", methods=['GET'])
def get_all_economy_transactions():
    """Retrieves all economy transactions, caching the results in Redis."""

    cache_key = "all_economy_transactions"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving economy transactions from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving economy transactions from database and caching in Redis")
        session = Session(bind=engine)
        try:
            transactions = session.query(Economy).all()
            result = [transaction.serialize() for transaction in transactions]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving all economy transactions: {e}")
            return jsonify({"error": "Could not retrieve economy transactions"}), 500
        finally:
            session.close()

@app.route("/economy/<int:transaction_id>", methods=['GET'])
def get_economy_transaction(transaction_id):
    """Retrieves a specific economy transaction by ID, using Redis for caching."""

    cache_key = f"economy_transaction:{transaction_id}"

    try:
        # Try to get the transaction from Redis cache
        cached_transaction = redis_client.get(cache_key)
        if cached_transaction:
            logger.info(f"Cache hit for economy transaction ID: {transaction_id}")
            return jsonify(json.loads(cached_transaction.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            transaction = session.query(Economy).filter_by(
                transaction_id=transaction_id
            ).first()
            if transaction:
                serialized_transaction = transaction.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_transaction), ex=3600)  # Cache for 1 hour
                logger.info(
                    f"Cache miss for economy transaction ID: {transaction_id}, stored in cache.")
                return jsonify(serialized_transaction)
            else:
                return jsonify({"error": "Economy transaction not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving economy transaction: {e}")
            return jsonify({"error": "Could not retrieve economy transaction"}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            transaction = session.query(Economy).filter_by(
                transaction_id=transaction_id
            ).first()
            if transaction:
                return jsonify(transaction.serialize())
            else:
                return jsonify({"error": "Economy transaction not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error: {db_e}")
            return jsonify({"error": "Could not retrieve economy transaction"}), 500
        finally:
            session.close()

@app.route("/effect_types", methods=["GET"])
def get_effect_types():
    """Retrieves all effect types, caching the results in Redis."""

    cache_key = "all_effect_types"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving effect types from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving effect types from database and caching in Redis")
        session = Session(bind=engine)
        try:
            effect_types = session.query(EffectType).all()
            result = [effect_type.serialize() for effect_type in effect_types]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving effect types: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/effect_types/<int:effect_type_id>", methods=["GET"])
def get_effect_type(effect_type_id):
    """Retrieves a specific effect type by ID, using Redis for caching."""

    cache_key = f"effect_type:{effect_type_id}"

    try:
        # Try to get the effect type from Redis cache
        cached_effect_type = redis_client.get(cache_key)
        if cached_effect_type:
            logger.info(f"Cache hit for effect type ID: {effect_type_id}")
            return jsonify(json.loads(cached_effect_type.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            effect_type = session.query(EffectType).filter(
                EffectType.effect_type_id == effect_type_id).first()
            if effect_type:
                serialized_effect_type = effect_type.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_effect_type), ex=3600)  # Cache for 1 hour
                logger.info(
                    f"Cache miss for effect type ID: {effect_type_id}, stored in cache.")
                return jsonify(serialized_effect_type)
            else:
                return jsonify({"error": "Effect Type not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving effect type: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            effect_type = session.query(EffectType).filter(
                EffectType.effect_type_id == effect_type_id).first()
            if effect_type:
                return jsonify(effect_type.serialize())
            else:
                return jsonify({"error": "Effect Type not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/equipment", methods=["GET"])
def get_equipments():
    """Retrieves all equipment items, caching the results in Redis."""

    cache_key = "all_equipment"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving equipment from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving equipment from database and caching in Redis")
        session = Session(bind=engine)
        try:
            equipments = session.query(Equipment).all()
            result = [equipment.serialize() for equipment in equipments]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving equipments: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/equipment/<int:equipment_id>", methods=["GET"])
def get_equipment(equipment_id):
    """Retrieves a specific equipment item by ID, using Redis for caching."""

    cache_key = f"equipment:{equipment_id}"

    try:
        # Try to get the equipment from Redis cache
        cached_equipment = redis_client.get(cache_key)
        if cached_equipment:
            logger.info(f"Cache hit for equipment ID: {equipment_id}")
            return jsonify(json.loads(cached_equipment.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            equipment = session.query(Equipment).filter_by(equipment_id=equipment_id).first()
            if equipment:
                serialized_equipment = equipment.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_equipment), ex=3600)
                logger.info(f"Cache miss for equipment ID: {equipment_id}, stored in cache.")
                return jsonify(serialized_equipment)
            else:
                return jsonify({"error": "Equipment not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving equipment: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            equipment = session.query(Equipment).filter_by(equipment_id=equipment_id).first()
            if equipment:
                return jsonify(equipment.serialize())
            else:
                return jsonify({"error": "Equipment not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/game_events", methods=["GET"])
def get_game_events():
    """Retrieves all game events, caching the results in Redis."""
    cache_key = "all_game_events"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving all game events from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving all game events from database and caching in Redis")
        session = Session(bind=engine)
        try:
            game_events = session.query(GameEvent).all()
            result = [event.serialize() for event in game_events]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving all game events: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/game_events/<int:event_id>", methods=["GET"])
def get_game_event(event_id):
    """Retrieves a specific game event by ID, using Redis for caching."""
    cache_key = f"game_event:{event_id}"

    try:
        # Try to get the game event from Redis cache
        cached_event = redis_client.get(cache_key)
        if cached_event:
            logger.info(f"Cache hit for game event ID: {event_id}")
            return jsonify(json.loads(cached_event.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            game_event = session.query(GameEvent).filter(GameEvent.event_id == event_id).first()
            if game_event:
                serialized_event = game_event.serialize()
                # Store in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_event), ex=3600)
                logger.info(f"Cache miss for game event ID: {event_id}, stored in cache.")
                return jsonify(serialized_event)
            else:
                return jsonify({"error": "Game event not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving game event {event_id}: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            game_event = session.query(GameEvent).filter(GameEvent.event_id == event_id).first()
            if game_event:
                return jsonify(game_event.serialize())
            else:
                return jsonify({"error": "Game event not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error retrieving game event {event_id}: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/items", methods=["GET"])
def get_items():
    """Retrieves all items, caching the results in Redis."""

    cache_key = "all_items"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving items from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving items from database and caching in Redis")
        session = Session(bind=engine)
        try:
            items = session.query(Item).all()
            result = [item.serialize() for item in items]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving items: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Retrieves a specific item by ID, using Redis for caching."""
    cache_key = f"item:{item_id}"

    try:
        # Try to get the item from Redis cache
        cached_item = redis_client.get(cache_key)
        if cached_item:
            logger.info(f"Cache hit for item ID: {item_id}")
            return jsonify(json.loads(cached_item.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if item:
                serialized_item = item.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_item), ex=3600)
                logger.info(f"Cache miss for item ID: {item_id}, stored in cache.")
                return jsonify(serialized_item)
            else:
                return jsonify({"error": "Item not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            item = session.query(Item).filter_by(item_id=item_id).first()
            if item:
                return jsonify(item.serialize())
            else:
                return jsonify({"error": "Item not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/plagues", methods=['GET'])
def get_plagues():
    """Retrieves all plagues, caching the results in Redis."""
    cache_key = "all_plagues"
    try:
        # Try to get the plagues from Redis cache
        cached_plagues = redis_client.get(cache_key)
        if cached_plagues:
            logger.info("Retrieving plagues from Redis cache")
            return jsonify(json.loads(cached_plagues.decode('utf-8')))
        else:
            logger.info("Retrieving plagues from database and caching in Redis")
            session = Session(bind=engine)
            try:
                plagues = session.query(Plague).all()
                result = [plague.serialize() for plague in plagues]
                json_result = json.dumps(result)
                redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            plagues = session.query(Plague).all()
            return jsonify([plague.serialize() for plague in plagues])
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/plagues/<int:plague_id>", methods=['GET'])
def get_plague(plague_id):
    """Retrieves a specific plague by ID, using Redis for caching."""
    cache_key = f"plague:{plague_id}"
    try:
        # Try to get the plague data from Redis cache
        cached_plague = redis_client.get(cache_key)
        if cached_plague:
            logger.info(f"Cache hit for plague ID: {plague_id}")
            return jsonify(json.loads(cached_plague.decode('utf-8')))
        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            plague = session.query(Plague).filter_by(plague_id=plague_id).first()
            if plague:
                serialized_plague = plague.serialize()
                # Store the data in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_plague), ex=3600)
                logger.info(f"Cache miss for plague ID: {plague_id}, stored in cache.")
                return jsonify(serialized_plague)
            else:
                return jsonify({"error": "Plague not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            plague = session.query(Plague).filter_by(plague_id=plague_id).first()
            if plague:
                return jsonify(plague.serialize())
            else:
                return jsonify({"error": "Plague not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/plague_affected", methods=['GET'])
def get_all_plague_affected():
    """Retrieves all plague affected records, caching the results in Redis."""

    cache_key = "all_plague_affected"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving all plague affected from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving all plague affected from database and caching in Redis")
        session = Session(bind=engine)
        try:
            plague_affected_list = session.query(PlagueAffected).all()
            result = [item.serialize() for item in plague_affected_list]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving all plague affected: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/plague_affected/<int:relation_id>", methods=['GET'])
def get_plague_affected_by_id(relation_id):
    """Retrieves a specific plague affected record by its ID, using Redis for caching."""

    cache_key = f"plague_affected:{relation_id}"

    try:
        # Try to get the record from Redis cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for plague_affected ID: {relation_id}")
            return jsonify(json.loads(cached_data.decode('utf-8')))
        else:
            logger.info(f"Cache miss for plague_affected ID: {relation_id}, retrieving from DB and caching")
            session = Session(bind=engine)
            try:
                plague_affected = session.query(PlagueAffected).filter_by(
                    relation_id=relation_id
                ).first()
                if plague_affected:
                    serialized_data = plague_affected.serialize()
                    json_result = json.dumps(serialized_data)
                    redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                    return jsonify(serialized_data)
                else:
                    return jsonify({"error": "Plague Affected record not found"}), 404
            except Exception as e:
                logger.error(f"Error retrieving plague_affected by ID: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            plague_affected = session.query(PlagueAffected).filter_by(
                relation_id=relation_id
            ).first()
            if plague_affected:
                return jsonify(plague_affected.serialize())
            else:
                return jsonify({"error": "Plague Affected record not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error after Redis failure: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/plague_rats", methods=['GET'])
def get_plague_rats():
    """Retrieves all plague rats, caching the results in Redis."""

    cache_key = "all_plague_rats"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving plague rats from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving plague rats from database and caching in Redis")
        session = Session(bind=engine)
        try:
            plague_rats = session.query(PlagueRat).all()
            result = [rat.serialize() for rat in plague_rats]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except SQLAlchemyError as e:  # Use SQLAlchemyError
            logger.error(f"Error retrieving plague rats: {e}")
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/plague_rats/<int:rat_id>", methods=['GET'])
def get_plague_rat(rat_id):
    """Retrieves a specific plague rat by ID, using Redis for caching."""

    cache_key = f"plague_rat:{rat_id}"

    try:
        # Try to get the plague rat from Redis cache
        cached_rat = redis_client.get(cache_key)
        if cached_rat:
            logger.info(f"Cache hit for plague rat ID: {rat_id}")
            return jsonify(json.loads(cached_rat.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            plague_rat = session.query(PlagueRat).filter_by(plague_rat_id=rat_id).first() # Use the correct model attribute
            if plague_rat:
                serialized_rat = plague_rat.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_rat), ex=3600)
                logger.info(f"Cache miss for plague rat ID: {rat_id}, stored in cache.")
                return jsonify(serialized_rat)
            else:
                return jsonify({"error": "Plague Rat not found"}), 404
        except SQLAlchemyError as e:  # Use SQLAlchemyError
            logger.error(f"Error retrieving plague rat {rat_id}: {e}")
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            plague_rat = session.query(PlagueRat).filter_by(plague_rat_id=rat_id).first() # Use the correct model attribute
            if plague_rat:
                return jsonify(plague_rat.serialize())
            else:
                return jsonify({"error": "Plague Rat not found"}), 404
        except SQLAlchemyError as db_e:  # Use SQLAlchemyError
            logger.error(f"Database error after Redis failure: {db_e}")
            session.rollback()
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/players", methods=["GET"])
def get_players():
    """Retrieves all players, caching the results in Redis."""
    cache_key = "all_players"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving all players from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving all players from database and caching in Redis")
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            players = session.query(Player).all()
            result = [player.serialize() for player in players]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except SQLAlchemyError as e:
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    """Retrieves a specific player by ID, using Redis for caching."""
    cache_key = f"player:{player_id}"

    try:
        # Try to get the player data from Redis cache
        cached_player = redis_client.get(cache_key)
        if cached_player:
            logger.info(f"Cache hit for player ID: {player_id}")
            return jsonify(json.loads(cached_player.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            player = session.query(Player).filter(Player.player_id == player_id).first()
            if player:
                serialized_player = player.serialize()
                # Store the data in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_player), ex=3600)
                logger.info(f"Cache miss for player ID: {player_id}, stored in cache.")
                return jsonify(serialized_player)
            else:
                return jsonify({"error": "Player not found"}), 404
        except SQLAlchemyError as e:
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)  # Bind the engine to the session
        try:
            player = session.query(Player).filter(Player.player_id == player_id).first()
            if player:
                return jsonify(player.serialize())
            else:
                return jsonify({"error": "Player not found"}), 404
        except SQLAlchemyError as db_e:
            session.rollback()
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/player_achievements", methods=['GET'])
def get_player_achievements():
    """Retrieves all player achievement records."""
    cache_key = "all_player_achievements"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("Retrieving data from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        print("Retrieving data from database and caching in Redis")
        session = Session(bind=engine)
        try:
            player_achievements = session.query(PlayerAchievement).all()
            result = [pa.serialize() for pa in player_achievements]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/player_achievements/<int:player_achievement_id>", methods=['GET'])
def get_player_achievement(player_achievement_id):
    """Retrieves a specific player achievement record by ID."""
    cache_key = f"player_achievement:{player_achievement_id}"
    try:
        cached_achievement = redis_client.get(cache_key)
        if cached_achievement:
            print("Retrieving data from Redis cache")
            return jsonify(json.loads(cached_achievement.decode('utf-8')))
        else:
            print("Retrieving data from database and caching in Redis")
            session = Session(bind=engine)
            try:
                player_achievement = session.query(PlayerAchievement).filter_by(player_achievement_id=player_achievement_id).first()
                if player_achievement:
                    serialized_achievement = player_achievement.serialize()
                    json_result = json.dumps(serialized_achievement)
                    redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                    return jsonify(serialized_achievement)
                else:
                    return jsonify({"error": "Player achievement record not found"}), 404
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        session = Session(bind=engine)
        try:
            player_achievement = session.query(PlayerAchievement).filter_by(player_achievement_id=player_achievement_id).first()
            if player_achievement:
                return jsonify(player_achievement.serialize())
            else:
                return jsonify({"error": "Player achievement record not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/players/<int:player_id>/achievements", methods=['GET'])
def get_player_achievements_by_player(player_id):
    """Retrieves all achievements for a specific player, caching the results in Redis."""

    cache_key = f"player:{player_id}:achievements"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info(f"Cache hit for player {player_id} achievements")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info(f"Cache miss for player {player_id} achievements, retrieving from DB and caching")
        session = Session(bind=engine)
        try:
            player_achievements = session.query(PlayerAchievement).filter_by(player_id=player_id).all()
            result = [pa.serialize() for pa in player_achievements]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/achievements/<int:achievement_id>/players", methods=['GET'])
def get_players_by_achievement(achievement_id):
    """Retrieves all players who have earned a specific achievement, caching the results in Redis."""

    cache_key = f"achievement:{achievement_id}:players"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info(f"Cache hit for achievement {achievement_id} players")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info(f"Cache miss for achievement {achievement_id} players, retrieving from DB and caching")
        session = Session(bind=engine)
        try:
            player_achievements = session.query(PlayerAchievement).filter_by(achievement_id=achievement_id).all()
            result = [pa.serialize() for pa in player_achievements]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/player_equipment", methods=['GET'])
def get_all_player_equipment():
    """Retrieves all player equipment records, caching the results in Redis."""
    cache_key = "all_player_equipment"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving all player equipment from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving all player equipment from database and caching in Redis")
        session = Session(bind=engine)
        try:
            player_equipments = session.query(PlayerEquipment).all()
            result = [pe.serialize() for pe in player_equipments]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/player_equipment/<int:player_equipment_id>", methods=['GET'])
def get_player_equipment_by_id(player_equipment_id):
    """Retrieves a specific player equipment record by ID, using Redis for caching."""
    cache_key = f"player_equipment:{player_equipment_id}"

    try:
        # Try to get the player equipment from Redis cache
        cached_equipment = redis_client.get(cache_key)
        if cached_equipment:
            logger.info(f"Cache hit for player equipment ID: {player_equipment_id}")
            return jsonify(json.loads(cached_equipment.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            player_equipment = session.query(PlayerEquipment).filter_by(player_equipment_id=player_equipment_id).first()
            if player_equipment:
                serialized_equipment = player_equipment.serialize()
                # Store in Redis cache with expiry (e.g., 1 hour = 3600 seconds)
                redis_client.set(cache_key, json.dumps(serialized_equipment), ex=3600)
                logger.info(f"Cache miss for player equipment ID: {player_equipment_id}, stored in cache.")
                return jsonify(serialized_equipment)
            else:
                return jsonify({"error": "Player equipment record not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            player_equipment = session.query(PlayerEquipment).filter_by(player_equipment_id=player_equipment_id).first()
            if player_equipment:
                return jsonify(player_equipment.serialize())
            else:
                return jsonify({"error": "Player equipment record not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/severities", methods=["GET"])
def get_severities():
    """Retrieves all severity levels, caching the results in Redis."""
    cache_key = "all_severities"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving severities from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving severities from database and caching in Redis")
        session = Session(bind=engine)
        try:
            severities = session.query(Severity).all()
            result = [severity.serialize() for severity in severities]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error retrieving severities: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/severities/<int:severity_id>", methods=["GET"])
def get_severity(severity_id):
    """Retrieves a specific severity level by ID, using Redis for caching."""
    cache_key = f"severity:{severity_id}"

    try:
        # Try to get the severity from Redis cache
        cached_severity = redis_client.get(cache_key)
        if cached_severity:
            logger.info(f"Cache hit for severity ID: {severity_id}")
            return jsonify(json.loads(cached_severity.decode('utf-8')))

        # If not in cache, fetch from the database
        session = Session(bind=engine)
        try:
            severity = session.query(Severity).filter_by(severity_id=severity_id).first()
            if severity:
                serialized_severity = severity.serialize()
                # Store in Redis cache with expiry
                redis_client.set(cache_key, json.dumps(serialized_severity), ex=3600)  # Cache for 1 hour
                logger.info(f"Cache miss for severity ID: {severity_id}, stored in cache.")
                return jsonify(serialized_severity)
            else:
                return jsonify({"error": "Severity not found"}), 404
        except Exception as e:
            logger.error(f"Error retrieving severity {severity_id}: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            severity = session.query(Severity).filter_by(severity_id=severity_id).first()
            if severity:
                return jsonify(severity.serialize())
            else:
                return jsonify({"error": "Severity not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/stats", methods=['GET'])
def get_all_stats():
    """Retrieves all player stats, caching the results in Redis."""
    cache_key = "all_stats"
    try:
        # Try to get data from Redis cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info("Retrieving all stats from Redis cache")
            return jsonify(json.loads(cached_data.decode('utf-8')))
        else:
            logger.info("Retrieving all stats from database and caching in Redis")
            session = Session(bind=engine)
            try:
                stats = session.query(Stats).all()
                result = [stat.serialize() for stat in stats]
                json_result = json.dumps(result)
                redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error retrieving all stats: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            stats = session.query(Stats).all()
            return jsonify([stat.serialize() for stat in stats])
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/stats/<int:player_id>", methods=['GET'])
def get_stats(player_id):
    """Retrieves stats for a specific player, using Redis for caching."""
    cache_key = f"stats:{player_id}"
    try:
        # Try to get stats from Redis cache
        cached_stats = redis_client.get(cache_key)
        if cached_stats:
            logger.info(f"Cache hit for player stats ID: {player_id}")
            return jsonify(json.loads(cached_stats.decode('utf-8')))
        else:
            logger.info(f"Cache miss for player stats ID: {player_id}, retrieving from database and caching.")
            session = Session(bind=engine)
            try:
                stat = session.query(Stats).filter_by(player_id=player_id).first()
                if stat:
                    serialized_stat = stat.serialize()
                    redis_client.set(cache_key, json.dumps(serialized_stat), ex=3600)  # Cache for 1 hour
                    return jsonify(serialized_stat)
                else:
                    return jsonify({"error": "Stats not found"}), 404
            except Exception as e:
                logger.error(f"Error retrieving stats for player {player_id}: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            stat = session.query(Stats).filter_by(player_id=player_id).first()
            if stat:
                return jsonify(stat.serialize())
            else:
                return jsonify({"error": "Stats not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/weather", methods=['GET'])
def get_all_weather():
    """Retrieves all weather entries with their effects, caching the results in Redis."""

    cache_key = "all_weather"
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            logger.info("Retrieving all weather data from Redis cache")
            return jsonify(json.loads(cached_data.decode('utf-8')))
        else:
            logger.info("Retrieving all weather data from database and caching in Redis")
            session = Session(bind=engine)
            try:
                weather_list = session.query(Weather).all()
                result = [weather.serialize() for weather in weather_list]
                json_result = json.dumps(result)
                redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error retrieving all weather: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            weather_list = session.query(Weather).all()
            return jsonify([weather.serialize() for weather in weather_list])
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/weather/<int:weather_id>", methods=['GET'])
def get_weather_by_id(weather_id):
    """Retrieves a specific weather entry by ID, using Redis for caching."""

    cache_key = f"weather:{weather_id}"
    try:
        cached_data = redis_client.get(cache_key)

        if cached_data:
            logger.info(f"Cache hit for weather ID: {weather_id}")
            return jsonify(json.loads(cached_data.decode('utf-8')))
        else:
            logger.info(f"Cache miss for weather ID: {weather_id}, retrieving from database and caching")
            session = Session(bind=engine)
            try:
                weather = session.query(Weather).filter_by(weather_id=weather_id).first()
                if weather:
                    serialized_weather = weather.serialize()
                    json_result = json.dumps(serialized_weather)
                    redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                    return jsonify(serialized_weather)
                else:
                    return jsonify({"error": "Weather not found"}), 404
            except Exception as e:
                logger.error(f"Error retrieving weather {weather_id}: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            weather = session.query(Weather).filter_by(weather_id=weather_id).first()
            if weather:
                return jsonify(weather.serialize())
            else:
                return jsonify({"error": "Weather not found"}), 404
        except Exception as db_e:
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

@app.route("/weather_effects", methods=["GET"])
def get_weather_effects():
    """Retrieves all weather effects, caching the results in Redis."""

    cache_key = "all_weather_effects"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        logger.info("Retrieving weather effects from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))
    else:
        logger.info("Retrieving weather effects from database and caching in Redis")
        session = Session(bind=engine)  # Bind the engine here
        try:
            weather_effects = session.query(WeatherEffects).all()
            result = [we.serialize() for we in weather_effects]
            json_result = json.dumps(result)
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
            return jsonify(result)
        except SQLAlchemyError as e:  # Use SQLAlchemyError
            logger.error(f"Error retrieving weather effects: {e}")
            session.rollback()  # Add rollback
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/weather_effects/<int:effect_id>", methods=["GET"])
def get_weather_effect(effect_id):
    """Retrieves a specific weather effect by ID, using Redis for caching."""

    cache_key = f"weather_effect:{effect_id}"

    try:
        # Try to get the weather effect from Redis cache
        cached_effect = redis_client.get(cache_key)
        if cached_effect:
            logger.info(f"Cache hit for weather effect ID: {effect_id}")
            return jsonify(json.loads(cached_effect.decode('utf-8')))
        else:
            logger.info(f"Cache miss for weather effect ID: {effect_id}, retrieving from database and caching")
            session = Session(bind=engine)
            try:
                weather_effect = session.query(WeatherEffects).filter_by(effect_id=effect_id).first()
                if weather_effect:
                    serialized_effect = weather_effect.serialize()
                    json_result = json.dumps(serialized_effect)
                    redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour
                    return jsonify(serialized_effect)
                else:
                    return jsonify({"error": "Weather effect not found"}), 404
            except Exception as e:
                logger.error(f"Error retrieving weather effect: {e}")
                return jsonify({"error": str(e)}), 500
            finally:
                session.close()

    except redis.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Redis: {e}")
        # If Redis connection fails, still try to fetch from the database
        session = Session(bind=engine)
        try:
            weather_effect = session.query(WeatherEffects).filter_by(effect_id=effect_id).first()
            if weather_effect:
                return jsonify(weather_effect.serialize())
            else:
                return jsonify({"error": "Weather effect not found"}), 404
        except Exception as db_e:
            logger.error(f"Database error after Redis failure: {db_e}")
            return jsonify({"error": str(db_e)}), 500
        finally:
            session.close()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='0.0.0.0', port=5000, debug=False)