from sqlmodel import create_engine
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

conn_str = 'sqlite:///' + os.path.join(BASE_DIR, 'project.db')


engine = create_engine(conn_str, echo=True)