# Лабораторная работа № 20 «Использование паттерна Singleton»
### Выполнил: Кидалов Александр

Выполнение программы: использование паттерна Singleton на примере бронирования толончиков (может быть в поликлинике).

```
import threading # a library for working with threads and locks

# users
user_1 = "Semen"
user_2 = "Meks"

class TicketMachine:
  _instance = None
  _lock = threading.Lock() # object locking

  # creates an automaton variable - free
  def __init__(self):
    self.current_user = None

  def __new__(cls):
    with cls._lock: # blocks the creation of an instance
      if cls._instance is None:
        cls._instance = super().__new__(cls)
        cls._instance.current_user = None
        cls._instance.resource_lock = threading.Lock() # creating a separate lock
      return cls._instance

  def take_ticket(self, user):
    with self.resource_lock: # input security system
      if self.current_user is None:
        self.current_user = user
        print(f"{user} takes ticket.")
      else:
        print(f"{user} can`t take — {self.current_user} is taking ticket.")

  def release_ticket(self, user):
    with self.resource_lock: # input security system
      if self.current_user == user:
        print(f"{user} released machine.")
        self.current_user = None
      else:
        print(f"{user} can`t release — user is not use machine.")

# use program
machine = TicketMachine()
machine.take_ticket(user_1) # Semen takes ticket.
machine.take_ticket(user_2) # Meks can`t take — Semen is taking ticket.
machine.release_ticket(user_1) # Semen released machine.
machine.take_ticket(user_2) # Meks takes ticket.
machine.release_ticket(user_2) # Meks released machine.
```
