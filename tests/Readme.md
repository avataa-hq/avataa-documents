### Запуск юнит тестов:
1. Установить requirements.txt из корневого каталога
2. Запустить контейнер с БД из корневого каталога:
    > docker-compose -f docker-compose.local.yml up -d --build
3. Установить зависимости для тестов:
    > pip install pytest requests
4. Запустить тесты из директории tests_unit:
    > pytest -v --disable-warnings routers/
5. Для отображения принтов в тестах к команде pytest добавить флаг -s



В данных тестах запросы отправляются на запущенный сервис при помощи бибилиотеки requests.
При использовании Testclient возникали ошибки внутри кода самого приложения, с которыми не получилось разобраться.
В conftest.py есть одна закомментированная фикстура "client_session". Если ее раскомментировать и закоментировать фикстуру перед ней,
то вместо requests будет использоваться Testclient.


Отчета по покрытию тестами сделать не получися, так кау использовуется requests.


### Полезные ссылки:
1. Документация FastAPI по тестированию
    1. https://fastapi.tiangolo.com/tutorial/testing/
    2. https://fastapi.tiangolo.com/advanced/testing-dependencies/
    3. https://fastapi.tiangolo.com/advanced/testing-database/
2. Документация SQLModel по тестированию
    1. https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/
