import json
import logging

from flask import jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db_utils import redis_client
from models import Achievement, Battle, BattleParticipant, Colony, ColonyProgress, ColonyRat, DayNightTime, Economy, \
    EffectType, Equipment, GameEvent, Item, Plague, PlagueAffected, PlagueRat, Player, PlayerAchievement, \
    PlayerEquipment, Severity, Stats, Weather, WeatherEffects, Base, engine

logger = logging.getLogger(__name__)

app = Blueprint('get_routes', __name__) # app is a Blueprint

#Get App Routes
@app.route("/achievements", methods=["GET"])
def get_achievements():
    """Retrieves all achievements, caching the results in Redis."""

    cache_key = "all_achievements"  # Define a cache key
    cached_data = redis_client.get(cache_key)  # Try to get data from Redis

    if cached_data:
        print("Retrieving data from Redis cache")
        return jsonify(json.loads(cached_data.decode('utf-8')))  # Decode and load JSON
    else:
        print("Retrieving data from database and caching in Redis")
        session = Session()
        try:
            achievements = session.query(Achievement).all()
            result = [achievement.serialize() for achievement in achievements]
            json_result = json.dumps(result)  # Convert to JSON
            redis_client.set(cache_key, json_result, ex=3600)  # Cache for 1 hour (3600 seconds)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()

@app.route("/achievements/<int:achievement_id>", methods=["GET"])
def get_achievement(achievement_id):
    """Retrieves a specific achievement by ID."""

    session = Session()
    try:
        achievement = session.query(Achievement).filter_by(
            achievement_id=achievement_id
        ).first()
        if achievement:
            return jsonify(achievement.serialize())
        else:
            return jsonify({"error": "Achievement not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/battles/<int:battle_id>", methods=['GET'])
def get_battle(battle_id):
    """Retrieves a battle by ID."""
    session = Session()
    try:
        battle = session.query(Battle).filter_by(battle_id=battle_id).first()
        if battle:
            return jsonify(battle.serialize())
        else:
            return jsonify({"error": "Battle not found"}), 404
    finally:
        session.close()

@app.route('/battle_participants/<int:participant_id>', methods=['GET'])
def get_battle_participant(participant_id):
    """Retrieves a battle participant by their ID."""
    session = Session()
    try:
        participant = session.query(BattleParticipant).filter_by(participant_id=participant_id).first()
        if participant:
            return jsonify(participant.serialize())
        else:
            return jsonify({'error': 'Battle participant not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/colonies', methods=['GET'])
def get_colonies():
    """
    Retrieves a list of all colonies.
    Returns:
        A JSON response containing a list of serialized colony objects.
    """
    session = Session()
    try:
        colonies = session.query(Colony).all()
        result = [colony.serialize() for colony in colonies]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving colonies: {e}")
        return jsonify({"error": "Could not retrieve colonies"}), 500
    finally:
        session.close()

@app.route('/colonies/<int:colony_id>', methods=['GET'])
def get_colony(colony_id):
    """
    Retrieves a specific colony by its ID.
    Args:
        colony_id: The ID of the colony to retrieve.
    Returns:
        A JSON response containing the serialized colony object, or an error message if not found.
    """
    session = Session()
    try:
        colony = session.query(Colony).filter_by(colony_id=colony_id).first()
        if colony:
            return jsonify(colony.serialize())
        else:
            return jsonify({"error": "Colony not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving colony {colony_id}: {e}")
        return jsonify({"error": "Could not retrieve colony"}), 500
    finally:
        session.close()

@app.route("/colony_progress/<int:colony_id>", methods=['GET'])
def get_colony_progress(colony_id):
    """Retrieves progress data for a specific colony."""
    session = Session()
    try:
        progress_data = session.query(ColonyProgress).filter_by(colony_id=colony_id).all()
        if progress_data:
            return jsonify([p.serialize() for p in progress_data])
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
    Retrieves all records from the colony_rat table.
    Returns:
        A JSON list of all colony_rat records.
    """
    session = Session()
    try:
        colony_rats = session.query(ColonyRat).all()
        result = [cr.serialize() for cr in colony_rats]
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving colony_rats: {e}")
        return jsonify({"error": "Could not retrieve colony_rats"}), 500
    finally:
        session.close()


@app.route('/colony_rats/<int:colony_id>/<int:rat_id>', methods=['GET'])
def get_colony_rat(colony_id, rat_id):
    """
    Retrieves a specific colony_rat record by colony_id and rat_id.

    Args:
        colony_id (int): The ID of the colony.
        rat_id (int): The ID of the rat.

    Returns:
        A JSON representation of the colony_rat record, or a 404 error if not found.
    """
    session = Session()
    try:
        colony_rat = session.query(ColonyRat).filter_by(colony_id=colony_id, rat_id=rat_id).first()
        if colony_rat:
            return jsonify(colony_rat.serialize())
        else:
            return jsonify({"error": "ColonyRat not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving colony_rat: {e}")
        return jsonify({"error": "Could not retrieve ColonyRat"}), 500
    finally:
        session.close()

@app.route("/day_night_times", methods=["GET"])
def get_day_night_times():
    """Retrieves all day/night time periods."""
    session = Session()
    try:
        day_night_times = session.query(DayNightTime).all()
        return jsonify([dnt.serialize() for dnt in day_night_times])
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/day_night_times/<int:time_id>", methods=["GET"])
def get_day_night_time(time_id):
    """Retrieves a specific day/night time period by ID."""
    session = Session()
    try:
        day_night_time = session.query(DayNightTime).filter(DayNightTime.time_id == time_id).first()
        if day_night_time:
            return jsonify(day_night_time.serialize())
        else:
            return jsonify({"error": "Day/Night Time not found"}), 404
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/economy", methods=['GET'])
def get_all_economy_transactions():
    """Retrieves all economy transactions."""
    session = Session()
    try:
        transactions = session.query(Economy).all()
        return jsonify([transaction.serialize() for transaction in transactions])
    except Exception as e:
        logger.error(f"Error retrieving all economy transactions: {e}")
        return jsonify({"error": "Could not retrieve economy transactions"}), 500
    finally:
        session.close()

@app.route("/economy/<int:transaction_id>", methods=['GET'])
def get_economy_transaction(transaction_id):
    """Retrieves a specific economy transaction by ID."""
    session = Session()
    try:
        transaction = session.query(Economy).filter_by(transaction_id=transaction_id).first()
        if transaction:
            return jsonify(transaction.serialize())
        else:
            return jsonify({"error": "Economy transaction not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving economy transaction: {e}")
        return jsonify({"error": "Could not retrieve economy transaction"}), 500
    finally:
        session.close()

@app.route("/effect_types", methods=["GET"])
def get_effect_types():
    """Retrieves all effect types."""
    session = Session()
    try:
        effect_types = session.query(EffectType).all()
        return jsonify([effect_type.serialize() for effect_type in effect_types])
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/effect_types/<int:effect_type_id>", methods=["GET"])
def get_effect_type(effect_type_id):
    """Retrieves a specific effect type by ID."""
    session = Session()
    try:
        effect_type = session.query(EffectType).filter(EffectType.effect_type_id == effect_type_id).first()
        if effect_type:
            return jsonify(effect_type.serialize())
        else:
            return jsonify({"error": "Effect Type not found"}), 404
    except Exception as e:
         return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/equipment", methods=["GET"])
def get_equipments():
    """Retrieves all equipment items."""
    session = Session()
    try:
        equipments = session.query(Equipment).all()
        return jsonify([equipment.serialize() for equipment in equipments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/equipment/<int:equipment_id>", methods=["GET"])
def get_equipment(equipment_id):
    """Retrieves a specific equipment item by ID."""
    session = Session()
    try:
        equipment = session.query(Equipment).filter(Equipment.equipment_id == equipment_id).first()
        if equipment:
            return jsonify(equipment.serialize())
        else:
            return jsonify({"error": "Equipment not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/game_events", methods=["GET"])
def get_game_events():
    """Retrieves all game events."""
    session = Session()
    try:
        game_events = session.query(GameEvent).all()
        return jsonify([event.serialize() for event in game_events])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/game_events/<int:event_id>", methods=["GET"])
def get_game_event(event_id):
    """Retrieves a specific game event by ID."""
    session = Session()
    try:
        game_event = session.query(GameEvent).filter(GameEvent.event_id == event_id).first()
        if game_event:
            return jsonify(game_event.serialize())
        else:
            return jsonify({"error": "Game event not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/items", methods=["GET"])
def get_items():
    """Retrieves all items."""
    session = Session()
    try:
        items = session.query(Item).all()
        return jsonify([item.serialize() for item in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Retrieves a specific item by ID."""
    session = Session()
    try:
        item = session.query(Item).filter_by(item_id=item_id).first()
        if item:
            return jsonify(item.serialize())
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/plagues", methods=['GET'])
def get_plagues():
    """Retrieves all plagues."""
    session = Session()
    try:
        plagues = session.query(Plague).all()
        return jsonify([plague.serialize() for plague in plagues])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/plagues/<int:plague_id>", methods=['GET'])
def get_plague(plague_id):
    """Retrieves a specific plague by ID."""
    session = Session()
    try:
        plague = session.query(Plague).filter_by(plague_id=plague_id).first()
        if plague:
            return jsonify(plague.serialize())
        else:
            return jsonify({"error": "Plague not found"}), 404
    finally:
        session.close()

@app.route("/plague_affected", methods=['GET'])
def get_all_plague_affected():
    """Retrieves all plague affected records."""

    session = Session()
    try:
        plague_affected_list = session.query(PlagueAffected).all()
        return jsonify([item.serialize() for item in plague_affected_list])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/plague_affected/<int:relation_id>", methods=['GET'])
def get_plague_affected_by_id(relation_id):
    """Retrieves a specific plague affected record by its ID."""

    session = Session()
    try:
        plague_affected = session.query(PlagueAffected).filter_by(relation_id=relation_id).first()
        if plague_affected:
            return jsonify(plague_affected.serialize())
        else:
            return jsonify({"error": "Plague Affected record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/plague_rats", methods=['GET'])
def get_plague_rats():
    """Retrieves all plague rats."""

    session = Session()
    try:
        plague_rats = session.query(PlagueRat).all()
        return jsonify([rat.serialize() for rat in plague_rats])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/plague_rats/<int:rat_id>", methods=['GET'])
def get_plague_rat(rat_id):
    """Retrieves a specific plague rat by ID."""

    session = Session()
    try:
        plague_rat = session.query(PlagueRat).filter_by(rat_id=rat_id).first()
        if plague_rat:
            return jsonify(plague_rat.serialize())
        else:
            return jsonify({"error": "Plague Rat not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/players", methods=["GET"])
def get_players():
    """Retrieves all players."""
    session = Session()
    try:
        players = session.query(Player).all()
        return jsonify([player.serialize() for player in players])
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    """Retrieves a specific player by ID."""
    session = Session()
    try:
        player = session.query(Player).filter(Player.player_id == player_id).first()
        if player:
            return jsonify(player.serialize())
        else:
            return jsonify({"error": "Player not found"}), 404
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/player_achievements", methods=['GET'])
def get_player_achievements():
    """Retrieves all player achievement records."""
    session = Session()
    try:
        player_achievements = session.query(PlayerAchievement).all()
        return jsonify([pa.serialize() for pa in player_achievements])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/player_achievements/<int:player_achievement_id>", methods=['GET'])
def get_player_achievement(player_achievement_id):
    """Retrieves a specific player achievement record by ID."""
    session = Session()
    try:
        player_achievement = session.query(PlayerAchievement).filter_by(player_achievement_id=player_achievement_id).first()
        if player_achievement:
            return jsonify(player_achievement.serialize())
        else:
            return jsonify({"error": "Player achievement record not found"}), 404
    finally:
        session.close()

@app.route("/players/<int:player_id>/achievements", methods=['GET'])
def get_player_achievements_by_player(player_id):
    """Retrieves all achievements for a specific player."""
    session = Session()
    try:
        player_achievements = session.query(PlayerAchievement).filter_by(player_id=player_id).all()
        return jsonify([pa.serialize() for pa in player_achievements])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/achievements/<int:achievement_id>/players", methods=['GET'])
def get_players_by_achievement(achievement_id):
    """Retrieves all players who have earned a specific achievement."""
    session = Session()
    try:
        player_achievements = session.query(PlayerAchievement).filter_by(achievement_id=achievement_id).all()
        return jsonify([pa.serialize() for pa in player_achievements])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/player_equipment", methods=['GET'])
def get_all_player_equipment():
    """Retrieves all player equipment records."""
    session = Session()
    try:
        player_equipments = session.query(PlayerEquipment).all()
        return jsonify([pe.serialize() for pe in player_equipments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/player_equipment/<int:player_equipment_id>", methods=['GET'])
def get_player_equipment_by_id(player_equipment_id):
    """Retrieves a specific player equipment record by ID."""

    session = Session()
    try:
        player_equipment = session.query(PlayerEquipment).filter_by(player_equipment_id=player_equipment_id).first()
        if player_equipment:
            return jsonify(player_equipment.serialize())
        else:
            return jsonify({"error": "Player equipment record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/severities", methods=["GET"])
def get_severities():
    """Retrieves all severity levels."""

    session = Session()
    try:
        severities = session.query(Severity).all()
        return jsonify([severity.serialize() for severity in severities])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/severities/<int:severity_id>", methods=["GET"])
def get_severity(severity_id):
    """Retrieves a specific severity level by ID."""

    session = Session()
    try:
        severity = session.query(Severity).filter_by(severity_id=severity_id).first()
        if severity:
            return jsonify(severity.serialize())
        else:
            return jsonify({"error": "Severity not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/stats", methods=['GET'])
def get_all_stats():
    """Retrieves all player stats."""

    session = Session()
    try:
        stats = session.query(Stats).all()
        return jsonify([stat.serialize() for stat in stats])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/stats/<int:player_id>", methods=['GET'])
def get_stats(player_id):
    """Retrieves stats for a specific player."""

    session = Session()
    try:
        stat = session.query(Stats).filter_by(player_id=player_id).first()
        if stat:
            return jsonify(stat.serialize())
        else:
            return jsonify({"error": "Stats not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/weather", methods=['GET'])
def get_all_weather():
    """Retrieves all weather entries with their effects."""

    session = Session()
    try:
        weather_list = session.query(Weather).all()
        return jsonify([weather.serialize() for weather in weather_list])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/weather/<int:weather_id>", methods=['GET'])
def get_weather_by_id(weather_id):
    """Retrieves a specific weather entry by ID."""

    session = Session()
    try:
        weather = session.query(Weather).filter_by(weather_id=weather_id).first()
        if weather:
            return jsonify(weather.serialize())
        else:
            return jsonify({"error": "Weather not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/weather_effects", methods=["GET"])
def get_weather_effects():
    """Retrieves all weather effects."""

    session = Session()
    try:
        weather_effects = session.query(WeatherEffects).all()
        return jsonify([we.serialize() for we in weather_effects])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/weather_effects/<int:effect_id>", methods=["GET"])
def get_weather_effect(effect_id):
    """Retrieves a specific weather effect by ID."""

    session = Session()
    try:
        weather_effect = session.query(WeatherEffects).filter_by(effect_id=effect_id).first()
        if weather_effect:
            return jsonify(weather_effect.serialize())
        else:
            return jsonify({"error": "Weather effect not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='0.0.0.0', port=5000, debug=False)