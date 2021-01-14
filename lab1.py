import argparse
import pathlib
import math
import array

parser = argparse.ArgumentParser(description='Option 5. Search for a text fragment in a file.')
parser.add_argument('input', type=pathlib.Path, default="input.txt", nargs='?', help='path file input')
parser.add_argument('str', type=str, help='search string')
parser.add_argument('output', type=pathlib.Path, default=None, nargs='?', help='path file output')
parser.add_argument('-distance', type=int, dest="distance", nargs="?", help='distance Livenshtein')
parser.add_argument('-case', dest="case", action='store_true', help='lead to a common case')
parser.add_argument('-natural', dest="natural", action='store_true', help='natural search')
parser.add_argument('-lines', dest="lines", action='store_true', help='line-by-line search')
parser.add_argument('-fulltext', dest="fulltext", action='store_true', help='fulltext search')
parser.add_argument('-limit', dest="limit", type=int, help='limit of occurrences')

args = parser.parse_args()
print(args)

# Список символов видимых для человека одинаково
listOfSimilarSymbols = [[item for item in open("similarSymbols.txt", "r", encoding="UTF8").read().split('\n')[0]],
                        [item for item in open("similarSymbols.txt", "r", encoding="UTF8").read().split('\n')[1]]]


# Вычисление дистанции Ливенштейна
def distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


# Привод к "натуральному" виду
def naturalView(line, string, reverse=False):
    if reverse is False:
        one = listOfSimilarSymbols[0]
        two = listOfSimilarSymbols[1]
    else:
        one = listOfSimilarSymbols[1]
        two = listOfSimilarSymbols[0]
    """
    Вместо использования различных сочетаний символов (при таком наборе кол-во возможных перестановок 5*е^19) 
    проверяем наличие определенных символов в искомом слове и
    меняем так же выглядящие символы на эти
    Например, были в искомом слове англ в тексте рус то в тексте после станут англ
    """
    for item in string:
        for i in two:
            if item == i:
                line = [i if j == one[two.index(i)] else j for j in line]
        for i in one:
            if item == i:
                line = [i if j == two[one.index(i)] else j for j in line]
    """Склеиваем строку"""
    return "".join(line)
    pass


# Поиск вхождений в строке
def findInLine(line, string):
    if args.distance is None:
        for i in range(len(line)):
            """При обычном поиске достаточно сначала проверить совпадение по длине"""
            if i + len(string) > len(line):
                break
            """Проверяем эквивалентность строк"""
            if (line[i:i + len(string)] if args.lines is False else line) == string:
                return i
            """Если поиск построчный и при первом проходе ничего не найдено то выходим из цикла"""
            if args.lines is not False:
                break
    else:
        """
        Если задано расстояние Ливенштейна, то необходимо пройти стороку полностью
        Поиск получается очень жадный, так как это нечеткий поиск при использовании строк фиксированной длины,
        можно пропустить вхождения
        Главное, не задавать большое расстояние, иначе весь текст будет разбит на нечеткие вхождения с шагом в 1 символ
        """
        for i in range(len(line)):
            for j in range(len(line)):
                """Проверяем соответсвие расстояния Ливенштейна с заданым"""
                if distance((line[i:j] if args.lines is False else line), string) > args.distance:
                    """Если построчный поиск, то при первой неудавшейся проверке нет смысла дальше искать """
                    if args.lines is False:
                        continue
                    else:
                        break
                return i
    return -1
    pass


# Поиск строки в тексте
def findInText(text, string):
    text = text.split('\n')  # разбиваем на строки
    result = ""
    numberLine = 0
    count = 0
    if args.case is True:
        # приводим к общему регистру
        text = [item.lower() for item in text]
        string = string.lower()
    for line in text:
        if args.natural is not False:
            """Приводим строку к "натуральному" виду"""
            line = naturalView(line, string, reverse=False)
        pos = 0
        while True:
            if args.limit is not None:
                """Проверяем лимит"""
                if count >= args.limit:
                    break
            """Находим вхождение в строке"""
            newPos = findInLine(line[pos:], string)
            if newPos == -1:
                """Если не твхождения выходим из цикла"""
                break
            pos += newPos
            """Сохраняем результат поиска"""
            result += str(numberLine) + ("-" + str(pos) if args.fulltext else "") + '\n'
            pos += 1
            count += 1

        numberLine += 1
    return result
    pass


if __name__ == '__main__':
    """Открытие файлов и """
    inp = open(args.input, "r", encoding="UTF8")
    if args.output is not None:
        out = open(args.output, "w", encoding="UTF8")
    searchStr = args.str
    """Ищем вхождения в тексте"""
    res = findInText(inp.read(), searchStr)
    if args.output is not None:
        out.write(res)
        out.close()
    else:
        print(res)
    inp.close()

    pass
