# Лабораторная работа №16: Аномалия «Потерянное обновление» в базе данных

## Цель работы

Показать, как при недостаточно строгом уровне изоляции транзакций в базе данных возможно возникновение аномалии **«Потерянное обновление»**, привести пример её проявления и предложить способы предотвращения.

---

## Пример с допущенной аномалией

В приведённом ниже коде реализуется параллельное выполнение двух транзакций, которые читают одно и то же значение и обновляют его, не зная о действиях друг друга.

```python
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

def transaction1():
    conn = sqlite3.connect('test.db', isolation_level=None)
    c = conn.cursor()

    c.execute('BEGIN TRANSACTION')
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
    conn = sqlite3.connect('test.db', isolation_level=None)
    c = conn.cursor()

    time.sleep(1)

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

    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('SELECT balance FROM accounts WHERE id=1')
    final_balance = c.fetchone()[0]
    conn.close()
    print(f'Итоговый баланс: {final_balance}')

if __name__ == "__main__":
    main()
````

### Результат выполнения

Ожидается, что:

* transaction1 добавляет 50,
* transaction2 добавляет 100.

Однако при параллельной работе итог может оказаться либо **150**, либо **200**, т.е. **одно из обновлений теряется**.

---

## Исправление с использованием `BEGIN IMMEDIATE`

Чтобы избежать аномалии, вводится строгий контроль за доступом к записи через механизм **блокировок**:

```python
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
        c.execute('BEGIN IMMEDIATE')  # Попытка блокировки
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

### Результат

Теперь одна из транзакций получает **исключительный доступ**, и вторая **ждёт или получает ошибку**, если не может захватить блокировку. Итоговое значение баланса будет **250**, как и ожидалось (100 + 50 + 100).

---

## Вывод

Аномалия **«Потерянное обновление»** возникает при параллельной работе транзакций, которые читают и обновляют одни и те же данные без должной синхронизации. В SQLite её можно устранить с помощью режима `BEGIN IMMEDIATE`, который гарантирует, что только одна транзакция имеет доступ к записи в данный момент. Такой подход обеспечивает корректное выполнение операций и сохранность данных.
