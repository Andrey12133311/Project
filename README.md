# ProcessForge Agent

Универсальный AI-agent для автоматизации корпоративных обращений и процессов. Проект демонстрирует управляемую агентную архитектуру: intake → classification → extraction → risk guard → routing → actions → human approval.

## Возможности

- классификация запроса и приоритета;
- извлечение e-mail, дат, сумм и номеров документов;
- проверка рисков (персональные данные, секреты, критичность, нехватка контекста);
- маршрутизация в профильный бизнес-блок;
- формирование действий и проекта ответа;
- human-in-the-loop для рискованных решений;
- прозрачный audit trail;
- детерминированный fallback без внешней LLM;
- подключение любой OpenAI-compatible LLM через переменные окружения.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

Демо: `GET /demo`.

## Подключение LLM

```bash
export LLM_BASE_URL="https://your-endpoint/v1"
export LLM_API_KEY="..."
export LLM_MODEL="your-model"
```

## Архитектурный принцип

ProcessForge — не просто чат-бот. Он отделяет принятие решения, исполнение и подтверждение человеком. Это позволяет безопасно адаптировать прототип под документооборот, Service Desk, финансы, юридические процессы, CRM и другие корпоративные сценарии.
