from peewee import (SqliteDatabase,
                    CharField,
                    BooleanField,
                    Model,
                    IntegerField,
                    ForeignKeyField,
                    DateField,
                    DateTimeField,
                    DeferredRelation,
                    fn,
                    JOIN,
                    )

from math import exp

import os
from datetime import datetime

FILENAME = os.environ.get('DBFILE') or 'coffee.db'
DBPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      FILENAME)

db = SqliteDatabase(DBPATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    name = CharField(null=True)
    email = CharField(null=True)
    active = BooleanField(default=True)
    vip = BooleanField(default=False)
    admin = BooleanField(default=False)

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.username

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active

    @property
    def balance(self):
        return self.payments - self.consume

    @property
    def payments(self):
        return (User
                .select(fn.SUM(Transaction.diff).alias('_payments'))
                .where(User.id==self.id)
                .join(Transaction, JOIN.LEFT_OUTER)
                .get()
                ._payments) or 0

    @property
    def score(self):
        services = 0
        consumptions = 1
        now = datetime.now()
        for s in self.services:
            timediff = now.date() - s.date
            services += s.service_count * exp(-timediff.days / 365)
        for c in self.consumptions:
            timediff = now - c.date
            units = c.units or 0
            consumptions += units * exp(-timediff.days / 365)
        return services**3 / consumptions

    @property
    def consume(self):
        return (User
                .select(fn.SUM(Consumption.units * Consumption.price_per_unit).alias('_consume'))
                .where(User.id==self.id)
                .join(Consumption, JOIN.LEFT_OUTER)
                .get()
                ._consume) or 0

    def get_uids():
        users = User.select().order_by(User.username)
        return map(lambda u: (u.id, u.name), users)

    def __str__(self):
        return 'User `{}`'.format(self.username)


class Transaction(BaseModel):
    date = DateTimeField(default=datetime.now)
    user = ForeignKeyField(User, null=True, related_name='transactions')
    description = CharField()
    diff = IntegerField()

    def __str__(self):
        return self.description


class Service(BaseModel):
    date = DateField()
    user = ForeignKeyField(User, related_name='services')
    service_count = IntegerField(default=1)


class Consumption(BaseModel):
    date = DateTimeField(default=datetime.now)
    units = IntegerField(default=1)
    price_per_unit = IntegerField()
    user = ForeignKeyField(User, related_name='consumptions')

    def __str__(self):
        return '{}\'s consumtion of {} units, {} each'.format(
            self.user.name,
            self.units,
            self.price_per_unit,
        )
