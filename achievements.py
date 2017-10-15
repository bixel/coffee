from database import Consumption, Service

@Consumption.achievement
def FirstCoffeeOfTheDay(consumption):
    print("This should do stuff to check the first coffee of the day!")

@Service.achievement
def test(service):
    print("Service achievement called")
