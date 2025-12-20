#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для удаления указанных источников и создания нового маппинга нумерации.
Использует результаты первого скрипта deduplicate_sources.py
"""

from deduplicate_sources import deduplicate_sources, main as get_deduplicated_sources
import sys
import re


def get_sources_list():
    """Получает список источников из первого скрипта."""
    # Исходный список источников (из первого скрипта)
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
    return sources_list


def remove_sources_and_create_new_mapping():
    """Удаляет указанные источники и создает новый маппинг."""
    # Исходные номера источников для удаления
    old_indices_to_remove = {8, 9, 11, 12, 13, 14, 15, 16, 30, 32, 33, 34, 35, 36, 37, 38, 40, 43, 44, 45, 48, 49, 66}
    
    # Получаем список источников
    sources_list = get_sources_list()
    sources = {i + 1: source for i, source in enumerate(sources_list)}
    
    # Получаем результаты первого скрипта (удаление дублей)
    new_sources, first_mapping = deduplicate_sources(sources)
    
    # Определяем, какие новые номера соответствуют старым номерам, которые нужно удалить
    new_indices_to_remove = set()
    old_to_new_mapping = {}  # Для информации: старый номер -> новый номер (после первого скрипта)
    
    for old_idx in old_indices_to_remove:
        if old_idx in first_mapping:
            new_idx = first_mapping[old_idx]
            new_indices_to_remove.add(new_idx)
            old_to_new_mapping[old_idx] = new_idx
    
    print("=" * 80)
    print("УДАЛЕНИЕ УКАЗАННЫХ ИСТОЧНИКОВ И СОЗДАНИЕ НОВОГО МАППИНГА")
    print("=" * 80)
    print(f"\nПромежуточных источников (после удаления дублей): {len(new_sources)}")
    print(f"Источников для удаления: {len(new_indices_to_remove)}")
    
    # Удаляем указанные источники
    final_sources = {}
    second_mapping = {}  # Новый маппинг: старый номер (из первого скрипта) -> новый номер (после удаления)
    new_index = 1
    
    for old_new_idx in sorted(new_sources.keys()):
        if old_new_idx not in new_indices_to_remove:
            final_sources[new_index] = new_sources[old_new_idx]
            second_mapping[old_new_idx] = new_index
            new_index += 1
    
    # Создаем финальный маппинг: исходный номер -> финальный номер
    final_mapping = {}
    for original_idx in range(1, len(sources) + 1):
        if original_idx in first_mapping:
            intermediate_idx = first_mapping[original_idx]
            if intermediate_idx in second_mapping:
                final_mapping[original_idx] = second_mapping[intermediate_idx]
            else:
                # Этот источник был удален
                final_mapping[original_idx] = None
    
    print("\n" + "=" * 80)
    print("ФИНАЛЬНЫЙ СПИСОК ИСТОЧНИКОВ (ПОСЛЕ УДАЛЕНИЯ)")
    print("=" * 80)
    print()
    
    # Выводим финальный список источников
    for final_idx, source in final_sources.items():
        print(f"{source}")
    
    print("\n" + "=" * 80)
    print("МАППИНГ: ПРОМЕЖУТОЧНЫЙ НОМЕР -> ФИНАЛЬНЫЙ НОМЕР")
    print("=" * 80)
    print()
    print("Промежуточный номер -> Финальный номер")
    print("-" * 50)
    
    # Выводим маппинг: промежуточный номер (после первого скрипта) -> финальный номер
    for intermediate_idx in sorted(new_sources.keys()):
        if intermediate_idx in second_mapping:
            final_idx = second_mapping[intermediate_idx]
            print(f"{intermediate_idx:3d} -> {final_idx:3d}")
        else:
            print(f"{intermediate_idx:3d} -> УДАЛЕН")
    
    print("\n" + "=" * 80)
    print("СТАТИСТИКА")
    print("=" * 80)
    print(f"Исходное количество источников: {len(sources)}")
    print(f"После удаления дублей: {len(new_sources)}")
    print(f"После удаления указанных источников: {len(final_sources)}")
    print(f"Удалено всего: {len(sources) - len(final_sources)}")
    print("=" * 80)
    
    return final_sources, final_mapping


if __name__ == "__main__":
    remove_sources_and_create_new_mapping()

