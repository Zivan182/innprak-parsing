# innprak-parsing

Build Requirements:

<img width="375" alt="image" src="https://github.com/Zivan182/innprak-parsing/assets/71238076/015ac969-b004-4317-8783-9b947970b2ad">

\
Установка необходимых библиотек python: pip install -r requirements.txt

\
Тестирование реализовано с помощью библиотек pytest и unittest. Всего 10 тестов.

Команда для запуска тестов: pytest test_unit.py test_integration.py test_system.py

\
Добавлено тестирование с помощью serverspec, проверяется установка chrome, python и необходимых python библиотек. Тесты реализованы в файле serverspec/spec/localhost/script_spec.rb

Результат serverspec тестирования:

![image](https://github.com/Zivan182/innprak-parsing/assets/71238076/652b2401-37a9-46b1-a847-025d54c02ee9)


