# worker/app/models.py
from sqlalchemy import Table, Column, Integer, BigInteger, Boolean, Text, TIMESTAMP, JSON, MetaData

metadata = MetaData()

celebrity_follows = Table(
    'celebrity_follows', metadata,
    Column('id', Integer, primary_key=True),
    Column('celeb_user_id', BigInteger, nullable=False),
    Column('celeb_username', Text),
    Column('target_user_id', BigInteger, nullable=False),
    Column('is_following', Boolean, nullable=False),
    Column('last_update', TIMESTAMP),
    Column('last_event_id', Text),
)

events_log = Table(
    'events_log', metadata,
    Column('id', Integer, primary_key=True),
    Column('event_id', Text, unique=True),
    Column('raw_event', JSON),
    Column('processed', Boolean, default=False),
    Column('error', Text),
)
