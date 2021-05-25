from staff_func import Cell
from random import randint


data_dir = 'data/'  # глобальная переменная с директорией с изначальными данными


def count_sum(dct, mode='usual'):  # сумма частот для выбора элемента
    num = 0
    if mode == 'usual':  # для всех случаев, кроме получения уровня child
        for node in dct:
            if isinstance(node, tuple):
                if isinstance(dct[node], dict):
                    num += dct[node]['freq']
                else:
                    num += dct[node]
    else:  # уровень child
        for node in dct:
            num += node[0]
    return num


def find_sum(dct, num, mode='usual'):  # найти элемент, находящийся до определенной суммы
    num_new = 0
    if mode == 'usual':  # для всех случаев, кроме получения уровня child
        for node in dct:
            if isinstance(node, tuple):
                if isinstance(dct[node], dict):
                    num_new += dct[node]['freq']
                else:
                    num_new += dct[node]
                if num_new >= num:
                    return node
    else:  # уровень child
        for node in dct:
            num_new += node[0]
            if num_new >= num:
                return node[1::]


def get_random(dct, mode='usual'):  # случайный элемент исходя из вероятностей
    n = randint(0, count_sum(dct, mode))
    node = find_sum(dct, n, mode)
    return node


def get_from_mask(dct, mask):  # получает тройку по маске: элемент None обозначает то, что надо найти
    lst = []
    if not mask[0]:  # если ищем левый
        for node in dct:
            if node[1:3] == mask[1:3]:
                lst.append(node)
    elif not mask[2]:  # если ищем правый
        for node in dct:
            if node[0:2] == mask[0:2]:
                lst.append(node)
    return lst


def get_side(dct, item, lst, gen_mode, mode=''):  # получает одну сторону от последовательности связей на уровне
    if mode == 'left':
        lst = [item, ] + lst
    elif mode == 'right':
        lst.append(item)

    if gen_mode == 'left':  # идем влево
        if not item[0]:  # больше не можем, выходим
            return lst
        else:  # можем - идем дальше
            mask = (None, *item[0:2])
            mode = 'left'

    else:  # аналогично справа (или если мы только начали)
        if not item[2]:
            return lst
        else:
            mask = (*item[1:3], None)
            mode = 'right'

    new_item_lst = get_from_mask(dct, mask)  # получаем возможных следующих по маске
    new_dct = {node: dct[node] for node in new_item_lst}
    new_item = get_random(new_dct)  # выбираем случайного
    lst = get_side(dct, new_item, lst, gen_mode, mode)  # идем дальше

    return lst


def get_lvl(dct, item):  # получает уровень целиком
    lst = [item, ]
    lst = get_side(dct, item, lst, 'left')
    lst = get_side(dct, item, lst, 'right')
    return lst


def get_main_part(data, head, head_deprel, node):
    def _add_var(lst, child_el, items, max_len, dct_new):  # совсем вспомогательная функция, добавляет элементы в список
        new_lst = []
        for i, line in enumerate(lst):
            if (line[-1] == child_el) and (len(line) < max_len):
                new_lst.extend([[lst[i][0] + dct_new[item], *lst[i][1::], item] for item in items])
            else:
                new_lst.append(lst[i])
        return new_lst

    def _clean_var(lst, child_el, max_len):  # удаляет элементы из списка
        new_lst = []
        for line in lst:
            if (line[-1] != child_el) or (len(line) >= max_len):
                new_lst.append(line)
        return new_lst

    tree = None

    if node != (None, None, None):  # если у вершины вообще можно сгененировать потомков, то идем дальше

        node_deprel_pack = data[head][head_deprel][node]
        node_deprel = get_random(node_deprel_pack)
        node_deprel_lvl = get_lvl(node_deprel_pack, node_deprel)  # генерируем связи

        if node_deprel_lvl[0] != (None, None, None):  # если мы не решили на этом закончить, то генерируем потомков

            tree = [[deprel, ] for deprel in node_deprel_lvl]  # поддерево данного уровня

            # так как не обязательно цепочка потомков сложится, то считаем все возможные, потом выбираем из тех, что
            # остались
            child_lvl = [[data[head][head_deprel][node][node_deprel_lvl[0]][el], el, ] for el in
                         data[head][head_deprel][node][node_deprel_lvl[0]] if el != 'freq']  # варианты
            child_pack = [el for el in data[head][head_deprel][node][node_deprel_lvl[0]] if el != 'freq']  # итерация
            if len(node_deprel_lvl) > 1:
                for key, deprel in enumerate(node_deprel_lvl[1::]):
                    new_child_pack = []
                    for child in child_pack:
                        mask = (*child[1:3], None)
                        dct = data[head][head_deprel][node][deprel]
                        children_lst = get_from_mask(dct, mask)  # получаем возможных потомков по маске
                        new_dct = {it: dct[it] for it in children_lst}
                        new_child_pack.extend(children_lst)
                        if len(children_lst) == 0:  # если что-то нашли, то добавляем в варианты
                            child_lvl = _clean_var(child_lvl, child, key + 3)
                        else:  # иначе удаляем все, что кончается на того, для кого не нашли
                            child_lvl = _add_var(child_lvl, child, children_lst, key + 3, new_dct)
                    child_pack = new_child_pack
            child_lvl = get_random(child_lvl, 'child')

            if not child_lvl:  # если вообще ничего не нашли, но можно закончить, то заканчиваем
                if (None, None, None) in data[head][head_deprel][node]:
                    return [[(None, None, None), (None, None, None)]]
                else:  # иначе возвращаем код ошибки
                    return 1

            for key, child in enumerate(child_lvl):  # для каждого из элементов ищем потомков
                dep_part = get_main_part(data, node, tree[key][0], child)
                if dep_part == 1:
                    return 1
                tree[key].append([child, ])
                if dep_part:
                    tree[key][1].extend(dep_part)
    return tree


def get_clean(tree):  # превращает список троек в простой список вершин
    if isinstance(tree[0][1], Cell):
        new_tree = [tree[0][1].to_str(), ]
    elif not tree[0][1]:
        return None
    else:
        new_tree = [tree[0][1], ]
    for line in tree[1:]:
        ss = get_clean(line)
        if ss:
            new_tree.append(ss)
    return new_tree


def get_clean_check(tree):  # превращает список в троек в список ячеек
    if isinstance(tree[0][1], Cell):
        new_tree = [tree[0][1], ]
    elif not tree[0][1]:
        return None
    else:
        new_tree = [tree[0][1], ]
    for line in tree[1:]:
        ss = get_clean_check(line)
        if ss:
            new_tree.append(ss)
    return new_tree


def print_tree_json(tree, strings=None, lvl=0):  # пишет дерево вертикально с отступами
    if not strings:
        strings = []
    dif = lvl * 10
    s = dif * ' ' + tree[0]
    strings.append(s)
    if len(tree) > 1:
        strings[-1] += ':'
        for node in tree[1::]:
            strings = print_tree_json(node, strings, lvl + 1)
    return strings


def print_tree(tree):  # основная функция для вывода дерева
    strings = print_tree_json(tree)
    for line in strings:
        print(line)


def get_tree(data):  # генерирует дерево
    tree_lst = None
    while not tree_lst:
        root = (None, Cell(), None)  # создаем корневую вершину
        root_deprel = (None, 'root', None)  # создаем связь с корневой вершиной
        node_pack = data[root][root_deprel]  # получаем набор возможных следующих вершин
        node = get_random(node_pack)  # получаем из возможных случайную
        tree_lst = [root, [root_deprel, [node, ]]]  # создаем заготовку под дерево
        main_part = get_main_part(data, root, root_deprel, node)  # получаем основную часть
        if main_part == 1:  # если не получилось с основной частью, то пытаемся еще раз
            tree_lst = None
        elif main_part:  # если получилось, то оставляем
            tree_lst[1][1].extend(main_part)
    tree_check = get_clean_check(tree_lst)  # получем очищенное дерево для проверки
    tree = get_clean(tree_lst)  # получаем очищенное дерево для вывода
    return tree, tree_check


def neigh_check(tree, neigh, normal=True):  # проверка на критерий соседей
    if normal:  # если есть смысл проверять

        if isinstance(tree[0], Cell):
            sub_tree_neigh = [i[0] for i in tree[1:]]
            len_nodes = len(sub_tree_neigh)
            for start in range(len_nodes - 2):  # перебираем всех сосоедей по три
                for point in range(start + 1, len_nodes - 1):
                    for move in range(point + 1, len_nodes):
                        lst_three = tuple([sub_tree_neigh[start], sub_tree_neigh[point], sub_tree_neigh[move]])
                        if lst_three not in neigh[tree[0]]:  # проверяем возможно ли так
                            return False

        for el in tree[1:]:  # если можно пойти глубже, то идем
            new_tree = el[1]
            normal = neigh_check(new_tree, neigh, normal)

    return normal


def l_check(tree, l, normal=True):  # проверка на критерий "племянников"
    if normal:  #
        head = tree[0]
        for key, i in enumerate(tree[1:]):  # перебираем всех потомков родительской вершины
            dep_head = i[0]  # связь с родительской вершиной
            node = i[1][0]  # текущая вершина
            neighs = [(j[0], j[1][0]) for j in tree[2:key + 1] + tree[key + 2:]]  # все сестринские вершины для текущей
            for el in i[1][1:]:  # перебираем всех потомков
                dep_node = el[0]  # связь с потомком
                child = el[1][0]  # потомок
                for n in neighs:  # перебираем всех соседей
                    if n not in l[(head, dep_head, node)][(dep_node, child)]:  # если не совпадает с данными, то выходим
                        return False

        for el in tree[1:]:  # если можно пойти глубже, то идем
            new_tree = el[1]
            normal = l_check(new_tree, l, normal)

    return normal


def both_check(tree, neigh, l, normal=True):  # проверка на оба критерия
    if normal:

        if isinstance(tree[0], Cell):
            sub_tree_neigh = [i[0] for i in tree[1:]]
            len_nodes = len(sub_tree_neigh)
            for start in range(len_nodes - 2):
                for point in range(start + 1, len_nodes - 1):
                    for move in range(point + 1, len_nodes):
                        lst_three = tuple([sub_tree_neigh[start], sub_tree_neigh[point], sub_tree_neigh[move]])
                        if lst_three not in neigh[tree[0]]:
                            return False

            head = tree[0]
            for key, i in enumerate(tree[1:]):
                dep_head = i[0]
                node = i[1][0]
                neighs = [(j[0], j[1][0]) for j in tree[2:key + 1] + tree[key + 2:]]
                for el in i[1][1:]:
                    dep_node = el[0]
                    child = el[1][0]
                    for n in neighs:
                        if n not in l[(head, dep_head, node)][(dep_node, child)]:
                            return False

        for el in tree[1:]:
            new_tree = el[1]
            normal = both_check(new_tree, neigh, l, normal)

    return normal


def check_tree(tree, neigh=None, l=None, mode='both'):  # выбор варианта проверки
    res = None
    if mode == 'both':
        res = both_check(tree, neigh, l)
    elif mode == 'l':
        res = l_check(tree, l)
    elif mode == 'neigh':
        res = neigh_check(tree, neigh)
    elif mode == 'no':
        res = True
    return res


def create_tree(freq, neigh, l, root=True, normal=False, mode='both'):  # создание дерева
    def check(tr):  # проверка, не состоит ли дерево из одного корня
        if len(tr[1][1]) < 2:
            return True
        else:
            return False

    norm = False  # определяем все нужные переменные
    only_root = True
    tree = []
    tree_check = []
    i = 0
    while (not norm) or (only_root and not root):  # пока не выполнены требования к дереву, генерируем
        i += 1
        tree, tree_check = get_tree(freq)
        norm = check_tree(tree_check, neigh, l, mode=mode)
        only_root = check(tree)
    if not normal:  # выбор того, что надо вернуть
        return tree, i
    else:
        return tree_check
