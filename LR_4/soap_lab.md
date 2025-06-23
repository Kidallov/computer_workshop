
# Лабораторная работа: Использование открытых SOAP-сервисов и тестирование в SoapUI

**Дата:** 23.06.2025  
**ФИО:** Кидалов А.А.  
**Инструменты:** SoapUI, публичные SOAP-сервисы  

---

## Цель работы

Изучить работу с SOAP веб-сервисами, реализовать бизнес-процесс на основе открытого публичного SOAP API и выполнить его тестирование с помощью SoapUI.

---

## Выбранный SOAP-сервис

**Сервис:** [Currency Converter WSDL](https://www.dataaccess.com/webservicesserver/NumberConversion.wso?WSDL)  
**Описание:** Сервис предоставляет методы для конвертации чисел в текстовое представление.

---

## Бизнес-процесс: Конвертация чисел в текстовое значение

### Сценарий:
1. Пользователь вводит число.
2. Система отправляет запрос к SOAP-сервису для получения текстового значения числа.
3. Возвращается строка, содержащая число словами.
4. Эта строка используется, например, для формирования текстовой квитанции.

---

## Структура запроса (SOAP)

**Метод:** `NumberToWords`  
**Пример запроса:**
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:web="http://www.dataaccess.com/webservicesserver/">
   <soapenv:Header/>
   <soapenv:Body>
      <web:NumberToWords>
         <web:ubiNum>123</web:ubiNum>
      </web:NumberToWords>
   </soapenv:Body>
</soapenv:Envelope>
```

---

## Реализация в SoapUI

1. Создайте новый SOAP-проект с WSDL:  
   `https://www.dataaccess.com/webservicesserver/NumberConversion.wso?WSDL`

2. Выберите метод `NumberToWords`.

3. Создайте новый **TestSuite** и **TestCase**:
   - TestStep: `NumberToWords`
   - В теле запроса укажите различные значения:
     - 1
     - 123
     - 1005

4. Добавьте **Assertions**:
   - Проверка наличия строки `<NumberToWordsResult>one hundred twenty three</NumberToWordsResult>`.

---

## Пример ответа от сервиса

```xml
<NumberToWordsResult>one hundred twenty three </NumberToWordsResult>
```

---

## Вывод

Был реализован простой бизнес-процесс на основе SOAP API: числовое значение переводится в текстовое, и результат используется в бизнес-логике. SoapUI позволяет эффективно тестировать такие сервисы через сценарии.

---

## Примечание

SOAP-сервисы активно используются в системах электронного документооборота, банковских системах и госуслугах.

