# Лабораторная работа № 16

Пример аномалии «Потерянное обновление» в SQLite:

```
import sqlite3
import threading
import time

# Создаём и инициализируем таблицу
def init_db():
    conn = sqlite3.connect('test.db', isolation_level=None)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS accounts')
    c.execute('CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER)')
    c.execute('INSERT INTO accounts (balance) VALUES (100)')
    conn.commit()
    conn.close()


# Функция имитирующая транзакцию 1
def transaction1():
    conn = sqlite3.connect('test.db', isolation_level=None)
    c = conn.cursor()

    c.execute('BEGIN TRANSACTION')
    c.execute('SELECT balance FROM accounts WHERE id=1')
    balance = c.fetchone()[0] # возвращает первую запись из таблицы
    print(f'Transaction1: прочитал баланс {balance}')

    time.sleep(2)  # Задержка, чтобы транзакция 2 успела прочитать старое значение

    new_balance = balance + 50
    c.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
    print(f'Transaction1: записал баланс {new_balance}')

    conn.commit()
    print('Transaction1: commit')
    conn.close()


# Функция имитирующая транзакцию 2
def transaction2():
    conn = sqlite3.connect('test.db', isolation_level=None)
    c = conn.cursor()

    time.sleep(1)  # Ждем, чтобы transaction1 успела прочитать баланс

    c.execute('BEGIN TRANSACTION')
    c.execute('SELECT balance FROM accounts WHERE id=1')
    balance = c.fetchone()[0]
    print(f'Transaction2: прочитал баланс {balance}')

    new_balance = balance + 100
    c.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
    print(f'Transaction2: записал баланс {new_balance}')

    conn.commit()
    print('Transaction2: commit')
    conn.close()


def main():
    init_db()

    t1 = threading.Thread(target=transaction1)
    t2 = threading.Thread(target=transaction2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # Проверим итоговое значение баланса
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM accounts WHERE id=1')
    final_balance = c.fetchone()[0]
    conn.close()
    print(f'Итоговый баланс: {final_balance}')


if __name__ == "__main__":
    main()
```

#### Что здесь происходит?
•	Начальный баланс — 100.
•	Транзакция 1 читает баланс = 100, ждёт 2 секунды, затем записывает баланс + 50 = 150.
•	Транзакция 2 в это время читает тот же баланс = 100 (т.к. transaction1 ещё не сделала коммит), добавляет +100 и записывает 200.
•	Итог: обновление транзакции 1, которое добавляет +50, теряется, так как транзакция 2 переписывает значение, считанное до обновления transaction1.

#### Результат:
Transaction1: прочитал баланс 100
Transaction2: прочитал баланс 100
Transaction2: записал баланс 200
Transaction2: commit
Transaction1: записал баланс 150
Transaction1: commit
Итоговый баланс: 150
•	Вместо 250 (100 + 50 + 100) в базе — только 150.
•	Это и есть аномалия «Потерянное обновление».

#### Как избежать аномалии?

1. Использовать блокировки:
•	Явное блокирование записей (SELECT ... FOR UPDATE в СУБД, поддерживающих это).
•	В SQLite — использовать BEGIN EXCLUSIVE TRANSACTION для запрета доступа другим транзакциям.
2. Повысить уровень изоляции транзакций:
•	SERIALIZABLE (не все СУБД это поддерживают в полной мере).
3. Использовать оптимистичные блокировки:
•	Хранить версию записи и проверять, не изменена ли она при коммите.
4. Повторять транзакцию при конфликте:
•	Если обнаружено несоответствие, прервать и попробовать заново.


Исправленный вариант, чтобы избежать "потери обновления":

```
import sqlite3
import threading
import time

def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS accounts')
    c.execute('CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INTEGER)')
    c.execute('INSERT INTO accounts (balance) VALUES (100)')
    conn.commit()
    conn.close()

def transaction1():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()

    c.execute('BEGIN IMMEDIATE')  # Устанавливаем блокировку записи
    c.execute('SELECT balance FROM accounts WHERE id=1')
    balance = c.fetchone()[0]
    print(f'Transaction1: прочитал баланс {balance}')

    time.sleep(2)

    new_balance = balance + 50
    c.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
    print(f'Transaction1: записал баланс {new_balance}')

    conn.commit()
    print('Transaction1: commit')
    conn.close()

def transaction2():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()

    time.sleep(1)

    try:
        c.execute('BEGIN IMMEDIATE')  # Блокировка не будет установлена, если первая транзакция ещё держит
        c.execute('SELECT balance FROM accounts WHERE id=1')
        balance = c.fetchone()[0]
        print(f'Transaction2: прочитал баланс {balance}')

        new_balance = balance + 100
        c.execute('UPDATE accounts SET balance=? WHERE id=1', (new_balance,))
        print(f'Transaction2: записал баланс {new_balance}')

        conn.commit()
        print('Transaction2: commit')
    except sqlite3.OperationalError as e:
        print(f'Transaction2: ошибка — {e}')
    finally:
        conn.close()

def main():
    init_db()

    t1 = threading.Thread(target=transaction1)
    t2 = threading.Thread(target=transaction2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM accounts WHERE id=1')
    final_balance = c.fetchone()[0]
    conn.close()
    print(f'Итоговый баланс: {final_balance}')

if __name__ == "__main__":
    main()
```
