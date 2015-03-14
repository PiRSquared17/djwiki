# Обзор среды разработки #

Краткий обзор среды разработки python/django

Python — мультипарадигменный язык программирования высокого уровня со строгой, динамической типизацией и автоматическим управлением памятью.

Наличие большого числа встроенных структур данных, таких как словари, списки и котрежи, лаконичные управляющие конструкции, использование утиной типизации и использование отступов для для группировки операторов делают программы на языке python очень лаконичными, что сильно упрощает их разработку и поддержку.

Django — это свободный фреймворк для создания веб-приложений, написанный на языке python. Он примерно соответствует архитектуре "Model-View-Controller". Django во многом похож на Ruby on Rails, предоставляет возможность быстро разрабатывать веб-приложения, абстрагируясь от конкретной СУБД и используя специальный язык шаблонов для определения дизайна страниц.

Архитектуру django часто называют Модель-Представление-Шаблон (MVT). При разработке приложения в django, разработчик отдельно определяет модель - как правило класс отображающий таблицу БД, шаблон страницы (соответствует представлению в MVC) на специальном языке шаблонов (представляющим собой html расширенный специальными тегами вида {% tag %}) и представление (соответствует контроллеру в MVC) - функцию отображающую модель в страницу.

Список некоторых возможностей django:

  * слой ORM
  * подключаемая архитектура приложений, которые можно устанавливать на любые Django-сайты
  * полноценный API доступа к БД с поддержкой транзакций.
  * встроенная система «generic views» — шаблонных функций контроллеров, которые избавляют от написания их вручную для некоторых частых задач
  * авторизация пользователей с возможностью подключения внешних модулей авторизации (например LDAP, OpenID)
  * расширяемая система шаблонов с тегами и наследованием
  * диспетчер URL на регулярных выражениях
  * система фильтров («middleware») для построения дополнительных обработчиков запросов, как например включенные в дистрибутив фильтры для кеширования, сжатия, нормализации URL и поддержки анонимных сессий
  * библиотека newforms для работы с формами (наследование, построение форм по существующей модели БД)
  * интернационализация и локализация приложений (i18n/l10n)
  * встроенный административный интерфейс с уже имеющимися переводами на многие языки
  * встроенная автоматическая документация по тегам шаблонов и моделям данных, доступная через административное приложение

В целом можно сказать, что фреймворк django позволяет достаточно быстро разрабатывать веб-приложения, используя такие принципы как DRY и KISS, django поддерживает философский принцип языка python "batteries included", предоставляя большое колличество готовых модулей (например систему комментариев), которые можно подключать к разрабатываемому проекту.