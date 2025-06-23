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
