#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для удаления дублей из списка источников и создания маппинга нумерации.
"""

import re
from typing import Dict, List, Tuple, Set


def normalize_text(text: str) -> str:
    """Нормализует текст для сравнения: убирает лишние пробелы, приводит к нижнему регистру."""
    # Убираем множественные пробелы
    text = re.sub(r'\s+', ' ', text)
    # Убираем пробелы в начале и конце
    text = text.strip()
    # Приводим к нижнему регистру
    text = text.lower()
    return text


def extract_key_info(source: str) -> Dict[str, str]:
    """Извлекает ключевую информацию из источника для сравнения."""
    normalized = normalize_text(source)
    
    # Извлекаем авторов (до первой запятой или точки, но учитываем формат "Автор, В. И.")
    authors_match = re.match(r'^([^,\.]+(?:\s*,\s*[^,\.]+)*)', normalized)
    authors = authors_match.group(1) if authors_match else ""
    
    # Извлекаем название (между авторами и годом/издательством)
    # Ищем год (4 цифры)
    year_match = re.search(r'\b(19|20)\d{2}\b', normalized)
    year_pos = year_match.start() if year_match else len(normalized)
    
    # Название обычно между авторами и годом
    title_part = normalized[:year_pos] if year_pos < len(normalized) else normalized
    
    # Извлекаем URL если есть (нормализуем - убираем параметры и якоря)
    url_match = re.search(r'https?://[^\s\)]+', normalized)
    url = ""
    if url_match:
        url = url_match.group(0).lower()
        # Убираем параметры запроса и якоря
        url = url.split('?')[0].split('#')[0].rstrip('/')
        # Убираем www. для нормализации
        url = url.replace('www.', '')
        # Извлекаем базовый путь (без последнего сегмента, если это число или дата)
        # Например: /articles/820159 -> /articles/
        url_parts = url.split('/')
        if len(url_parts) > 1:
            # Если последний сегмент похож на ID или дату, убираем его
            last_part = url_parts[-1]
            if re.match(r'^\d+$', last_part) or re.match(r'^\d{4}-\d{2}-\d{2}', last_part):
                url = '/'.join(url_parts[:-1])
    
    return {
        'authors': authors,
        'title_part': title_part,
        'url': url,
        'full_normalized': normalized
    }


def is_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли текст кириллицу."""
    return bool(re.search(r'[а-яё]', text, re.IGNORECASE))


def normalize_authors(authors: str) -> str:
    """Нормализует имена авторов для сравнения."""
    # Убираем лишние пробелы и приводим к нижнему регистру
    normalized = normalize_text(authors)
    # Убираем точки после инициалов
    normalized = re.sub(r'\.\s*', '', normalized)
    # Убираем запятые
    normalized = normalized.replace(',', ' ')
    # Убираем множественные пробелы
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def are_duplicates(source1: str, source2: str) -> bool:
    """Определяет, являются ли два источника дублями."""
    info1 = extract_key_info(source1)
    info2 = extract_key_info(source2)
    
    # 1. Сравниваем полный нормализованный текст (для точных дублей с разными пробелами/знаками)
    # Убираем различия в пробелах и пунктуации для более точного сравнения
    norm1_clean = re.sub(r'[^\w\s]', '', info1['full_normalized'])
    norm2_clean = re.sub(r'[^\w\s]', '', info2['full_normalized'])
    norm1_clean = re.sub(r'\s+', ' ', norm1_clean).strip()
    norm2_clean = re.sub(r'\s+', ' ', norm2_clean).strip()
    if norm1_clean == norm2_clean:
        return True
    
    # 2. Если есть URL, сравниваем по URL (самый надежный способ)
    if info1['url'] and info2['url']:
        if info1['url'] == info2['url']:
            return True
    
    # 3. Сравниваем авторов и ключевую часть названия
    authors1_norm = normalize_authors(info1['authors'])
    authors2_norm = normalize_authors(info2['authors'])
    
    # Если авторы совпадают точно
    authors_match = False
    if authors1_norm and authors2_norm:
        if authors1_norm == authors2_norm:
            authors_match = True
        # Для многоавторных работ проверяем пересечение основных авторов
        elif len(authors1_norm.split()) >= 2 and len(authors2_norm.split()) >= 2:
            # Берем первые два слова (фамилию и имя/инициал) каждого автора
            authors1_words = set(authors1_norm.split()[:4])  # Первые 4 слова
            authors2_words = set(authors2_norm.split()[:4])
            if authors1_words and authors2_words:
                common = authors1_words.intersection(authors2_words)
                # Если есть хотя бы 2 общих слова (фамилия + инициал)
                if len(common) >= 2:
                    authors_match = True
    
    if authors_match:
        # Сравниваем ключевую часть названия
        title1 = info1['title_part']
        title2 = info2['title_part']
        
        # Извлекаем ключевые слова из названия (слова длиной >= 4 символов, исключая стоп-слова)
        stop_words = {'для', 'при', 'про', 'the', 'for', 'and', 'with', 'from', 'that', 'this'}
        words1 = set(w for w in re.findall(r'\b\w{4,}\b', title1) if w not in stop_words)
        words2 = set(w for w in re.findall(r'\b\w{4,}\b', title2) if w not in stop_words)
        
        # Если есть пересечение ключевых слов
        if words1 and words2:
            common_words = words1.intersection(words2)
            # Для коротких названий достаточно 3 слов, для длинных - 4
            min_common = 3 if min(len(words1), len(words2)) < 8 else 4
            if len(common_words) >= min_common:
                return True
    
    # 4. Специальные случаи известных дублей (точные совпадения по ключевым словам)
    norm1 = info1['full_normalized']
    norm2 = info2['full_normalized']
    
    # BERT статьи Devlin (русский и английский варианты)
    if 'bert' in norm1 and 'bert' in norm2:
        if 'devlin' in norm1 and 'devlin' in norm2:
            # Проверяем, что это про одно и то же (pre-training или предобучение)
            if ('pre-training' in norm1 or 'предобучение' in norm1 or 'pre-training' in norm2 or 'предобучение' in norm2):
                # Также проверяем наличие arxiv или arXiv
                arxiv1 = re.search(r'arxiv[:\s]+(\d+\.\d+)', norm1)
                arxiv2 = re.search(r'arxiv[:\s]+(\d+\.\d+)', norm2)
                if arxiv1 and arxiv2:
                    if arxiv1.group(1) == arxiv2.group(1):
                        return True
                elif 'arxiv' in norm1 or 'arxiv' in norm2:
                    # Если есть arxiv упоминание, но без номера, все равно считаем дублем
                    return True
    
    # Salton, McGill - Introduction to Modern Information Retrieval (русский и английский)
    if 'salton' in norm1 and 'salton' in norm2:
        if 'mcgill' in norm1 and 'mcgill' in norm2:
            if 'introduction' in norm1 and 'introduction' in norm2:
                if ('information' in norm1 and 'information' in norm2) or ('информационный' in norm1 and 'информационный' in norm2):
                    if 'retrieval' in norm1 or 'поиск' in norm1:
                        return True
    
    # Manning Introduction to Information Retrieval (точный дубль)
    if 'manning' in norm1 and 'manning' in norm2:
        if 'introduction' in norm1 and 'information' in norm1 and 'retrieval' in norm1:
            if 'introduction' in norm2 and 'information' in norm2 and 'retrieval' in norm2:
                # Проверяем, что это одна и та же книга
                if 'cambridge' in norm1 and 'cambridge' in norm2:
                    return True
    
    # Mikolov Word2Vec статьи (только если это одна и та же статья)
    if 'mikolov' in norm1 and 'mikolov' in norm2:
        if 'representation' in norm1 and 'representation' in norm2:
            # Проверяем arxiv номер
            arxiv1 = re.search(r'arxiv[:\s]+(\d+\.\d+)', norm1)
            arxiv2 = re.search(r'arxiv[:\s]+(\d+\.\d+)', norm2)
            if arxiv1 and arxiv2 and arxiv1.group(1) == arxiv2.group(1):
                return True
    
    # Статьи с одинаковым URL (но разными датами обращения) - это точно дубли
    if info1['url'] and info2['url']:
        # Сравниваем базовый URL без параметров
        url1_base = info1['url'].split('/')[:-1]  # Убираем последний сегмент (может быть ID статьи)
        url2_base = info2['url'].split('/')[:-1]
        if len(url1_base) >= 3 and len(url2_base) >= 3:
            # Сравниваем домен и путь до последнего сегмента
            if '/'.join(url1_base[-3:]) == '/'.join(url2_base[-3:]):
                return True
    
    return False


def find_duplicates(sources: Dict[int, str]) -> Dict[int, List[int]]:
    """Находит группы дублей в списке источников."""
    duplicates_groups = {}
    processed = set()
    
    for i in range(1, len(sources) + 1):
        if i in processed:
            continue
        
        group = [i]
        for j in range(i + 1, len(sources) + 1):
            if j in processed:
                continue
            
            if are_duplicates(sources[i], sources[j]):
                group.append(j)
                processed.add(j)
        
        if len(group) > 1:
            duplicates_groups[i] = group
            processed.add(i)
    
    return duplicates_groups


def select_best_from_duplicates(sources: Dict[int, str], group: List[int]) -> int:
    """Выбирает лучший источник из группы дублей (предпочитает русский)."""
    # Сначала проверяем наличие русскоязычных версий
    russian_indices = []
    for idx in group:
        if is_cyrillic(sources[idx]):
            russian_indices.append(idx)
    
    if russian_indices:
        # Если есть русскоязычные, выбираем первый
        return russian_indices[0]
    else:
        # Иначе выбираем первый в группе
        return group[0]


def deduplicate_sources(sources: Dict[int, str]) -> Tuple[Dict[int, str], Dict[int, int]]:
    """Удаляет дубли из списка источников и создает маппинг старой нумерации на новую."""
    duplicates_groups = find_duplicates(sources)
    
    # Определяем, какие источники нужно удалить и какой лучший в каждой группе
    to_remove = set()
    best_in_group = {}  # old_index -> best_index в группе
    
    # Обрабатываем группы дублей
    for group in duplicates_groups.values():
        best_idx = select_best_from_duplicates(sources, group)
        # Помечаем остальные для удаления и запоминаем лучший
        for idx in group:
            if idx != best_idx:
                to_remove.add(idx)
            best_in_group[idx] = best_idx
    
    # Создаем новый список источников и маппинг
    new_sources = {}
    mapping = {}
    new_index = 1
    
    # Сначала создаем маппинг для всех элементов, которые остаются
    for old_index in range(1, len(sources) + 1):
        if old_index not in to_remove:
            new_sources[new_index] = sources[old_index]
            mapping[old_index] = new_index
            new_index += 1
    
    # Теперь маппим удаленные элементы на их лучшие версии
    for old_index in range(1, len(sources) + 1):
        if old_index in to_remove:
            # Находим лучший элемент в группе
            best_idx = best_in_group.get(old_index, old_index)
            # Маппим на новый индекс лучшего элемента
            if best_idx in mapping:
                mapping[old_index] = mapping[best_idx]
            else:
                # Если по какой-то причине лучший элемент не найден, маппим на 0
                mapping[old_index] = 0
    
    return new_sources, mapping


def main():
    # Исходный список источников
    sources_list = [
        "Байдыбеков А.А., Гильванов Р.Г., Молодкин И.А.,Современные фреймворки для разработки WEB-приложений, 2020. - с. 24.",
        "Дронов В.А. HTML5, CSS3 и Web 2.0. Разработка современных Web-сайтов. – М.: БХВ-Петербург, 2016. - 656 с. - с. 23.",
        "1.5.3. А.М. Дергачев, Ю.Д. Кореньков, И.П. Логинов,А.Г. Сафронов, Технологии Веб-сервисов,Министерство науки и высшего образования Российской Федерации Университет ИТМО, 2021, -100 с. -с. 22.",
        "Байдыбеков А.А., Гильванов Р.Г., Молодкин И.А., Современные фреймворки для разработки WEB-приложений, 2020. - с. 24",
        "Хекслет – Почему Django — лучший фреймворк для разработки сайтов [Электронный ресурс]– Режим доступа: https://ru.hexlet.io/blog/posts/pochemu-django-luchshiy-freymvork-dlya razrabotki-saytov, свободный (дата обращения: 01.04.2025).",
        "Ногербек Н.Д., Обзор MVC Веб-фреймворков. 2015.",
        "Удальцова Н.Л. Особенности проведения Customer Development в процессе коммерциализации минимального жизнеспособного продукта, 2024",
        "Дорохов, В. И. Инновационные бизнес-модели. Бизнес-модель стриминговых сервисов, 2019",
        "Катаев М. Как подружить бизнес и процессы [Электронный ресурс] // Хабр : сайт. — 2023. — URL: https://habr.com/ru/companies/tbank/articles/765382/ (дата обращения: 25.06.2025).",
        "Каплан, Р. С., Нортон, Д. П. Сбалансированная система показателей: превращение стратегии в действие. Бостон: Harvard Business School Press, 1996. 322 с.",
        "Беккер, Б. Э., Хьюзлид, М. А. Высокопроизводительные рабочие системы и эффективность фирмы: синтез исследований и управленческих приложений // Research in Personnel and Human Resources Management. 1998. Т. 16. С. 53–101.",
        "Девлин, Дж., Чанг, М. В., Ли, К., Тоутаанова, К. BERT: Предобучение глубоких двунаправленных трансформеров для понимания языка // arXiv preprint arXiv:1810.04805. 2019. 13 с.",
        "Миколов, Т., Чен, К., Коррадо, Г., Дин, Дж. Эффективная оценка представлений слов в векторном пространстве // arXiv preprint arXiv:1301.3781. 2013. 12 с.",
        "Салтон, Г., МакГилл, М. Дж. Введение в современный информационный поиск. Нью-Йорк: McGraw-Hill, 1983. 448 с.",
        "Федеральный закон № 152-ФЗ «О персональных данных».",
        "LinkedIn Profile Media Guidelines, 2023.",
        "Devlin J. et al. «BERT: Pre-training for NLP» [arXiv, 2019].",
        "Gartner «HR Analytics Trends», 2023.",
        "Harvard Business Review «ROI of Hiring», 2022.",
        "Getanalyst – Протокол HTTP и его связь с REST API [Электронный ресурс]– Режим доступа: https://getanalyst.ru/database/http-protocol?ysclid=m97g23uvqf649006248, свободный (дата обращения: 07.04.2025).",
        "Getanalyst – Архитектура систем для аналитиков: ТОП-5 нотаций моделирования архитектуры [Электронный ресурс]– Режим доступа: https://getanalyst.ru/database/system-analysts-architect-notations?ysclid=m97etps15k40606470, свободный (дата обращения: 07.04.2025).",
        "Исакова Т.А., Разработка web-сервиса для оказания бытовых услуг, Екатеринбург – 2017. - 66 с. - с.30.",
        "Карташев И.А., Создание веб-сервиса для организации совместных закупок, Томск – 2021 г. -82 с. - с.41.",
        "Bass, L., Weber, I., & Zhu, L.  DevOps: A Software Architect's Perspective, 2015",
        "Штефуряк, А. С. Грамотный выбор стратегии развертывания микросервисного программного продукта, 2020",
        "Маркелов А. А. Введение в технологии контейнеров и Kubernetes, 2019",
        "Микросервисная архитектура от А до Я, 2021",
        "Н.А. Меньшов.использование технологии контейнеризации как компонента обеспечения информационной безопасности. Статья 2022.",
        "Карнаухов К.В. Преимущества контейнеризации и сервисно-ориентированной архитектуры при разработке и развертывании веб-приложения // Экономика и социум. — 2018. — № 6 (49). — С. 1–6. — Режим доступа: https://sciup.org/preimushhestva-kontejnerizacii-i-servisno-orientirovannoj-arhitektury-pri-140239221 (дата обращения: 29.05.2025)",
        "Google Developers. Core Web Vitals // Google. — 2023. — [Электронный ресурс]. — URL: https://developers.google.com/speed/docs/insights/v5/about (дата обращения: 27.03.2025).",
        "PageSpeed Insights. Инструмент анализа производительности веб-страниц от Google. Доступен по адресу: https://pagespeed.web.dev/ . Дата обращения: 27.03.2025.",
        "Brown T., Davis K. AI in Recruitment: Transforming Talent Acquisition. — New York: Springer, 2019. — 180 p.",
        "Круг С. Веб-дизайн: книга Стива Круга. — Санкт-Петербург: Питер, 2021. — 240 с",
        "Троицкий, А. Что такое векторизация текста в NLP и какая она бывает: One-hot encoding, Bag of words, TF-IDF, Word2Vec, BERT и другие / А. Троицкий // Хабр. — 2024. — URL: https://habr.com/ru/articles/820159/ (дата обращения: 22.11.2025).",
        "Term Frequency-Inverse Document Frequency (TF-IDF): извлечение признаков из текстовых данных [Электронный ресурс] // OTUS. — URL: https://habr.com/ru/companies/otus/articles/755772/ (дата обращения: 22.11.2025).",
        "Троицкий, А. Что такое векторизация текста в NLP и какая она бывает: One-hot encoding, Bag of words, TF-IDF, Word2Vec, BERT и другие [Электронный ресурс] / А. Троицкий // Хабр. – 2024. – URL: https://habr.com/ru/articles/820159/ (дата обращения: 01.12.2025).",
        "TF-IDF: извлечение признаков из текстовых данных [Электронный ресурс] // Хабр. – 2023. – URL: https://habr.com/ru/companies/otus/articles/755772/ (дата обращения: 01.12.2025).",
        "Обзор методов векторизации текста: от Bag of Words до BERT [Электронный ресурс] // Хабр. – 2023. – URL: https://habr.com/ru/articles/778048/ (дата обращения: 01.12.2025).",
        "Как эмбеддинги улучшают рекомендательные системы: кейс Билайн ТВ [Электронный ресурс] // Хабр. – 2021. — URL: https://habr.com/ru/companies/rubda/articles/594759/ (дата обращения: 01.12.2025).",
        "Word2Vec: реализация модели на PyTorch [Электронный ресурс] // Хабр. — URL: https://habr.com/ru/articles/801807/ (дата обращения: 01.12.2025).",
        "Word2Vec: принцип работы и идея модели [Электронный ресурс] // Хабр. — URL: https://habr.com/ru/companies/otus/articles/574624/ (дата обращения: 01.12.2025).",
        "Доброхотов Д. BERT: что это такое и как использовать для NLP-задач [Электронный ресурс] // Хабр. – URL: https://habr.com/ru/companies/getmeit/articles/579518/  (дата обращения: 01.12.2025).",
        "Жарова М. BERT: архитектура, обучение и применение [Электронный ресурс] // Хабр. – URL: https://habr.com/ru/companies/skillfactory/articles/862130/  (дата обращения: 01.12.2025).",
        "Чижик, А. В. Сравнение моделей векторизации текстов для задачи анализа тональности коротких сообщений из социальных сетей / А. В. Чижик // Компьютерная лингвистика и вычислительные онтологии. — 2024. — Вып. 7. — С. 81–89. — DOI: 10.17586/2541-9781-2024-7-81–89.",
        "Искусственный интеллект в цифровой экономике: стратегические направления развития : аналитический доклад / Рос. акад. наук ; под общ. ред. А. К. Ковалёва [и др.]. — М., 2023. — 104 с. — URL: https://new.ras.ru/upload/iblock/969/wyh3c4g5hbdohtix9o23ljj5n36mahtn.pdf (дата обращения: 01.12.2025).",
        "Векторизация текста: от мешка слов до BERT [Электронный ресурс] // Хабр. — 2023. — URL: https://habr.com/ru/articles/778048/ (дата обращения: 01.12.2025).",
        "Коновалов, А. Как тюнингом TF-IDF побить BERT4Rec в ретро-тесте рекомендательной системы [Электронный ресурс] / А. Коновалов // Хабр. — 2024. — URL: https://habr.com/ru/companies/wildberries/articles/861466/ (дата обращения: 01.12.2025).",
        "Сжатие модели fastText для русского языка до 28 МБ [Электронный ресурс] // Хабр. — URL: https://habr.com/ru/articles/489474/ (дата обращения: 01.12.2025).",
        "Сжатие модели fastText для русского языка: квантизация и отбор признаков [Электронный ресурс] // Хабр. — URL: https://habr.com/ru/articles/582980/ (дата обращения: 01.12.2025).",
        "Manning C.D., Raghavan P., Schütze H. Introduction to Information Retrieval. Cambridge University Press, 2008.",
        "Jurafsky D., Martin J.H. Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition. Prentice Hall, 2009.",
        "Salton G., McGill M.J. Introduction to Modern Information Retrieval. McGraw-Hill, 1983.",
        "Mikolov T., Sutskever I., Chen K., Corrado G.S., Dean J. Distributed Representations of Words and Phrases and their Compositionality. Advances in Neural Information Processing Systems, 2013.",
        "Baeza-Yates R., Ribeiro-Neto B. Modern Information Retrieval: The Concepts and Technology behind Search. 2nd ed. Addison-Wesley, 2011.",
        "Devlin J., Chang M.-W., Lee K., Toutanova K. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. Proceedings of NAACL-HLT 2019, 2019.",
        "Manning C.D., Raghavan P., Schütze H. Introduction to Information Retrieval. Cambridge University Press, 2008.",
        "Zamani H., Croft W.B. Semantic Matching in Search. Foundations and Trends® in Information Retrieval, 2016.",
        "Сaatçı M., Kaya R., Ünlü R. Resume Screening with Natural Language Processing (NLP) // alphanumeric. 2024. Vol. 12, № 2. P. 121–140.",
        "Heakl A., Mohamed Y., Aly Elsharkawy N., Zaky A. ResuméAtlas: Revisiting Resume Classification with Large-Scale Datasets and Large Language Models // arXiv preprint arXiv:2406.18125. 2024.",
        "Zhao J. et al. Selecting the best rather than ranking correctly: A multi-expert ranking model for candidate selection // Expert Systems with Applications. 2025.",
        "Alderham A.H. et al. Comparative Semantic Resume Analysis for Improving Candidate-Job Matching // IEEE Access. 2022.",
        "Mikheev A. Russian Named Entity Recognition // Journal of Language Modelling. — 2021. — Vol. 9, № 2. — P. 155–180.",
        "Liu Y., Zhang Y., Chen X. Resume Parsing Based on Hybrid Rule and Deep Learning Approach // Proceedings of the International Conference on Intelligent Information Processing. — Springer, 2020. — P. 112–121.",
        "Sarawagi S. Information Extraction // Foundations and Trends in Databases. — 2008. — Vol. 1, № 3. — P. 261–377.",
        "Devlin J., Chang M.-W., Lee K., Toutanova K. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding // Proceedings of NAACL-HLT. — 2019. — P. 4171–4186.",
        "Newman D., Chemudugunta C., Fox P. A Structured Topic Model for Resume Parsing // ACM Transactions on Intelligent Systems and Technology. — 2011. — Vol. 2, № 4. — P. 1–25.",
    ]
    
    # Создаем словарь с нумерацией
    sources = {i + 1: source for i, source in enumerate(sources_list)}
    
    print("=" * 80)
    print("ОБРАБОТКА ИСТОЧНИКОВ: УДАЛЕНИЕ ДУБЛЕЙ")
    print("=" * 80)
    print(f"\nВсего источников: {len(sources)}\n")
    
    # Удаляем дубли
    new_sources, mapping = deduplicate_sources(sources)
    
    print("=" * 80)
    print("ОЧИЩЕННЫЙ СПИСОК ИСТОЧНИКОВ (БЕЗ ДУБЛЕЙ)")
    print("=" * 80)
    print()
    
    # Выводим очищенный список источников
    for new_idx, source in new_sources.items():
        print(f"{source}")
    
    print("\n" + "=" * 80)
    print("МАППИНГ СТАРОЙ НУМЕРАЦИИ НА НОВУЮ")
    print("=" * 80)
    print()
    print("Старый номер -> Новый номер")
    print("-" * 40)
    
    # Группируем маппинг для удобства чтения
    for old_idx in sorted(mapping.keys()):
        new_idx = mapping[old_idx]
        print(f"{old_idx:3d} -> {new_idx:3d}")
    
    print("\n" + "=" * 80)
    print(f"ИТОГО: {len(sources)} источников -> {len(new_sources)} источников")
    print(f"Удалено дублей: {len(sources) - len(new_sources)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

