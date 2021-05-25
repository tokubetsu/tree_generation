from staff_classes import Cell
import json


class MyEncoder(json.JSONEncoder):  # encoder для записи пользовательских типов данных
    def default(self, obj):
        if isinstance(obj, Cell):  # если ячейка, то превращаем в словарь
            return {'pos': obj.pos, 'feats': obj.feats}
        elif isinstance(self, tuple):  # если кортеж, то превращаем в словарь с пометкой, чтобы отличать от списков
            return {'is_tuple': True, 'tuple': list(obj)}
        else:  # для всего остального используем дефолтный encoder
            return json.JSONEncoder.default(self, obj)


def my_classes(dct):  # отлавливаем пользовательские типы данных при чтении
    if 'pos' in dct:  # если есть часть речи, то читаем как ячейку
        if dct['feats']:
            return Cell(dct['pos'], tuple(dct['feats']))
        else:
            return Cell(dct['pos'], dct['feats'])
    elif isinstance(dct, list):  # иначе это коржеж, читаем как кортеж
        return tuple(dct)


# записть статистик в файл в виде строк #уровень#значение/
def encode_file(data, lvl=0, simb='#', simb_sep='/', f_obj=None):
    def func_write(line):
        f_obj.write(line)

    for key in data:

        if (isinstance(key, tuple)) or (isinstance(key, Cell)):  # если кортеж или ячейка, то свой encoder
            new_key = simb + str(lvl) + simb + json.dumps(key, cls=MyEncoder) + simb_sep
        else:  # иначе просто пишем, как есть (для строк)
            new_key = simb + str(lvl) + simb + key + simb_sep
        func_write(new_key)  # пишем строку в файл

        if isinstance(data[key], dict):  # если на следующем уровне словарь, то решаем, идти ли глубже
            if len(data[key]) == 0:  # словарь пустой, значит просто пишем и все
                new_line = simb + str(lvl + 1) + simb + simb_sep
                func_write(new_line)
            else:  # словарь не пустой, значит, идем в глубь рекурсии
                new_data = data[key]
                encode_file(new_data, lvl + 1, f_obj=f_obj)

        else:  # если не словарь, то просто пишем новую строку в файл
            new_line = simb + str(lvl + 1) + simb + json.dumps(data[key], cls=MyEncoder) + simb_sep
            func_write(new_line)


# чтение записанного в предыдущей функции файла
def decode_file(data, dct=None, lst_key=None, simb_sep='/'):
    def add_to_dct(lst, d):  # добавляем элементы по цепочке ключей в слолварь
        if len(lst) > 2:  # если больше двух элементов, то добавляем ключ и идем по нему глубже
            if lst[0] not in d:
                d[lst[0]] = {}
            new_dct = d[lst[0]]
            d[lst[0]] = add_to_dct(lst[1:], new_dct)
        else:  # если всего два, то добавляем ключ и значение и выходим
            if lst[1] == '':
                lst[1] = {}
            d[lst[0]] = lst[1]
        return d

    if not dct:  # если это первый шаг, то создаем словарь и список
        dct = {}
    if not lst_key:
        lst_key = []

    data = data.split(simb_sep)[0:-1]  # делим данные на строки по разделителю

    prev_lvl = -1  # предыдущий уровень считаем отрицательным

    for key, line in enumerate(data):
        lvl = int(line[1])  # определяе  текущий уровень

        # если в строке есть скобки, то это словарь или список, ловим описанным классом
        if ('{' in line) or ('[' in line):
            item = json.loads(line[3:], object_hook=my_classes)
        elif line[3:].isdigit():  # если нет скобок, но строка из цифр, то сохраняем int
            item = int(line[3:])
        elif line[3:] == 'None':  # если None, то добавляем соответствующее значение
            item = None
        else:  # если ничего из перечисленного, то просто сохраняем (это строка)
            item = line[3:]
        if prev_lvl < lvl:  # если уровень увеличился, просто пишем новый ключ и идем дальше
            if isinstance(item, list):
                lst_key.append(tuple(item))
            else:
                lst_key.append(item)
        else:  # если уменьшился, то добавляем все в словарь
            dct = add_to_dct(lst_key, dct)
            lst_key = lst_key[0:lvl]
            if isinstance(item, list):
                lst_key.append(tuple(item))
            else:
                lst_key.append(item)
        prev_lvl = lvl  # переопределяем предыдущий уровень

        if key == len(data) - 1:  # если это конец, то добавляем все, что осталось в списке
            dct = add_to_dct(lst_key, dct)
    return dct
