# ImpulseProblemV3
# Установка и запуск <br>
1. Установите python3 и pip https://www.python.org/downloads/ <br>
2. Установите matplotlib и pyqt5 <br>
https://matplotlib.org/users/installing.html <br>
http://pyqt.sourceforge.net/Docs/PyQt5/installation.html <br>

python -m pip install matplotlib pyqt5 <br>

3. Запустите ImpulseProblemV3.py используя python <br>

python ImpulseProblemV3.py <br>

# Инструкция
1. Общая информация  <br>
2. Переменные <br>
3. Поддерживаемые константы и функции <br>
4. Поля для ввода <br>
5. Начало расчетов и вывод графиков <br>


# 1. Общая информация
Данная программа была создана для численных расчетов траекторий импульсных систем. 
# 2. Переменные 
t - текущее время <br>
x1,...,xn - координаты текущей точки <br>
T - длина промежутка между импульсами, которому принадлежит t <br>
# 3. Поддерживаемые константы и функции
Данная программа поддерживает константы и функции модуля math: https://docs.python.org/3/library/math.html
# 4. Поля для ввода
Dim - целое число больше 0
Дифф система, Импульсный оператор - математические выражения, поддерживающие переменные, константы и матем функции
Начальные точки - математические выражения, поддерживающие константы и матем функции
Промежутки между импульсами - математические выражения, поддерживающие константы и матем функции. Должны быть больше 0
# 5. Начало расчетов и вывод графиков
Для ввода новой системы нажмите на кнопку "Dim" и введите новою размерность системы. После введите Дифф систему, Импульсный оператор
начальные точки и промежутки между импульсами. Для удаления точки или промежутка нажмите на "-" слева от удаляемой точки/промежутка. 
После нажмите "Посчитать", введите максимальное время и размер сетки по параметру t и нажмите "Ok".
Если расчет прошел успешно - появится таблица с результатами. После нажатия на кнопку "Plot" появится диалог настройки графика. 
Выберете необходимые для отображения переменные и нажмите "ok".
