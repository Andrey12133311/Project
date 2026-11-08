from __future__ import annotations
import re
import uuid
from dataclasses import dataclass
from typing import Dict, List
from llm import LLMClient
from models import AgentStep, ProcessRequest, ProcessResult

CATEGORY_RULES = {
    "incident": ["ошибка", "не работает", "сбой", "авария", "недоступ", "инцидент"],
    "finance": ["счет", "оплата", "платеж", "возврат", "сверка", "акт", "счёт"],
    "contract": ["договор", "допсоглаш", "контракт", "услови", "пролонгац"],
    "access": ["доступ", "роль", "пароль", "учетн", "аккаунт", "логин"],
    "document": ["документ", "письмо", "справк", "заявлен", "обращен", "согласован"],
}
ROUTES = {
    "incident": "IT / Service Desk",
    "finance": "Финансы",
    "contract": "Юридический блок",
    "access": "IAM / IT",
    "document": "Документооборот",
    "general": "Операционный центр",
}
HIGH_WORDS = ["срочно", "критично", "простой", "утечка", "взлом", "блокировка", "штраф", "сегодня"]
CRITICAL_WORDS = ["утечка данных", "взлом", "ransomware", "персональные данные утекли"]

@dataclass
class Classification:
    category: str
    priority: str
    confidence: float

class CorporateProcessAgent:
    def __init__(self):
        self.llm = LLMClient()

    def _classify_rules(self, text: str) -> Classification:
        t = text.lower()
        scores = {k: sum(1 for w in ws if w in t) for k, ws in CATEGORY_RULES.items()}
        category = max(scores, key=scores.get) if max(scores.values(), default=0) > 0 else "general"
        top = scores.get(category, 0)
        confidence = min(0.55 + 0.12 * top, 0.92) if top else 0.45
        if any(w in t for w in CRITICAL_WORDS):
            priority = "critical"
        elif any(w in t for w in HIGH_WORDS):
            priority = "high"
        else:
            priority = "normal"
        return Classification(category, priority, confidence)

    def _extract(self, text: str) -> Dict:
        return {
            "emails": re.findall(r"[\w.+'-]+@[\w.-]+\.[A-Za-z]{2,}", text)[:10],
            "dates": re.findall(r"\b(?:0?[1-9]|[12]\d|3[01])[./-](?:0?[1-9]|1[0-2])[./-](?:20)?\d{2}\b", text)[:10],
            "amounts": re.findall(r"\b\d[\d\s]*(?:[.,]\d+)?\s*(?:₽|руб(?:лей|ля|.)?)\b", text, flags=re.I)[:10],
            "document_numbers": re.findall(r"(?:№|N)\s*[A-Za-zА-Яа-я0-9/_-]+", text)[:10],
        }

    def _risk_checks(self, text: str, cls: Classification) -> List[str]:
        t = text.lower()
        risks: List[str] = []
        if cls.priority in {"high", "critical"}:
            risks.append("Повышенный приоритет: требуется ускоренная проверка человеком")
        if "персональн" in t or "паспорт" in t or "снилс" in t:
            risks.append("Возможны персональные данные: ограничить доступ и логирование содержимого")
        if "пароль" in t or "токен" in t or "секрет" in t:
            risks.append("В тексте могут быть секреты доступа: скрыть перед передачей в модель")
        if len(text) < 25:
            risks.append("Недостаточно контекста для уверенного автоматического решения")
        return risks

    def _llm_enrich(self, text: str) -> Dict | None:
        system = (
            "Ты корпоративный process-agent. Верни только JSON с ключами category, priority, "
            "confidence, route_to, suggested_actions, draft_reply. Не выдумывай факты. "
            "Если данных недостаточно, требуй human approval."
        )
        try:
            return self.llm.json_completion(system, text)
        except Exception:
            return None

    def process(self, req: ProcessRequest) -> ProcessResult:
        run_id = uuid.uuid4().hex[:12]
        steps: List[AgentStep] = []
        text = " ".join(req.text.split())
        steps.append(AgentStep(name="intake", status="ok", summary="Запрос нормализован", data={"chars": len(text)}))

        cls = self._classify_rules(text)
        steps.append(AgentStep(name="classification", status="ok", summary=f"{cls.category} / {cls.priority}", data={"confidence": cls.confidence}))

        extracted = self._extract(text)
        steps.append(AgentStep(name="extraction", status="ok", summary="Извлечены структурированные реквизиты", data=extracted))

        risks = self._risk_checks(text, cls)
        steps.append(AgentStep(name="risk_guard", status="needs_human" if risks else "ok", summary="; ".join(risks) if risks else "Критичных рисков не найдено"))

        route = ROUTES.get(cls.category, ROUTES["general"])
        actions = [
            f"Создать карточку процесса и направить в «{route}»",
            "Приложить извлечённые реквизиты и исходный текст",
            "Зафиксировать SLA и следующий контрольный срок",
        ]
        if cls.priority in {"high", "critical"}:
            actions.insert(0, "Немедленно уведомить ответственного владельца процесса")

        draft = (
            "Запрос принят и классифицирован. Материалы направлены ответственному подразделению. "
            "После проверки исходных данных будет определено дальнейшее действие; при нехватке сведений "
            "мы запросим уточнение."
        )

        enriched = self._llm_enrich(text)
        if enriched:
            cls = Classification(
                str(enriched.get("category", cls.category)),
                str(enriched.get("priority", cls.priority)),
                float(enriched.get("confidence", cls.confidence)),
            )
            route = str(enriched.get("route_to", route))
            actions = list(enriched.get("suggested_actions", actions))
            draft = str(enriched.get("draft_reply", draft))
            steps.append(AgentStep(name="llm_enrichment", status="ok", summary="LLM уточнила маршрутизацию и проект ответа"))
        else:
            steps.append(AgentStep(name="llm_enrichment", status="warning", summary="LLM не настроена/недоступна — использован детерминированный режим"))

        human = bool(risks or cls.confidence < 0.65 or cls.priority == "critical")
        steps.append(AgentStep(name="human_gate", status="needs_human" if human else "ok", summary="Требуется подтверждение" if human else "Можно продолжить автоматически"))

        return ProcessResult(
            run_id=run_id,
            category=cls.category,
            priority=cls.priority,
            confidence=max(0.0, min(1.0, cls.confidence)),
            route_to=route,
            extracted=extracted,
            risks=risks,
            suggested_actions=actions,
            draft_reply=draft,
            human_approval_required=human,
            steps=steps,
        )
