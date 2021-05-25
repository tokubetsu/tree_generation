from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:  # ячейка с характеристиками
    pos: str = None  # часть речи
    feats: any = None  # грамматические характеристики

    def __str__(self):  # превращение в строковый тип данный для сохранения
        if self.feats:
            feats = ','.join(self.feats)
        else:
            feats = None
        return f'|{self.pos}#{feats}|'

    def to_dict(self):  # превращение в словарь для сохранения в json
        dc = {'pos': self.pos, 'feats': self.feats}
        return dc

    def to_str(self):  # преврашение в строку для удобства и краткости вывода
        s = ''
        if self.pos:
            s += self.pos
        else:
            return 'root'
        if self.feats:
            s += ';' + ','.join(self.feats)
        return s


@dataclass(frozen=True)
class NumItem:  # нумерованный элемент, чтобы избежать зацикливания внутри дерева предложения
    word: any
    ident: int
