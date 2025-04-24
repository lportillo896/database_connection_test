from datetime import time
from sqlite3 import OperationalError

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, DECIMAL, \
    UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db_utils import Base, create_engine, MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE

#SQLAlchemy Configuration
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

engine = None
for i in range(MAX_RETRIES):
    try:
        engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{3306}/{MYSQL_DATABASE}')
        engine.connect()
        print("Successfully connected to MySQL!")
        break
    except OperationalError as e:
        print(f"Failed to connect to MySQL (attempt {i + 1}/{MAX_RETRIES}): {e}")
        time(RETRY_DELAY)

if engine is None:
    raise Exception("Failed to connect to MySQL after multiple retries.")

# SQLAlchemy Models
class Achievement(Base):
    __tablename__ = 'achievements'
    achievement_id = Column(Integer, primary_key=True)
    achievement_name = Column(String(255), unique=True, nullable=False)
    achievement_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def serialize(self):
        return {
            'achievement_id': self.achievement_id,
            'achievement_name': self.achievement_name,
            'achievement_description': self.achievement_description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Battle(Base):
    __tablename__ = 'battle'

    battle_id = Column(Integer, primary_key=True)
    battle_type = Column(String(100))
    winner_colony_id = Column(Integer, ForeignKey('colony.colony_id'), nullable=True)
    battle_date = Column(DateTime, nullable=False, server_default=func.now())

    winner_colony = relationship("Colony")

    def serialize(self):
        return {
            'battle_id': self.battle_id,
            'battle_type': self.battle_type,
            'winner_colony_id': self.winner_colony_id,
            'battle_date': self.battle_date.isoformat() if self.battle_date else None
        }

class BattleParticipant(Base):
    __tablename__ = 'battle_participant'

    participant_id = Column(Integer, primary_key=True)
    battle_id = Column(Integer, ForeignKey('battle.battle_id'), nullable=False)
    colony_id = Column(Integer, ForeignKey('colony.colony_id'), nullable=False)
    num_units = Column(Integer, default=1)

    battle = relationship("Battle")
    colony = relationship("Colony")

    def serialize(self):
        return {
            'participant_id': self.participant_id,
            'battle_id': self.battle_id,
            'colony_id': self.colony_id,
            'num_units': self.num_units,
        }

class Colony(Base):
    __tablename__ = 'colony'
    colony_id = Column(Integer, primary_key=True)
    leader_id = Column(Integer, ForeignKey('player.player_id'), nullable=True)
    colony_name = Column(String(255), nullable=False)
    colony_size = Column(Integer, default=1)
    x_coordinate = Column(DECIMAL(10, 6), nullable=True)
    y_coordinate = Column(DECIMAL(10, 6), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(50), default='developing')

    leader = relationship("Player")

    def serialize(self):
        return {
            'colony_id': self.colony_id,
            'leader_id': self.leader_id,
            'colony_name': self.colony_name,
            'colony_size': self.colony_size,
            'x_coordinate': str(self.x_coordinate),
            'y_coordinate': str(self.y_coordinate),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status
        }

class ColonyProgress(Base):
    __tablename__ = 'colony_progress'

    progress_id = Column(Integer, primary_key=True)
    colony_id = Column(Integer, ForeignKey('colony.colony_id'), nullable=False)
    upgrade_type = Column(String(100), nullable=False)
    upgrade_level = Column(Integer, default=1)
    timestamp = Column(DateTime, server_default=func.now())

    colony = relationship("Colony")

    def serialize(self):
        return {
            'progress_id': self.progress_id,
            'colony_id': self.colony_id,
            'upgrade_type': self.upgrade_type,
            'upgrade_level': self.upgrade_level,
            'timestamp': self.timestamp
        }

class ColonyRat(Base):
    __tablename__ = 'colony_rat'

    colony_id = Column(Integer, ForeignKey('colony.colony_id'), primary_key=True)
    rat_id = Column(Integer, ForeignKey('plague_rat.rat_id'), primary_key=True)
    role = Column(String(50), default='resident')
    joined_at = Column(DateTime, server_default=func.now())

    colony = relationship("Colony")
    rat = relationship("PlagueRat")

    def serialize(self):
        return {
            'colony_id': self.colony_id,
            'rat_id': self.rat_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class DayNightTime(Base):
    __tablename__ = 'day_night_time'

    time_id = Column(Integer, primary_key=True)
    day_night_period = Column(String(50), nullable=False, unique=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    effect = Column(String(100))

    def serialize(self):
        return {
            'time_id': self.time_id,
            'day_night_period': self.day_night_period,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'effect': self.effect,
        }

class Economy(Base):
    __tablename__ = 'economy'
    transaction_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.player_id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.item_id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False, default=1)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

    player = relationship("Player")
    item = relationship("Item")

    def serialize(self):
        return {
            'transaction_id': self.transaction_id,
            'player_id': self.player_id,
            'item_id': self.item_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

class EffectType(Base):
    __tablename__ = 'effect_type'
    effect_type_id = Column(Integer, primary_key=True)
    effect_type_name = Column(String(100), nullable=False, unique=True)

    def serialize(self):
        return {
            'effect_type_id': self.effect_type_id,
            'effect_type_name': self.effect_type_name
        }

class Equipment(Base):
    __tablename__ = 'equipment'
    equipment_id = Column(Integer, primary_key=True)
    equipment_name = Column(String(255), unique=True, nullable=False)
    equipment_type = Column(String(100))
    description = Column(Text)

    def serialize(self):
        return {
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment_name,
            'equipment_type': self.equipment_type,
            'description': self.description
        }

class GameEvent(Base):
    __tablename__ = 'game_event'

    event_id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    player_id = Column(Integer, ForeignKey('player.player_id'))
    colony_id = Column(Integer, ForeignKey('colony.colony_id'))

    player = relationship("Player")
    colony = relationship("Colony")

    def serialize(self):
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'description': self.description,
            'timestamp': self.timestamp,
            'player_id': self.player_id,
            'colony_id': self.colony_id,
        }

class Item(Base):
    __tablename__ = 'item'

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(255), unique=True, nullable=False)
    item_type = Column(String(100), nullable=False)

    def serialize(self):
        return {
            'item_id': self.item_id,
            'item_name': self.item_name,
            'item_type': self.item_type
        }

class Plague(Base):
    __tablename__ = 'plague'
    plague_id = Column(Integer, primary_key=True, autoincrement=True)
    plague_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    effect_type_id = Column(Integer, ForeignKey('effect_type.effect_type_id'))
    severity_id = Column(Integer, ForeignKey('severity.severity_id'))
    duration = Column(Integer)
    spread_rate = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    effect_type = relationship("EffectType")
    severity = relationship("Severity")

    def serialize(self):
        return {
            'plague_id': self.plague_id,
            'plague_name': self.plague_name,
            'description': self.description,
            'effect_type_id': self.effect_type_id,
            'severity_id': self.severity_id,
            'duration': self.duration,
            'spread_rate': self.spread_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None  # Handle potential None value
        }

class PlagueAffected(Base):
    __tablename__ = 'plague_affected'

    relation_id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    plague_id = Column(Integer, ForeignKey('plague.plague_id'), nullable=False)
    infection_date = Column(DateTime, nullable=False, server_default=func.now())
    recovery_date = Column(DateTime)

    plague = relationship("Plague")

    def serialize(self):
        return {
            'relation_id': self.relation_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'plague_id': self.plague_id,
            'infection_date': self.infection_date,
            'recovery_date': self.recovery_date
        }

class PlagueRat(Base):
    __tablename__ = 'plague_rat'

    rat_id = Column(Integer, primary_key=True)
    species = Column(String(100))
    health = Column(Integer, default=10)
    strength = Column(Integer, default=5)
    colony_id = Column(Integer, ForeignKey('colony.colony_id'))
    evolution_stage = Column(Integer, default=0)
    mutation_type = Column(String(100))

    colony = relationship("Colony")

    def __repr__(self):
        return f"<PlagueRat(rat_id={self.rat_id}, species='{self.species}', health={self.health}, strength={self.strength}, colony_id={self.colony_id}, evolution_stage={self.evolution_stage}, mutation_type='{self.mutation_type}')>"

    def serialize(self):
        return {
            'rat_id': self.rat_id,
            'species': self.species,
            'health': self.health,
            'strength': self.strength,
            'colony_id': self.colony_id,
            'evolution_stage': self.evolution_stage,
            'mutation_type': self.mutation_type
        }

class Player(Base):
    __tablename__ = 'player'
    player_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    join_date = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime)
    current_colony_id = Column(Integer, ForeignKey('colony.colony_id'))

    # Relationship to Colony (optional, if needed)
    current_colony = relationship("Colony")

    def serialize(self):
        return {
            'player_id': self.player_id,
            'username': self.username,
            'email': self.email,
            'join_date': self.join_date,
            'last_login': self.last_login,
            'current_colony_id': self.current_colony_id,
        }

class PlayerAchievement(Base):
    __tablename__ = 'player_achievements'
    player_achievement_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.player_id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.achievement_id'), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship("Player")
    achievement = relationship("Achievement")

    __table_args__ = (
        UniqueConstraint('player_id', 'achievement_id', name='unique_player_achievement'),
    )

    def serialize(self):
        return {
            'player_achievement_id': self.player_achievement_id,
            'player_id': self.player_id,
            'achievement_id': self.achievement_id,
            'granted_at': self.granted_at
        }

class PlayerEquipment(Base):
    __tablename__ = 'player_equipment'
    player_equipment_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.player_id'), nullable=False)
    equipment_id = Column(Integer, ForeignKey('equipment.equipment_id'), nullable=False)
    equipped_slot = Column(String(50))

    player = relationship("Player")
    equipment = relationship("Equipment")

    __table_args__ = (
        UniqueConstraint('player_id', 'equipment_id', 'equipped_slot', name='unique_player_equipment_slot'),
    )

    def serialize(self):
        return {
            'player_equipment_id': self.player_equipment_id,
            'player_id': self.player_id,
            'equipment_id': self.equipment_id,
            'equipped_slot': self.equipped_slot,
        }

class Severity(Base):
    __tablename__ = 'severity'
    severity_id = Column(Integer, primary_key=True)
    severity_name = Column(String(100), unique=True, nullable=False)

    def serialize(self):
        return {
            'severity_id': self.severity_id,
            'severity_name': self.severity_name
        }

class Stats(Base):
    __tablename__ = 'stats'

    player_id = Column(Integer, ForeignKey('player.player_id'), primary_key=True)
    HP = Column(Integer, default=100)
    MP = Column(Integer, default=50)
    AP = Column(Integer, default=10)
    XP = Column(Integer, default=0)
    SP = Column(Integer, default=0)
    x_coordinate = Column(DECIMAL(10, 6))
    y_coordinate = Column(DECIMAL(10, 6))

    player = relationship("Player")

    def serialize(self):
        return {
            'player_id': self.player_id,
            'HP': self.HP,
            'MP': self.MP,
            'AP': self.AP,
            'XP': self.XP,
            'SP': self.SP,
            'x_coordinate': str(self.x_coordinate) if self.x_coordinate else None, # Convert DECIMAL to string
            'y_coordinate': str(self.y_coordinate) if self.y_coordinate else None  # Convert DECIMAL to string
        }

class Weather(Base):
    __tablename__ = 'weather'

    weather_id = Column(Integer, primary_key=True)
    weather_name = Column(String(100), nullable=False, unique=True)
    effect_id = Column(Integer, ForeignKey('weather_effects.effect_id'))

    effect = relationship("WeatherEffects")

    def serialize(self):
        return {
            'weather_id': self.weather_id,
            'weather_name': self.weather_name,
            'effect_id': self.effect_id,
        }

class WeatherEffects(Base):
    __tablename__ = 'weather_effects'

    effect_id = Column(Integer, primary_key=True)
    effect_name = Column(String(100), nullable=False, unique=True)
    effect_description = Column(Text)

    def serialize(self):
        return {
            'effect_id': self.effect_id,
            'effect_name': self.effect_name,
            'effect_description': self.effect_description
        }