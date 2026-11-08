from agent import CorporateProcessAgent
from models import ProcessRequest

def test_finance_high_priority_and_extraction():
    agent = CorporateProcessAgent()
    result = agent.process(ProcessRequest(text=(
        "Срочно: по договору № 45/26 от 08.11.2026 не прошла оплата 250 000 руб. "
        "Контакт finance@example.ru. Просим проверить и дать статус сегодня."
    )))
    assert result.category == "finance"
    assert result.priority == "high"
    assert result.route_to == "Финансы"
    assert "finance@example.ru" in result.extracted["emails"]
    assert result.human_approval_required is True

def test_access_routing():
    agent = CorporateProcessAgent()
    result = agent.process(ProcessRequest(text=(
        "Сотруднику требуется доступ к корпоративной системе, роль аналитика не назначена."
    )))
    assert result.category == "access"
    assert result.route_to == "IAM / IT"

def test_short_request_requires_human():
    agent = CorporateProcessAgent()
    result = agent.process(ProcessRequest(text="Ошибка входа"))
    assert result.human_approval_required is True
    assert any("Недостаточно контекста" in risk for risk in result.risks)
