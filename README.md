# UI Test Framework для mebelmart-saratov

Фреймворк для автоматизированного тестирования UI [mebelmart-saratov](https://mebelmart-saratov.ru/) с использованием слоистой архитектуры и Allure отчетности.

## Установка

`python -m venv venv`  
`venv\Scripts\activate`          # Windows  
`source venv/bin/activate`       # Linux/Mac  
`pip install --default-timeout=100 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt`    

## Запуск тестов и отчетов

`pytest --alluredir=allure-results --test-browser=chromium -v`    
`pytest --alluredir=allure-results ./tests -n=5 -v`    
`allure serve allure-results`    
