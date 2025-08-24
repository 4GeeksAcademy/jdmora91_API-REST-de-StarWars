from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean(), default=True, nullable=False)
    favorites: Mapped[list["Favorite"]
                      ] = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "favorites": [favorite.serialize() for favorite in self.favorites]
        }

    def __str__(self):
        return f'{self.email}'


class Planet(db.Model):
    __tablename__ = 'planet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    climate: Mapped[Optional[str]] = mapped_column(String(50))
    population: Mapped[Optional[str]] = mapped_column(String(50))

    favorites = relationship("Favorite", back_populates="planet")

    def __str__(self):
        return f'{self.name}'


class Character(db.Model):
    __tablename__ = 'character'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    height: Mapped[Optional[str]] = mapped_column(String(20))
    weight: Mapped[Optional[str]] = mapped_column(String(20))

    favorites = relationship("Favorite", back_populates="character")

    def __str__(self):
        return f'{self.name}'


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[Optional[int]] = mapped_column(ForeignKey('planet.id'))
    character_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('character.id'))
    user = relationship("User", back_populates="favorites")
    planet = relationship("Planet", back_populates="favorites")
    character = relationship("Character", back_populates="favorites")

    def serialize(self):
        return {
        "id": self.id,
        "user_email": self.user.email if self.user else None,
        "planet_name": self.planet.name if self.planet else None,
        "character_name": self.character.name if self.character else None
    }

    def __repr__(self):
        return f"Favorite {self.id}"
