def get_pos(dist, dep):  # получаем наиболее частотное положение
    if dep != 'root':  # если это не корень
        cur = dist[dep]
        sum_p = 0
        sum_n = 0
        for el in cur:  # считаем сумму частот отрицательных и положительных позиций
            if int(el) > 0:
                sum_p += cur[el]
            else:
                sum_n += cur[el]
        if sum_p >= sum_n:  # возвращаем соответствующий результат
            return 1
        else:
            return -1
    else:
        return 0


def get_order(tree, dist):  # получаем порядок слов
    seq = []
    
    if len(tree) > 1:  # уходим максимально вглубь, пока есть возможность
        for el in tree[1:]:
            lst, head = get_order(el[1], dist)  # получаем порядок для всех уровней вниз
            lst[head].append(el[0])  # добавляем тип связи
            seq.append(lst)  # добавляем к последовательности на текущем уровне
    else:
        # если дальше некуда, то возвращаем список вида [[лист, вершина для листа (0, так как не определена)], ]
        # второй 0 - индекс вершины текущего уровня
        return [[tree[0], 0], ], 0
    
    total_seq = []
    prev_point = -1
    head_pos = -1
    for i, el in enumerate(tree[1:]):  # перебираем всех потомков текущей вершины
        dep = el[0]  # связь с потомком
        point = get_pos(dist, dep)  # получаем позицию
        if point == prev_point:  # если она такая же, как была, то просто добавляем
            total_seq.extend(seq[i])
            prev_point = point
        else:
            if (point != 0) and (head_pos == -1):  # если позиция сменилась и вершина пока не в списке, то добавляем
                total_seq.append([tree[0], 0])
                head_pos = len(total_seq) - 1
            total_seq.extend(seq[i])  # добавялем потомка
            prev_point = point
    
    if (head_pos == -1) and (prev_point != 0):  # если вершина не добавлена и это не корень, то добавляем
        total_seq.append([tree[0], 0])
        head_pos = len(total_seq) - 1

    for j in range(len(total_seq)):  # переопределяем номера вершин для всех новых элементов
        if (j != head_pos) and (total_seq[j][1] == 0):
            total_seq[j][1] = j - head_pos

    return total_seq, head_pos


def print_seq(seq):
    for key, el in enumerate(seq):
        s = f'{key + 1}\t '
        if isinstance(el[0], dict):
            s += f'pos: {el[0]["pos"]};\t feats: {", ".join(el[0]["feats"])};\t '
        else:
            small_s = el[0].split(';')
            small_s.extend([None for _ in range(2 - len(small_s))])
            s += f'pos: {small_s[0]};\t feats: {str(small_s[1])};\t '
        s += f'head: {key + 1 - el[1]};\t deprel: {el[2]}'
        print(s)
