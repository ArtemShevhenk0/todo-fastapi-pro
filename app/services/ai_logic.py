import json

import httpx
from app.core.config import settings
from app.models.models import Task


class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    async def analyze_task(self, title: str, description: str):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'}

        prompt = 'Analyze the task. Return JSON with the fields summary (up to 50 characters), tags (3 tags separated by commas), and difficulty (number 1-10).'

        payload = {
            "model": "nex-agi/nex-n2-pro:free",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Title: {title}, Description: {description}"}
            ],
            "temperature": 0.1
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=20.0
                )
                data = response.json()
                if response.status_code != 200:
                    print(f"OPENROUTER ERROR: {response.status_code} - {response.text}")
                    return {
                        "summary": "Не удалось проанализировать задачу",
                        "tags": "no, tags",
                        "difficulty": 1
                    }
                ai_text = data['choices'][0]['message']['content']
                print(f"DEBUG: AI RAW RESPONSE: {ai_text}")
                ai_text = ai_text.replace("```json", "").replace("```", "").strip()

                try:
                    result = json.loads(ai_text)
                    return result
                except json.JSONDecodeError:
                    print("ERROR: AI returned non-JSON text")
                    return None
        except httpx.RequestError as exc:
            # Обрабатываем ошибки сети (например, таймаут или отсутствие интернета)
            print(f"HTTP REQUEST ERROR: {exc}")
            return None

    async def chat_with_manager(self, question: str, task: list[Task]):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        task_context = "\n".join(", ".join([
            "Задачи:" + str(t.title),
            "Описание:" + str(t.description),
            "Приоритет:" + str(t.priority),
        ])
            for t in task
        )

        prompt = "Ты — умный менеджер задач. Тебе дан список задач пользователя. Отвечай на его вопросы кратко и по делу, опираясь на этот список."

        payload = {
            "model": "nex-agi/nex-n2-pro:free",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Список задач: {task_context}, Вопрос: {question}"}
            ],
            "temperature": 0.4
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url = url,
                    headers= headers,
                    json = payload,
                    timeout= 25.0
                )
                data = response.json()

                if response.status_code != 200:
                    print(f"OPENROUTER ERROR: {response.status_code} - {response.text}")
                    return "Я устал, напиши мне чуть позже"

                ai_text = data['choices'][0]['message']['content']
                print(f"DEBUG: AI RAW RESPONSE: {ai_text}")
                return ai_text
        except httpx.RequestError as exc:
            print(f'HTTP REQUEST ERROR: {exc}')
            return None





async def get_ai_service() -> AIService:
    return AIService(api_key=settings.OPENROUTER_API_KEY)