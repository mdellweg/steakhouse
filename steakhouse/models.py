import uuid
import datetime
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    UUIDField,
)


STATUS_BURNED = -1
STATUS_WELLDONE = 0
STATUS_MEDIUM = 1
STATUS_RAW = 2
STATUS_CHOICES = (
    (STATUS_BURNED, 'burned'),
    (STATUS_WELLDONE, 'well done'),
    (STATUS_MEDIUM, 'medium'),
    (STATUS_RAW, 'raw'),
)

database = SqliteDatabase('steaks.db', pragmas={'foreign_keys': 1})


def create_tables():
    TABLES = [
        Grill,
        GrillSpice,
        Steak,
        SteakGrill,
        SteakSpice,
    ]
    with database:
        database.create_tables(TABLES)


class Grill(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    created = DateTimeField(default=datetime.datetime.now)
    heartbeat = DateTimeField(null=True)
    class Meta:
        database = database
        only_save_dirty = True


class GrillSpice(Model):
    spice = CharField(unique=True)
    grill = ForeignKeyField(Grill)
    class Meta:
        database = database
        only_save_dirty = True


class Steak(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    status = IntegerField(default=2, choices=STATUS_CHOICES)
    recipe = CharField()
    parameters = CharField(null=True)
    result = CharField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    started = DateTimeField(null=True)
    finished = DateTimeField(null=True)
    class Meta:
        database = database
        only_save_dirty = True


class SteakGrill(Model):
    steak = ForeignKeyField(Steak, unique=True)
    grill = ForeignKeyField(Grill)
    class Meta:
        database = database


class SteakSpice(Model):
    spice = CharField()
    steak = ForeignKeyField(Steak)
    class Meta:
        database = database
        only_save_dirty = True
        indexes=(
            (('spice', 'steak'), True),
        )
