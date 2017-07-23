<HTML>
    <HEAD>
        <TITLE>README - ImpulseProblemV3</TITLE>
        <BASE target="_blank">
        <STYLE></STYLE>
    </HEAD>
    <BODY>
        <H1>ImpulseProblemV3</H1>
        Данная программа была создана для численных расчетов траекторий импульсных систем. 
        <H2>Установка и запуск</H2>
        <OL>
            <LI>Установите python3 и pip <br>
                <a href="https://www.python.org/downloads/">https://www.python.org/downloads/</a>
            </LI>
            <LI>Установите matplotlib и pyqt5 <br>
                <a href="https://matplotlib.org/users/installing.html">https://matplotlib.org/users/installing.html</a><br>
                <a href="http://pyqt.sourceforge.net/Docs/PyQt5/installation.html">http://pyqt.sourceforge.net/Docs/PyQt5/installation.html</a>
            </LI>
            <LI>
                Запустите ImpulseProblemV3.py используя python
            </LI>
        </OL>
        <H2>Инструкция</H2>
        <OL>
            <LI> <H4>Переменные</H4>
                t - текущее время <br>
                x1, ..., xn - координаты текущей точки <br>
                T - длина промежутка между импульсами, которому принадлежит t <br>
            </LI>
            <LI> <H4>Поддерживаемые константы и функции </H4>
                Данная программа поддерживает константы и функции модуля math: 
                <a href="https://docs.python.org/3/library/math.html">https://docs.python.org/3/library/math.html</a>
            </LI>
            <LI><H4>Поля для ввода</H4>
                Dim - целое число больше 0 <br>
                Дифф система, Импульсный оператор - математические выражения, поддерживающие переменные, константы и матем функции <br>
                Начальные точки - математические выражения, поддерживающие константы и матем функции <br>
                Промежутки между импульсами - математические выражения, поддерживающие константы и матем функции. Должны быть больше 0 <br>
            </LI>
            <LI><H4>Начало расчетов и вывод графиков</H4>
                Для ввода новой системы нажмите на кнопку "Dim" и введите новою размерность системы. После введите Дифф систему, Импульсный оператор
начальные точки и промежутки между импульсами. Для удаления точки или промежутка нажмите на "-" слева от удаляемой точки/промежутка. 
После нажмите "Посчитать", введите максимальное время и размер сетки по параметру t и нажмите "Ok".
Если расчет прошел успешно - появится таблица с результатами. После нажатия на кнопку "Plot" появится диалог настройки графика. 
Выберете необходимые для отображения переменные и нажмите "ok".
            </LI>
        </OL>
    </BODY>
</HTML>
