#database.py
import os
# Импортируем библиотеку для работы с базой данных (БД)
import ydb

# Получаем переменные подключения к БД из окружения
YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")

def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    # Задаем конфигурацию драйвера, параметры подключения
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    # Инициализируем драйвер
    ydb_driver = ydb.Driver(ydb_driver_config)
    # Ожидаем, пока драйвер станет активным для запросов.
    ydb_driver.wait(fail_fast=True, timeout=timeout)

    # Возвращаем пул сессий
    return ydb.SessionPool(ydb_driver)

# Функция форматирования входных аргументов
def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/docs/ru/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        # Наши подготовленные, параметризованные запросы
        prepared_query = session.prepare(query)

        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
    # Реализация стратегии повторных запросов
    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/docs/ru/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)

# Зададим настройки базы данных
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза
