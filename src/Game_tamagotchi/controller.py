"""Controller (MVC): управляющий модуль"""

from pathlib import Path
from sys import path

from model import *


ROOT_DIR = Path(path[0]).parent.parent
DATA_DIR = ROOT_DIR / 'data'


class KindLoader:
    default_path: Path = DATA_DIR / 'kinds'
    
    @classmethod
    def _get_files(cls) -> list[Path]:
        return list(cls.default_path.glob('*.kind'))
    
    @classmethod
    def load(cls) -> list[Kind]:  
        kinds = []
        for file in cls._get_files():
            source = file.read_text(encoding='utf-8')
            # вычисление выражения в строке с исходным кодом - функция eval() возвращает объект, полученный в результате вычисления выражения
            kind = eval(source)
            kinds.append(kind)
        return kinds


class Application:
    def __init__(self):
        self.view = None
        self.creature: Creature = None
    
    def link_view(self, view):
        self.view = view
    
    def run(self) -> None:
        if self.is_live_creature():
            self.creature = self.load_creature()
        else:
            self.view.menu_frame(KindLoader.load())
        self.view.mainloop()
        self.save_creature()
    
    def is_live_creature(self) -> bool:
        ...
        # для теста
        return False
    
    def load_creature(self) -> Creature:
        ...
    
    def _progress_creature(self) -> Creature:
        ...
    
    def new_creature(
            self, 
            kind: Kind,
            name: str
    ) -> Creature:
        self.creature = Creature(kind, name)
        return self.creature
    
    def save_creature(self):
        ...


kinds = KindLoader.load()

