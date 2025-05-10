from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import mapped_column

db = SQLAlchemy()


class News(db.Model):
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(100), nullable=False)
    text = mapped_column(Text, nullable=False)
    img = mapped_column(String(255), nullable=False)
    tags = mapped_column(postgresql.ARRAY(String))