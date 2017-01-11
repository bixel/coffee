from database import User as SUser
from database_mongo import (User as MUser,
                            Consumption as MConsumption,
                            Service as MService)

for user in SUser.select():
    new_user = MUser(username=user.username, name=user.name, email=user.email,
                     active=user.active, admin=user.admin).save()
    for c in user.consumptions:
        new_c = MConsumption(date=c.date, units=c.units, user=new_user,
                             price_per_unit=c.price_per_unit).save()
    for s in user.services:
        new_s = MService(date=s.date, service_count=s.service_count,
                         user=new_user).save()
    print(new_user)
