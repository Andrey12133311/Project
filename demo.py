from pprint import pprint
from agent import CorporateProcessAgent
from models import ProcessRequest

agent = CorporateProcessAgent()
result = agent.process(ProcessRequest(text=(
    "Срочно: по договору № 45/26 от 08.11.2026 не прошла оплата 250 000 руб. "
    "Контакт finance@example.ru. Просим проверить и дать статус сегодня."
)))
pprint(result.model_dump())
