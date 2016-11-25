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


engine = create_engine('sqlite:///coffee.dev.db')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


if __name__ == '__main__':
    s = session()
    print('Transferring Users')
    users = s.query(User).all()
    for user in users:
        new = NewUser(username=user.username, name=user.name, email=user.email,
                      vip=user.vip, active=user.active)
