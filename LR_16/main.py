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
