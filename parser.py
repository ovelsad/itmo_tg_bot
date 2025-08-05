import pdfplumber
import re
import json
from collections import defaultdict


def parse_pdf(file_path):
    """Улучшенный парсинг PDF с учетом конкретной структуры файлов"""
    data = defaultdict(list)
    current_semester = None

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Улучшенное извлечение табличных данных
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if len(row) >= 4 and row[0] and row[1] and row[2] and row[3]:
                            sem, name, credits, hours = row[0], row[1], row[2], row[3]

                            # Очистка данных
                            sem = re.sub(r'\D', '', sem) or None
                            name = name.strip()
                            credits = re.sub(r'\D', '', credits) or '0'
                            hours = re.sub(r'\D', '', hours) or '0'

                            if sem and name:
                                current_semester = sem
                                is_elective = 'выбор' in name.lower() or 'электив' in name.lower()

                                data[current_semester].append({
                                    'name': name,
                                    'credits': int(credits),
                                    'hours': int(hours),
                                    'is_elective': is_elective
                                })
            else:
                # Альтернативный парсинг для текста без таблиц
                for line in text.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Поиск строк вида "1|Название|3|108|"
                    match = re.search(r'^(\d+)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|', line)
                    if match:
                        sem, name, credits, hours = match.groups()
                        current_semester = sem
                        data[current_semester].append({
                            'name': name.strip(),
                            'credits': int(credits),
                            'hours': int(hours),
                            'is_elective': 'выбор' in name.lower()
                        })

    return dict(data)


def save_to_json(data, filename):
    """Сохранение данных в JSON с проверкой"""
    result = {
        "semesters": data,
        "stats": {
            "total_semesters": len(data),
            "total_courses": sum(len(courses) for courses in data.values())
        }
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


# Парсинг с диагностикой
print("Парсинг ai.pdf...")
ai_data = parse_pdf('ai.pdf')
print(f"Найдено: {sum(len(v) for v in ai_data.values())} курсов")

print("\nПарсинг ai_product.pdf...")
ai_product_data = parse_pdf('ai_product.pdf')
print(f"Найдено: {sum(len(v) for v in ai_product_data.values())} курсов")

# Сохранение
save_to_json(ai_data, 'ai_plan.json')
save_to_json(ai_product_data, 'ai_product_plan.json')

print("\nРезультат сохранен в:")
print("- ai_plan.json")
print("- ai_product_plan.json")