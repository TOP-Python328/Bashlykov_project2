from pathlib import Path
from sys import path


ROOT_DIR = Path(path[0]).parent.parent  
DATA_DIR = ROOT_DIR / 'data'

# имя питомца по умолчанию (пока не реализован запрос имени)
default_name = 'Питомец'
