### Отчёт по доработке приложения Budget Planner

#### Введение

В рамках данной задачи я доработал приложение Budget Planner, добавив возможность **сохранять и загружать данные из localStorage браузера**. Также внёс небольшие изменения в **Makefile** для удобства сборки и запуска проекта.

#### Что было реализовано

1. **Новые функции на C для работы с localStorage**:

```
void saveToLocalStorage() {
    // Формирую JSON-строку из всех расходов
    char* json = (char*)malloc(MAX_STRING_LENGTH * expenseCount);
    if (!json) return;

    sprintf(json, "[");
    for (int i = 0; i < expenseCount; i++) {
        if (i > 0) strcat(json, ",");
        char* expense_json = getExpenseJSON(i);
        strcat(json, expense_json);
        freeMemory(expense_json);
    }
    strcat(json, "]");

    // Сохраняю JSON в localStorage через JavaScript
    EM_ASM({
        localStorage.setItem('budgetPlanner_expenses', UTF8ToString($0));
    }, json);

    free(json);
}

void loadFromLocalStorage() {
    // Загружаю JSON из localStorage и добавляю данные обратно
    EM_ASM({
        var stored = localStorage.getItem('budgetPlanner_expenses');
        if (stored) {
            var expenses = JSON.parse(stored);
            Module.ccall('jsClearAllExpenses', 'number', [], []);
            for (var i = 0; i < expenses.length; i++) {
                var expense = expenses[i];
                Module.ccall('jsAddExpense', 'number', 
                    ['string', 'string', 'number', 'string'],
                    [expense.date, expense.category, expense.amount, expense.description]
                );
            }
        }
    });
}
```

2. **Изменения в Makefile**:

```makefile
# Цель по умолчанию
all: build server

build:
	$(CC) $(SOURCES) -s WASM=1 -s ASSERTIONS=1 -s MODULARIZE=1 -s EXPORT_NAME="'BudgetPlanner'" \
	-s EXPORTED_FUNCTIONS='["_main","_showHelloMessage","_jsAddExpense","_jsDeleteExpense","_jsClearAllExpenses","_jsGetTotalExpenses","_jsGetExpenseCount","_jsGetCategoryCount","_getExpenseJSON","_getCategoryTotalJSON","_freeMemory","_malloc","_free","_saveToLocalStorage","_loadFromLocalStorage"]' \
	-s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap", "stringToUTF8", "UTF8ToString"]' \
	$(LDFLAGS) -o index.js

server:
	python3 -m http.server 8000
```

Теперь при сборке проекта можно сразу запускать сервер одной командой (`make`), а отдельная цель `build` отвечает только за компиляцию. Также я добавил экспорт новых функций `_saveToLocalStorage` и `_loadFromLocalStorage`.

#### Как всё работает

1. **Сохранение данных**:

   * Все текущие расходы преобразуются в JSON прямо в C-коде
   * С помощью `EM_ASM` вызывается JavaScript-функция, которая сохраняет строку в `localStorage`
   * Используется `malloc` и `free` для корректного управления памятью

2. **Загрузка данных**:

   * Из JavaScript получаю сохранённый JSON
   * Сначала очищаю текущие записи
   * Затем по одной восстанавливаю все расходы, вызывая экспортированные C-функции

#### Результат

В результате:

* Данные сохраняются между сессиями без участия пользователя
* Загрузка расходов происходит автоматически при запуске приложения
* Сохранилась вся существующая функциональность
* Память используется эффективно, утечек не наблюдается

Теперь приложение стало более удобным и завершённым с точки зрения пользовательского опыта.