import random
import pendulum

from database import Consumption, Service, Achievement, AchievementDescriptions


@Consumption.achievement_function
def FirstCoffeeOfTheDay(consumption):
    # define some motivational descriptions
    description_pool = (AchievementDescriptions.objects(key='first_coffee_of_the_day').first().descriptions)
    # first, get the date of the last coffee
    last_day = Consumption.objects.order_by('-date').first().date.date()
    print(consumption.date.date(), last_day, consumption.date.date() > last_day)
    if consumption.date.date() > last_day:
        print('new Achievement!')
        new = Achievement(description=random.choice(description_pool),
                          key='first_coffee_of_the_day')
        consumption.user.achievements.append(new)
        consumption.user.save()


@Service.achievement_function
def test(service):
    print("Service achievement called")
