from sqlmodel import SQLModel
from models import *
from database import engine

SQLModel.metadata.create_all(engine)