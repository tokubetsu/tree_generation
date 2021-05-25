from trees import create_tree, print_tree
from staff_func import read_data
from lineseq import get_order, print_seq
from time import time


def main():
    begin = time()
    freq, neigh, l, dist = read_data()  # читаем все имеющиеся файлы, при этом засекаем время на чтение
    end = time()
    print(int(end - begin))

    stop = False  # определяем переменную, говорящую, чтоит ли остановить генерацию
    normal = False  # определяем переменную, говоряющую какую запись деревьев мы хотим видеть: строкой или ячейкой
    root = False  # определяем, устраивает ли нас дерево из одного корня
    # печать в консоль доступна только для строк, но Cell() более удобны для работы внутри программы
    while not stop:  # выполняем генерацию, пока не сказано обратное
        tree, _ = create_tree(freq, neigh, l, normal=normal, root=root)  # генерируем дерево
        print_tree(tree)  # выводим дерево в консоль
        print('\n\n')
        seq, _ = get_order(tree, dist)  # получаем линейный порядок
        print_seq(seq)  # выводим порядок в консоль
        s = input('Stop? Yes/No\n')  # спрашиваем, стоит ли остановиться
        if s == 'Yes':
            stop = True


if __name__ == '__main__':
    main()
