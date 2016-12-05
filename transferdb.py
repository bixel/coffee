from sqlalchemy import (Column,
                        String,
                        Integer,
                        ForeignKey,
                        Boolean,
                        DateTime,
                        Date,
                        create_engine,
                        )
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import User as NewUser
from database import Consumption as NewConsumption
from database import Transaction as NewTransaction
from database import Service as NewService
from database import db
from datetime import datetime

import sys

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    name = Column(String(80), unique=True)
    email = Column(String(120), unique=True)
    payments = relationship('Payment', backref='user', lazy='dynamic')
    consumptions = relationship('Consumption', backref='user',
                                   lazy='dynamic')
    services = relationship('Service', backref='user', lazy='dynamic')
    active = Column(Boolean)
    vip = Column(Boolean, default=False)

    def __init__(self, name=None, username=None, email=None):
        if name:
            self.name = name
        if username:
            self.username = username
        if email:
            self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @property
    def balance(self):
        s = 0
        for p in self.payments:
            s += p.amount
        for c in self.consumptions:
            s += c.amountPaid
        return s

    @property
    def total_consumption(self):
        return self.consumptions(func.sum(Consumption.units)).scalar()

    @property
    def score(self):
        services = 0
        consumptions = 1
        now = datetime.utcnow()
        for s in self.services.filter(
            Service.end_date > date(*app.config['INITIAL_SCORE_DATE'])
        ):
            timediff = now.date() - s.end_date
            services += s.service_count * exp(-timediff.days / 365)
        for c in self.consumptions.filter(
            Consumption.date > datetime(*app.config['INITIAL_SCORE_DATE'])
        ):
            timediff = now - c.date
            units = c.units or 0
            consumptions += units * exp(-timediff.days / 365)
        return services**3 / consumptions


class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    budgetChanges = relationship('BudgetChange', backref='Payment',
                                    lazy='dynamic')

    def __init__(self, amount=None, date=None):
        if amount:
            self.amount = amount
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<Payment %r>' % self.id


class Consumption(Base):
    __tablename__ = 'consumption'
    id = Column(Integer, primary_key=True)
    units = Column(Integer)
    amountPaid = Column(Integer)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))

    def __init__(self, amountPaid=None, units=None, date=None):
        if units:
            self.units = units
        self.amountPaid = amountPaid or 0
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<Consumption %r>' % self.id


class BudgetChange(Base):
    __tablename__ = 'budget_change'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    description = Column(String(200))
    date = Column(DateTime)
    payment_id = Column(Integer, ForeignKey('payment.id'))

    def __init__(self, amount=None, description=None, date=None):
        if amount:
            self.amount = amount
        if description:
            self.description = description
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<BudgetChange %r>' % self.description


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)
    user_id = Column(Integer, ForeignKey('user.id'))
    service_count = Column(Integer)

    def __init__(self, start=None, end=None, user_id=None, service_count=None):
        self.start_date = start or datetime.utcnow()
        self.end_date = end or self.start_date + timedelta(days=5)
        self.user_id = user_id
        self.service_count = (service_count
                              or (self.end_date - self.start_date).days + 1)

    def __repr__(self):
        return '<Service {} to {}>'.format(self.start_date, self.end_date)


engine = create_engine('sqlite:///' + sys.argv[1])
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


if __name__ == '__main__':
    db.create_tables([NewUser, NewConsumption, NewTransaction, NewService])

    s = session()

    DB_DATE = datetime(2013, 10, 20)

    print('Transferring currently active Users.')
    users = s.query(User).all()
    for user in users:
        new = NewUser(username=user.username, name=user.name, email=user.email,
                      vip=user.vip, active=user.active)
        stored = new.save()

        past_consume = 0
        for c in user.consumptions:
            if c.date >= DB_DATE:
                try:
                    units = c.units or 1
                    new_con = NewConsumption(date=c.date, user=new, units=units,
                                             price_per_unit=(-c.amountPaid / units))
                    stored = new_con.save()
                except:
                    print('Error transferring {}'.format(c), c.units, c.amountPaid)
            else:
                past_consume += c.amountPaid

        past_payments = 0
        for t in user.payments:
            if t.date >= DB_DATE:
                try:
                    new_t = NewTransaction(
                        date=t.date, user=new, diff=t.amount,
                        description='Payment of {} from {}'.format(t.amount, user.name)
                    )
                    stored = new_t.save()
                except:
                    print("Error transferring", t)
            else:
                past_payments += t.amount

        past_balance = past_payments + past_consume
        if past_balance:
            new_t = NewTransaction(date=DB_DATE, user=new, diff=past_balance,
                                   description='{} Budget from old database'.format(past_balance))
            print(new_t)
            new_t.save()

        for service in user.services.all():
            try:
                new_s = NewService(date=service.end_date,
                        service_count=service.service_count, user=new)
                new_s.save()
            except:
                raise
                print("Error transferring", service)

    print('Transferring expenses.')
    for expense in s.query(BudgetChange).filter(BudgetChange.payment_id==None, ~BudgetChange.description.like('Payment from%')):
        try:
            new_t = NewTransaction(date=expense.date,
                                   diff=expense.amount,
                                   description=expense.description)
            new_t.save()
        except:
            print("Error transferring", expense)
