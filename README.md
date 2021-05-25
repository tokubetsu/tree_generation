# tree_generation
В данном репозитории выложен код к курсовой работе по теме "Автоматическая генерация дерева зависимостей с использованием статистики совместной встречаемости конструкций"

## Получение статистики
Для получения статистики в работе были использованы материалы из корпуса SynTagRus, они доступны в официальном репозитории по адресу: https://github.com/UniversalDependencies/UD_Russian-SynTagRus/tree/master </br>
</br>
Данную задачу в программе выполняет файл get_data.py, его требуется запустить перед тем, как начинать генерацию деревьев. </br>
Чтение файлов происходит из директории 'data/', находящейся в одной папке с вызываемой программой, для использования файлов, отличающихся от изначальных, требуется исправить глобальную переменную filename_lst в файле get_data.py. Все файлы должны быть в формате conllu. </br>
</br>
Файлы статистики, полученные в ходе работы программы, будут сохранены так же в директорию 'data/'.

## Генерация деревьев и линейного порядка

Требуется запустить файл main.py. В качестве входных данных программа использует данные, сохраненные в 'data/' при запуске get_data.py, поэтому специально ничего указывать не треубется. </br>
На выходе программа выдает в консоль сгенерированные деревья и линейный порядок к ним в формате, как на примере ниже: </br>
```root:
          root:
                    VERB;Imp,Ind,Sing,3,Pres,Fin,Act:
                              advmod:
                                        PART
                              xcomp:
                                        VERB;Perf,Neut,Sing,Past,Short,Part,Pass:
                                                  aux:pass:
                                                            AUX;Imp,Inf,Act
                                                  iobj:
                                                            NOUN;Inan,Dat,Fem,Sing
                                                  advmod:
                                                            ADV;Pos



1	 pos: PART;	 feats: None;	 head: 2;	 deprel: advmod
2	 pos: VERB;	 feats: Imp,Ind,Sing,3,Pres,Fin,Act;	 head: 0;	 deprel: root
3	 pos: AUX;	 feats: Imp,Inf,Act;	 head: 4;	 deprel: aux:pass
4	 pos: VERB;	 feats: Perf,Neut,Sing,Past,Short,Part,Pass;	 head: 2;	 deprel: xcomp
5	 pos: NOUN;	 feats: Inan,Dat,Fem,Sing;	 head: 4;	 deprel: iobj
6	 pos: ADV;	 feats: Pos;	 head: 4;	 deprel: advmod```
