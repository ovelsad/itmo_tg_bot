import os
import telebot
from telebot import types
import json
import re
from dotenv import load_dotenv

# Инициализация бота
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Create a .env file from .env.example.")
bot = telebot.TeleBot(TOKEN)

# Загрузка данных учебных планов
with open('ai_plan.json', 'r', encoding='utf-8') as f:
    ai_plan = json.load(f)

with open('ai_product_plan.json', 'r', encoding='utf-8') as f:
    ai_product_plan = json.load(f)

# Полный словарь ключевых слов
RELEVANT_KEYWORDS = {
    'program': [
        'ии', 'ai', 'искусственн', 'интеллект', 'продукт', 'product',
        'магистратур', 'обучен', 'образован', 'study', 'программ', 'program',
        'образовательн', 'обучение', 'учёб', 'учебн', 'образовани', 'education',
        'master', 'магистр', 'поступлен', 'поступить', 'подач', 'заявк',
        'специальност', 'направлен', 'curriculum', 'куррикулум', 'itmo',
        'итмо', 'универ', 'вуз', 'univers', 'faculty', 'факультет'
    ],
    'courses': [
        'курс', 'дисциплин', 'предмет', 'elective', 'выбор', 'лекци',
        'семинар', 'занят', 'class', 'module', 'модул', 'study plan',
        'учебн план', 'программ обучен', 'teaching', 'преподаван',
        'academic', 'академич', 'credit', 'кредит', 'ects', 'часы',
        'hours', 'аудиторн', 'load', 'нагрузк', 'syllabus', 'силлабус',
        'кафедр', 'department', 'chair', 'teacher', 'преподавател',
        'professor', 'лектор', 'instructor', 'тренер', 'учител'
    ],
    'structure': [
        'семестр', 'график', 'план', 'расписан', 'трудоемк', 'период',
        'семестров', 'полугодие', 'trimester', 'квартал', 'quarter',
        'год', 'year', 'учебн год', 'academic year', 'расписани',
        'schedule', 'календар', 'calendar', 'даты', 'dates', 'начало',
        'start', 'конец', 'end', 'продолжительн', 'duration', 'длительн',
        'срок', 'term', 'stage', 'этап', 'phase', 'часть', 'part',
        'блок', 'block', 'segment', 'модул', 'module', 'раздел', 'section'
    ],
    'practice': [
        'практик', 'стажировк', 'работ', 'project', 'internship',
        'лабораторн', 'lab', 'лаба', 'research', 'исследовани',
        'experiment', 'эксперимент', 'задани', 'task', 'assignment',
        'проект', 'project', 'кейс', 'case', 'решен', 'solution',
        'problem', 'проблем', 'задач', 'exercise', 'упражнен',
        'тренировк', 'training', 'workshop', 'воркшоп', 'семинар',
        'seminar', 'коллоквиум', 'colloquium', 'конференц', 'conference',
        'публикац', 'publication', 'article', 'стать', 'paper', 'работ',
        'thesis', 'диплом', 'диссертац', 'dissertation', 'qualification',
        'квалификац', 'аттестац', 'certification', 'сертификац'
    ],
    'recommend': [
        'посоветуй', 'рекоменд', 'выбрать', 'бэкграунд', 'опыт',
        'background', 'совет', 'advice', 'help', 'помощ', 'подскаж',
        'suggest', 'предлож', 'ориентир', 'ориентац', 'guidance',
        'руководств', 'инструкц', 'instruction', 'manual', 'гайд',
        'guide', 'tutorial', 'обучен', 'teach', 'study', 'изучен',
        'learn', 'как лучш', 'how to', 'что лучш', 'what is better',
        'compare', 'сравнен', 'difference', 'различ', 'отлич',
        'similar', 'похож', 'аналог', 'analog', 'альтернат', 'alternative',
        'выбор', 'choice', 'select', 'подбор', 'подходящ', 'suitable',
        'соответств', 'match', 'соответств', 'соответств', 'fit', 'подход',
        'approach', 'стратег', 'strategy', 'тактик', 'tactic', 'план',
        'plan', 'курс', 'path', 'путь', 'roadmap', 'дорожн карт'
    ],
    'assessment': [
        'экзамен', 'exam', 'зачет', 'test', 'тест', 'контрольн',
        'аттестац', 'assessment', 'оценк', 'grade', 'балл', 'score',
        'рейтинг', 'rating', 'систем оцен', 'grading', 'шкал',
        'scale', 'критери', 'criterion', 'requirement', 'требован',
        'услов', 'condition', 'норматив', 'standard', 'стандарт',
        'правил', 'rule', 'regulation', 'регламент', 'procedure',
        'процедур', 'порядок', 'order', 'process', 'процесс'
    ],
    'career': [
        'карьер', 'career', 'работ', 'job', 'трудоустройств', 'employment',
        'ваканс', 'vacancy', 'компани', 'company', 'организац', 'organization',
        'предприят', 'enterprise', 'business', 'бизнес', 'стартап', 'startup',
        'професс', 'profession', 'должност', 'position', 'занятост',
        'employment', 'заработн', 'salary', 'доход', 'income', 'перспектив',
        'perspective', 'возможност', 'opportunity', 'потенциал', 'potential',
        'развит', 'development', 'growth', 'рост', 'успех', 'success',
        'достижен', 'achievement', 'цель', 'goal', 'target', 'мишен',
        'objective', 'задач', 'task', 'план', 'plan', 'стратег', 'strategy'
    ],
    'admission': [
        'поступлен', 'admission', 'подач', 'application', 'заявк', 'request',
        'документ', 'document', 'требован', 'requirement', 'услов', 'condition',
        'срок', 'deadline', 'дата', 'date', 'времен', 'time', 'период', 'period',
        'правил', 'rule', 'regulation', 'процедур', 'procedure', 'процесс',
        'process', 'порядок', 'order', 'этап', 'stage', 'шаг', 'step',
        'подготовк', 'preparation', 'готов', 'ready', 'необходим', 'necessary',
        'обязательн', 'mandatory', 'рекомендац', 'recommendation', 'совет',
        'advice', 'инструкц', 'instruction', 'руководств', 'guide', 'manual',
        'гайд', 'tutorial', 'пример', 'example', 'образец', 'sample', 'шаблон',
        'template', 'форма', 'form', 'анкет', 'questionnaire', 'опрос', 'survey'
    ],
    'international': [
        'международн', 'international', 'иностран', 'foreign', 'зарубеж',
        'abroad', 'обмен', 'exchange', 'партнерств', 'partnership',
        'сотрудничеств', 'cooperation', 'collaboration', 'язык', 'language',
        'английск', 'english', 'немецк', 'german', 'французск', 'french',
        'китайск', 'chinese', 'перевод', 'translation', 'локализ', 'localization',
        'виза', 'visa', 'документ', 'document', 'страноведен', 'country studies',
        'культур', 'culture', 'традиц', 'tradition', 'обыча', 'custom',
        'менталитет', 'mentality', 'адаптац', 'adaptation', 'акклиматизац',
        'acclimatization', 'поддержк', 'support', 'помощ', 'help', 'assistance',
        'сервис', 'service', 'residence', 'проживан', 'living', 'быт', 'everyday life'
    ],
    'research': [
        'научн', 'research', 'исследован', 'study', 'анализ', 'analysis',
        'эксперимент', 'experiment', 'лаборатор', 'laboratory', 'lab',
        'метод', 'method', 'methodology', 'подход', 'approach', 'теори',
        'theory', 'гипотез', 'hypothesis', 'предположен', 'assumption',
        'доказательств', 'proof', 'evidence', 'результат', 'result',
        'вывод', 'conclusion', 'заключен', 'finding', 'открыт', 'discovery',
        'инновац', 'innovation', 'разработк', 'development', 'патент',
        'patent', 'публикац', 'publication', 'article', 'стать', 'paper',
        'доклад', 'report', 'презентац', 'presentation', 'конференц',
        'conference', 'симпозиум', 'symposium', 'семинар', 'seminar',
        'коллоквиум', 'colloquium', 'workshop', 'воркшоп', 'дискусси',
        'discussion', 'дебат', 'debate', 'полемик', 'controversy'
    ]
}

# База знаний для рекомендаций
RECOMMENDATIONS = {
    'programming': {
        'ai': ['Проектирование систем машинного обучения', 'Глубокое обучение', 'Вычисления на GPU'],
        'ai_product': ['Программирование на Python (продвинутый уровень)', 'Инженерия данных']
    },
    'math': {
        'ai': ['Математика для машинного обучения', 'Прикладная математика и статистика'],
        'ai_product': ['Математическая статистика', 'Прикладной анализ временных рядов']
    },
    'management': {
        'ai': ['Управление проектами в Data Science'],
        'ai_product': ['Стратегический продуктовый менеджмент', 'Управление продуктовым портфелем']
    },
    'data': {
        'ai': ['Обработка естественного языка', 'Компьютерное зрение'],
        'ai_product': ['Метрики и аналитика продукта', 'Бизнес-анализ']
    },
    'ai_interest': {
        'ai': ['Нейронные сети', 'Генеративные модели', 'Обработка естественного языка'],
        'ai_product': ['Прикладное использование ИИ', 'UX для AI-продуктов']
    }
}

# Состояния пользователей
user_states = {}


def get_elective_recommendations(background, program):
    """Получение рекомендаций по выборным курсам"""
    program_data = ai_plan if program == 'ai' else ai_product_plan
    recommendations = []

    for category in background:
        if category in RECOMMENDATIONS:
            recommendations.extend(RECOMMENDATIONS[category].get(program, []))

    if len(recommendations) < 3:
        top_electives = sorted(
            [course for sem in program_data['semesters'].values() for course in sem
             if course.get('is_elective')],
            key=lambda x: x['hours'],
            reverse=True
        )[:5]
        recommendations.extend([c['name'] for c in top_electives])

    return list(set(recommendations))[:5]


def detect_background(text):
    """Анализ бэкграунда пользователя"""
    background = []
    text_lower = text.lower()

    if any(word in text_lower for word in ['программир', 'код', 'sql', 'алгоритм']):
        background.append('programming')
    if any(word in text_lower for word in ['матем', 'стат', 'анализ', 'алгебр']):
        background.append('math')
    if any(word in text_lower for word in ['менедж', 'управл', 'руковод', 'лидер']):
        background.append('management')
    if any(word in text_lower for word in ['анализ данн', 'data', 'deep learning', 'ml']):
        background.append('data')
    if any(word in text_lower for word in ['нейросет', 'ai', 'ии', 'машинн обучен']):
        background.append('ai_interest')

    return background


def determine_best_program(background):
    """Автоматическое определение оптимальной программы"""
    tech_score = sum(1 for cat in ['programming', 'math', 'data'] if cat in background)
    management_score = sum(1 for cat in ['management'] if cat in background)
    ai_interest_score = sum(1 for cat in ['ai_interest'] if cat in background)

    if tech_score >= 2 and ai_interest_score >= 1:
        return 'ai', "Искусственный интеллект (техническая направленность)"
    elif management_score >= 1 and ai_interest_score >= 1:
        return 'ai_product', "Управление ИИ-продуктами (менеджерская направленность)"
    elif tech_score >= management_score:
        return 'ai', "Искусственный интеллект (техническая база)"
    else:
        return 'ai_product', "Управление ИИ-продуктами (управленческий потенциал)"


# Приветственное сообщение
PROGRAMS_DESCRIPTION = """
🎓 *Магистратуры ИТМО*:

1. *Искусственный интеллект*:
   - Глубокое изучение алгоритмов ML/DL
   - Акцент на технические навыки
   - Для будущих исследователей и инженеров AI

2. *Управление ИИ-продуктами*:
   - Продуктовый менеджмент в AI
   - Бизнес-аспекты искусственного интеллекта
   - Для будущих проджект-менеджеров в AI

*Опишите ваш опыт и интересы, и я подберу оптимальную программу и курсы!*
"""


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, PROGRAMS_DESCRIPTION, parse_mode='Markdown')
    msg = bot.send_message(
        message.chat.id,
        "📝 *Пожалуйста, кратко опишите:*\n"
        "- Ваш опыт (программирование, математика, менеджмент и т.д.)\n"
        "- Интересы в области ИИ\n"
        "- Карьерные цели (если есть)",
        parse_mode='Markdown'
    )
    user_states[message.chat.id] = {'state': 'waiting_background'}


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id]['state'] == 'waiting_background':
        background = detect_background(message.text)

        if not background:
            bot.send_message(
                chat_id,
                "🤔 Не могу определить ваш профиль. Попробуйте описать подробнее, например:\n"
                "'Имею опыт программирования на Python и интересуюсь нейросетями'\n"
                "'Работал менеджером и хочу изучить применение ИИ в бизнесе'"
            )
            return

        # Определяем оптимальную программу
        program, program_name = determine_best_program(background)
        recommendations = get_elective_recommendations(background, program)

        # Формируем персонализированный ответ
        response = (
                f"🎯 *На основе вашего опыта оптимальной программой будет {program_name}*\n\n"
                f"🔹 *Рекомендуемые курсы:*\n" +
                "\n".join(f"• {course}" for course in recommendations) +
                "\n\n💡 Совет: Обратите особое внимание на курсы по " +
                ("техническим аспектам ИИ" if program == 'ai' else "управлению AI-продуктами") +
                "\n\nХотите рассмотреть альтернативные варианты? Напишите /start"
        )

        bot.send_message(chat_id, response, parse_mode='Markdown')
        user_states.pop(chat_id, None)
        return

    # Обработка других сообщений
    if any(keyword in message.text.lower() for keyword in RELEVANT_KEYWORDS['recommend']):
        bot.send_message(chat_id, "Для получения рекомендаций нажмите /start")
    else:
        bot.send_message(
            chat_id,
            "Я помогаю с выбором магистратуры по ИИ в ИТМО. "
            "Нажмите /start для получения персонализированных рекомендаций."
        )


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)