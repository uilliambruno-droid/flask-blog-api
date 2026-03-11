import sqlalchemy as sa
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db

bcrypt = Bcrypt()


class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String, unique=True)
    password: Mapped[str] = mapped_column(sa.String, nullable=False)
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("role.id"), nullable=False)
    role: Mapped["Role"] = relationship(back_populates="users")

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password, password)
        except ValueError:
            return self.password == password

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
