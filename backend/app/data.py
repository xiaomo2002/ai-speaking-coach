"""Canonical question bank shared by the API."""
from .models import LessonOut

LESSONS: list[LessonOut] = [
    LessonOut(
        id="daily", title="日常打招呼", subtitle="Everyday", icon="👋",
        questions=[
            {"id": "daily-1", "text": "Hello, nice to meet you.", "translation": "你好，很高兴认识你。"},
            {"id": "daily-2", "text": "How are you doing today?", "translation": "你今天过得怎么样？"},
            {"id": "daily-3", "text": "My name is Alex.", "translation": "我叫 Alex。"},
            {"id": "daily-4", "text": "Where are you from?", "translation": "你来自哪里？"},
            {"id": "daily-5", "text": "Have a wonderful day!", "translation": "祝你今天愉快！"},
        ],
    ),
    LessonOut(
        id="coffee", title="咖啡店点单", subtitle="Coffee Shop", icon="☕",
        questions=[
            {"id": "coffee-1", "text": "I would like a cup of coffee.", "translation": "我想要一杯咖啡。"},
            {"id": "coffee-2", "text": "Can I see the menu?", "translation": "我可以看一下菜单吗？"},
            {"id": "coffee-3", "text": "Do you have oat milk?", "translation": "你们有燕麦奶吗？"},
            {"id": "coffee-4", "text": "How much does it cost?", "translation": "这个多少钱？"},
            {"id": "coffee-5", "text": "Can I pay by card?", "translation": "我可以刷卡吗？"},
        ],
    ),
    LessonOut(
        id="travel", title="旅行与问路", subtitle="Travel", icon="✈️",
        questions=[
            {"id": "travel-1", "text": "Where is the train station?", "translation": "火车站在哪里？"},
            {"id": "travel-2", "text": "I need a ticket to the airport.", "translation": "我需要一张去机场的票。"},
            {"id": "travel-3", "text": "Could you help me, please?", "translation": "可以请你帮个忙吗？"},
            {"id": "travel-4", "text": "How long does it take?", "translation": "需要多长时间？"},
            {"id": "travel-5", "text": "Thank you for your help.", "translation": "谢谢你的帮助。"},
        ],
    ),
]
LESSONS_BY_ID = {lesson.id: lesson for lesson in LESSONS}
