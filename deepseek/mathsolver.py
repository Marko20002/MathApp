# import os
# from dotenv import load_dotenv
# import json
# from pathlib import Path
#
# from agent.normalization import clean_prompt
#
# BASE_DIR = Path(__file__).resolve().parent.parent / "django"
# load_dotenv(BASE_DIR / ".env")
# # Ако моделот врати нешто како: 'Here is the JSON:\n{...}\n' ова ќе проба да го извади првиот JSON објект {...}.
# def _extract_json_object(text: str) -> str | None:
#
#     if not text:
#         return None
#     start = text.find("{")
#     end = text.rfind("}")
#     if start == -1 or end == -1 or end <= start:
#         return None
#     return text[start:end+1]
#
#
# def _get_client():
#     api_key = os.getenv("DEEPSEEK_API_KEY")
#     if not api_key:
#         return None
#
#     from openai import OpenAI
#     return OpenAI(
#         api_key=api_key,
#         base_url="https://api.deepseek.com"
#     )
#
# def solve_math_with_deepseek(task_text: str) -> str:
#     client = _get_client()
#     if client is None:
#         return "DeepSeek е исклучен (нема DEEPSEEK_API_KEY)."
#
#     # 1️⃣ Clean & classify
#     clean_result = clean_prompt(task_text)
#
#     domain = clean_result.domain
#     normalized = clean_result.normalized
#
#     # 2️⃣ Domain-specific instruction
#     if domain == "calculus":
#         problem_text = normalized.get("canonical_ascii", clean_result.core)
#
#     else:
#         problem_text = normalized.get("canonical_text", clean_result.core)
#
#
#     # 3️⃣ Structured prompt
#     payload = {
#         "language": "mk",
#         "domain": domain,
#         "mode": "step_by_step",
#         "problem": problem_text,
#         "instructions": {
#             "format": "json",
#             "steps_required": True,
#             "use_latex": True
#         },
#         "response_schema": {
#             "steps": [
#                 {
#                     "latex": "string",
#                     "explanation": "string"
#                 }
#             ],
#             "final_answer_latex": "string"
#         }
#     }
#
#     try:
#         response = client.chat.completions.create(
#             model="deepseek-reasoner",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a mathematical reasoning engine. Respond ONLY in valid JSON."
#                 },
#                 {
#                     "role": "user",
#                     "content": json.dumps(payload, ensure_ascii=False)
#                 }
#             ],
#             temperature=0.2,
#         )
#
#         content = response.choices[0].message.content
#
#         try:
#             data = json.loads(content)
#         except json.JSONDecodeError:
#             # 5) Salvage JSON if model wrapped it in text
#             candidate = _extract_json_object(content)
#             if candidate:
#                 try:
#                     data = json.loads(candidate)
#                 except json.JSONDecodeError:
#                     return {"error": "Invalid JSON from model", "raw_response": content}
#             else:
#                 return {"error": "Invalid JSON from model", "raw_response": content}
#
#         return data
#
#     except Exception as e:
#         return {"error": "DeepSeek error", "details": str(e)}
from pathlib import Path

from openai import OpenAI
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent / "django"
load_dotenv(BASE_DIR / ".env")


def _get_client():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def solve_math_with_deepseek(task_text: str) -> str:

    client = _get_client()
    prompt = (
        "Ти си математички асистент. Реши ја следната задача чекор по чекор, "
        "објаснувај јасно и на крајот јасно означи го конечниот одговор.\n\n"
        f"{task_text}"
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "You are a helpful math tutor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("DeepSeek error:", repr(e))
        return task_text