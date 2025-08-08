import requests

def test_ping():
    """
    Autotest for /ping route.

    Автотест для эндпоинта /ping — проверяет статус 200 и корректный ответ.
    """
    res = requests.get("http://127.0.0.1:8000/ping")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}