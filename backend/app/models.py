from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import enum


Base = declarative_base()


class UserProfile(Base):
    __tablename__ = 'user_profile'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    email = Column(String(255))
    date_birthday = Column(String(255), nullable=True)
    restriction_health = Column(String(255), nullable=True)
    token_auth = Column(String(255), nullable=False, unique=True)


class GeoData(Base):
    __tablename__ = 'geo_data'

    id = Column(Integer, primary_key=True)
    coordinates = Column(ARRAY(Float))


class PlantingStatus(Base):
    __tablename__ = 'planting_status'

    id = Column(Integer, primary_key=True)
    status_name = Column(String)
    percent_value = Column(Float)
    global_id = Column(Integer)
    is_deleted = Column(Integer)

    green_planting_id = Column(Integer, ForeignKey('green_plantings.id'))


class GreenPlanting(Base):
    __tablename__ = 'green_plantings'

    id = Column(Integer, primary_key=True)
    period = Column(Integer)
    global_id = Column(Integer)
    adm_area = Column(String)
    district = Column(String)
    address = Column(String)

    geo_data_id = Column(Integer, ForeignKey('geo_data.id'))
    geo_data = relationship("GeoData", backref="green_plantings")

    statuses = relationship("PlantingStatus", backref="green_planting", cascade="all, delete-orphan")


class Entry(Base):
    __tablename__ = 'entries'

    global_id = Column(Integer, primary_key=True)
    number = Column(Integer)
    green_planting_id = Column(Integer, ForeignKey('green_plantings.id'))
    green_planting = relationship("GreenPlanting", backref="entry")


class TreeSpecies(Base):
    __tablename__ = 'tree_species'

    id = Column(Integer, primary_key=True)
    tree = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)

    trees = relationship("TreeData", back_populates="species")


class TreeData(Base):
    class TreeCondition(enum.Enum):
        good = "хорошее"
        satisfactory = "удовлетворительное"
        poor = "неудовлетворительное"

    __tablename__ = 'tree_data'

    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    condition = Column(Enum(TreeCondition), nullable=False)
    last_assessed = Column(DateTime, default=datetime.utcnow)
    is_accurate = Column(Boolean, default=True)

    species_id = Column(Integer, ForeignKey('tree_species.id'), nullable=False)
    species = relationship("TreeSpecies", back_populates="trees")
