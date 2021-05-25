from networkx import DiGraph
from staff_func import make_cell, NumItem, Cell, file_read, parse_conllu, save_data


data_dir = 'data/'  # глобальная переменная с директорией с изначальными данными


def get_tree(sent):  # создаем дерево зависимостей для предложения
    tree = DiGraph()

    for item in sent:
        if item['head'] != None:
            if item['head'] - 1 != -1:  # если это не корень, то ищем head, если корень, то присваиваем Cell()
                head_item = sent[item['head'] - 1]
                head = make_cell(head_item)  # создаем ячейку с родителем
            else:
                head = NumItem(Cell(), 0)
            connect = item['deprel']  # получем тип зависимости
            word = make_cell(item)  # создаем ячейку с текущей вершиной
            tree.add_edge(head, word, deprel=connect)  # добавляем в дерево

    return tree


def iter_tree(tree, prev_node=None, prev_node_el=None, prev_deprel=None, cur_node=None, cur_node_el=None,
              freq_dict=None, neighbors=None, neigh_dct=None, l_dct=None, dist_dict=None):
    if not freq_dict:  # если словаря нет, то создать
        freq_dict = {}
    if not neigh_dct:  # если множества соседей нет, то создать
        neigh_dct = {}
    if not l_dct:  # если множества племянников нет, то создать
        l_dct = {}
    if not neighbors:  # если множества соседей на предыдущем уровне нет, то пустое множество
        neighbors = []
    if not dist_dict:  # если множества взаимных расположений нет, то создать
        dist_dict = {}

    if not prev_node:  # если это первый элемент в дереве, то создать корень, связь с ним и вершину
        root = NumItem(Cell(), 0)   # создаем пустую вершину-кореньс номером
        prev_node_el = root  # сохраняем элемент, чтобы потом искать в дереве
        prev_node = (None, root.word, None)  # создаем тройку с корнем без номера для сохранения в статистику
        cur_node_el = list(tree[root].keys())[0]  # создаем элемент с номером - текущую вершину
        cur_node = (None, cur_node_el.word, None)  # создаем тройку текущей вершины без номера
        deprel_str = tree.get_edge_data(root, cur_node_el, 'deprel')['deprel']
        prev_deprel = (None, deprel_str, None)  # создаем тройку связей для текущей вершины и корня

    if prev_node not in freq_dict:  # если что-то еще не лежит на месте, то положить
        freq_dict[prev_node] = {}
    if prev_deprel not in freq_dict[prev_node]:
        freq_dict[prev_node][prev_deprel] = {}
    if cur_node not in freq_dict[prev_node][prev_deprel]:
        freq_dict[prev_node][prev_deprel][cur_node] = {'freq': 0, }

    dist = cur_node_el.ident - prev_node_el.ident  # ищем расстояние между текущей вершиной и предыдущей
    if prev_deprel[1] not in dist_dict:  # если что-то не лежит в словаре, то положить
        dist_dict[prev_deprel[1]] = {}
    if dist not in dist_dict[prev_deprel[1]]:
        dist_dict[prev_deprel[1]][dist] = 0
    dist_dict[prev_deprel[1]][dist] += 1  # увеличиваем частоту полученного расстояния

    # собрать всех потомков, кроме пунктуации
    lst_new = [node for node in tree[cur_node_el] if node.word.pos != 'PUNCT']
    lst_nodes = [None, ]  # первый элемент None для удобства работы
    if len(lst_new) == 0:  # если ничего нет, то добавляем None
        lst_nodes.append(None)
    else:
        lst_nodes.extend(sorted(lst_new, key=lambda items: items.ident))
    lst_nodes.append(None)
    len_nodes = len(lst_nodes)

    # перебираем все неповторяющиеся комбинации по три
    for start in range(len_nodes - 2):
        for point in range(start + 1, len_nodes - 1):
            for move in range(point + 1, len_nodes):

                # сохраняем связи соседей по три, но без None
                lst_three = [lst_nodes[start], lst_nodes[point], lst_nodes[move]]
                tpl = [i for i in lst_three if i]
                tpl_three = tuple([tree.get_edge_data(cur_node_el, i, 'deprel')['deprel'] for i in tpl])
                if cur_node[1] not in neigh_dct:
                    neigh_dct[cur_node[1]] = {}
                if tpl_three not in neigh_dct[cur_node[1]]:
                    neigh_dct[cur_node[1]][tpl_three] = 0
                neigh_dct[cur_node[1]][tpl_three] += 1

                # перебираем все последовательные тройки
                if (point == start + 1) and (move == point + 1):

                    # формируем одновременно и уровень связей и уровень потомков
                    child_num = tuple(lst_nodes[start:start + 3])
                    cur_node_el_new = child_num[1]
                    data = []
                    child = []
                    for item in child_num:
                        if not item:
                            data.append(None)
                            child.append(None)
                        else:
                            data.append(tree.get_edge_data(cur_node_el, item, 'deprel')['deprel'])
                            child.append(item.word)
                    deprel = tuple(data)
                    child = tuple(child)

                    # перебираем комбинации head-node+node_neigh-child
                    tpl_l1 = tuple([prev_node[1], prev_deprel[1], cur_node[1]])
                    if tpl_l1 not in l_dct:
                        l_dct[tpl_l1] = {}
                    tpl_l2 = tuple([deprel[1], child[1]])
                    if tpl_l2 not in l_dct:
                        l_dct[tpl_l1][tpl_l2] = {}
                    for elem in neighbors:
                        if elem not in l_dct[tpl_l1][tpl_l2]:
                            l_dct[tpl_l1][tpl_l2][elem] = 0
                        l_dct[tpl_l1][tpl_l2][elem] += 1

                    # создаем новый список соседей
                    data_l = lst_nodes[1:start + 1] + lst_nodes[start + 2:len(lst_nodes) - 1]
                    neighbors_new = []
                    for elem in data_l:
                        data_new = tree.get_edge_data(cur_node_el, elem, 'deprel')['deprel']
                        neighbors_new.append(tuple([data_new, elem.word]))

                    # кладем на место все, что там еще не лежит
                    if deprel not in freq_dict[prev_node][prev_deprel][cur_node]:
                        freq_dict[prev_node][prev_deprel][cur_node][deprel] = {'freq': 0, }
                    if child not in freq_dict[prev_node][prev_deprel][cur_node][deprel]:
                        freq_dict[prev_node][prev_deprel][cur_node][deprel][child] = 0

                    # увеличиваем частоты срозу для всего
                    freq_dict[prev_node][prev_deprel][cur_node][deprel][child] += 1
                    freq_dict[prev_node][prev_deprel][cur_node][deprel]['freq'] += 1
                    freq_dict[prev_node][prev_deprel][cur_node]['freq'] += 1

                    # если есть, куда идти, то идем глубже по дереву
                    if child[1]:
                        freq_dict, neigh_dct, l_dct, dist_dict = iter_tree(tree=tree, prev_node=cur_node,
                                                                           prev_node_el=cur_node_el, prev_deprel=deprel,
                                                                           cur_node=child, cur_node_el=cur_node_el_new,
                                                                           freq_dict=freq_dict, neighbors=neighbors_new,
                                                                           neigh_dct=neigh_dct, l_dct=l_dct,
                                                                           dist_dict=dist_dict)

    return freq_dict, neigh_dct, l_dct, dist_dict


def make_freq(data):  # создает частотный словарь
    freq_dict = {}
    neigh_dct = {}
    l_dct = {}
    dist_dct = {}
    for key, sent in enumerate(data):
        tree = get_tree(sent)
        freq_dict, neigh_dct, l_dct, dist_dct = iter_tree(tree, freq_dict=freq_dict, neigh_dct=neigh_dct, l_dct=l_dct,
                                                          dist_dict=dist_dct)
        if key % 1000 == 0:
            print(f'done {key + 1} of {len(data)}')
    return freq_dict, neigh_dct, l_dct, dist_dct


def get_statistics():
    global data_dir  # подгружаем глабальную переменную с директорией

    filename_lst = ['ru_syntagrus-ud-dev.conllu', 'ru_syntagrus-ud-test.conllu', 'ru_syntagrus-ud-train.conllu']

    conllu_data = []
    for name in filename_lst:  # складываем все прочитанные данные в одну переменную
        filename = data_dir + name
        text = file_read(filename)
        conllu_data.extend(parse_conllu(text))

    freq_dct, neigh_dct, l_dct, dist_dct = make_freq(conllu_data)  # получаем все нужные словари

    save_data([freq_dct, neigh_dct, l_dct, dist_dct])  # сохраняем полученную статистику


if __name__ == '__main__':
    get_statistics()
