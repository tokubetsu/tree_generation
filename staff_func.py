import conllu
import threading
import json
from save_txt_json import decode_file, encode_file
from staff_classes import Cell, NumItem


total_data = [{}, {}, {}, {}]  # глобальная переменная для чтения данных
data_dir = 'data/'  # глобальная переменная с директорией с изначальными данными


def file_read(filename):  # чтение файла
    with open(filename, encoding='utf-8') as f:
        text = f.read()
    return text


def save_data(files, names=('freq', 'neigh', 'l', 'dist')):  # сохранение созданных статистик
    with open(data_dir + f'{names[-1]}.json', 'w', encoding='utf-8') as f:
        json.dump(files[-1], f)

    for i, el in enumerate(files[:-1]):
        with open(f'{data_dir}{names[i]}.txt', 'w', encoding='utf-8') as f:
            encode_file(el, f_obj=f)


def read_file(filename, num):  # чтение файлов для загрузки стастик в генерацию
    global total_data, data_dir
    with open(data_dir + filename, 'r', encoding='utf-8') as f:
        if 'json' in filename:
            data = json.load(f)
        else:
            data = decode_file(f.read())
    total_data[num] = data
    print(f'{filename} read')


def read_data(filename=('freq.txt', 'neigh.txt', 'l.txt', 'dist.json')):  # запуск параллельных процессов с чтением
    freq_p = threading.Thread(target=read_file, args=(filename[0], 0))
    neigh_p = threading.Thread(target=read_file, args=(filename[1], 1))
    l_p = threading.Thread(target=read_file, args=(filename[2], 2))
    dist_p = threading.Thread(target=read_file, args=(filename[3], 3))

    freq_p.start()
    neigh_p.start()
    l_p.start()
    dist_p.start()

    dist_p.join()
    neigh_p.join()
    l_p.join()
    freq_p.join()

    return total_data[0], total_data[1], total_data[2], total_data[3]


def parse_conllu(text):  # разбор conllu
    info = conllu.parse(text)
    return info


def make_cell(item):  # создает ячейки из элемента conllu
    pos = item['upos']
    if item['feats']:
        feats = tuple(item['feats'][val] for val in sorted(item['feats'].keys()))
    else:
        feats = None
    res_word = Cell(pos, feats)
    ident = item['id']
    res = NumItem(res_word, ident)
    return res
