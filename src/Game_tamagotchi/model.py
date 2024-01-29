"""Модель (MVC) приложения"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from random import choice, sample
from sys import path
from typing import Type


ROOT_DIR = Path(path[0]).parent.parent 
DATA_DIR = ROOT_DIR / 'data'

class DictOfRanges(dict):
    def __init__(self, mappable: dict):
        for key in mappable:
            if (
                   not isinstance(key, tuple) 
                or len(key) != 2
                or not isinstance(key[0], int) 
                or not isinstance(key[1], int)
            ):
                raise ValueError('...')
        super().__init__(mappable)
    
    def __getitem__(self, key: int):
        if isinstance(key, int):
            for left, right in self:
                if left <= key <= right:
                    return super().__getitem__((left, right))
        else:
            return super().__getitem__(key)
    
    def get_range(self, key: int) -> tuple[int, int]:
        if isinstance(key, int):
            for left, right in self:
                if left <= key <= right:
                    return left, right
        else:
            raise TypeError


@dataclass
class KindParameter:
    """Описывает параметры для фазы возраста(зрелости) питомца"""
    name: str
    initial: float
    min: float
    max: float
    
    def __hash__(self):
        return hash(self.name)


class CreatureParameter(ABC):
    """Описывает параметры существа"""
    name: str
    
    def __init__(
            self,
            initial: float,
            left: float,
            right: float,
            creature: 'Creature',
    ):
        self.__value = initial
        self._min = left
        self._max = right
        self.creature = creature
    
    @property
    def value(self) -> float:
        return self.__value
    
    @cached_property
    def range(self) -> tuple[float, float]:
        return self._min, self._max
    
    @value.setter
    def value(self, new_value: float):
        if new_value <= self._min:
            self.__value = self._min
        elif self._max <= new_value:
            self.__value = self._max
        else:
            self.__value = new_value
    
    @abstractmethod
    def update(self) -> None:
        pass


class Health(CreatureParameter):
    """Описывает здоровье существа."""
    name = 'здоровье'
    
    def update(self) -> None:
        """Пересчитывает параметр Health"""
        satiety = self.creature.params[Satiety]
        thirst = self.creature.params[Thirst]
        tiredness = self.creature.params[Tiredness]
        mood = self.creature.params[Mood]
        critical_satiety = sum(satiety.range) / 4
        critical_thirst = 3 * (sum(thirst.range) / 4)
        critical_tiredness = 3 * (sum(tiredness.range) / 4)
        critical_mood = sum(mood.range) / 4
        if (
            0 < satiety.value < critical_satiety or 
            0 < mood.value < critical_mood or 
            thirst.value > critical_thirst or
            tiredness.value > critical_tiredness
        ):
            self.value -= 0.5
        elif (
              satiety.value == 0 or
              mood.value == 0 or
              thirst.value == critical_thirst or
              tiredness.value == critical_tiredness
        ):
             self.value -= 1
        else:   
            self.value += 0.5


class Satiety(CreatureParameter):
    """Описывает сытость существа."""
    name = 'сытость'
    
    def update(self) -> None:
        self.value -= 1
        
        
class Thirst(CreatureParameter):
    """Описывает жажду существа"""
    name = 'жажда'

    def update(self) -> None:
        self.value += 1
        
        
class Tiredness(CreatureParameter):
    """Описывает усталость существа."""
    name = 'усталость'
    
    def update(self) -> None:
        self.value += 0.5

        
class Mood(CreatureParameter):
    """Описывает настроение существа."""
    name = 'настроение'
    
    def update(self) -> None:
        self.value -= 0.5


Parameters = Enum(
    """Перечислитель параметров."""
    'Parameters',
    {
        cls.__name__: cls
        for cls in CreatureParameter.__subclasses__()
    }
)


class Action(ABC):
    """Родительский класс для активностей(действий)"""
    name: str
    image: Path
    
    def __init__(self, creature: 'Creature' = None):
        self.creature = creature
    
    def __hash__(self):
        return hash(self.name)
    
    @abstractmethod
    def do(self) -> str:
        pass


class PlayerAction(Action):
    """Описывает действия игрока"""
    image: Path
    state = 'normal'


class Feed(PlayerAction):
    name = 'покормить питомца'
    image = DATA_DIR / 'images/btn1.png'
    
    def __init__(
            self, 
            amount: float = 5.0,
            creature: 'Creature' = None, 
    ):
        self.amount = amount
        super().__init__(creature)
    
    def do(self) -> str:
        """Пересчитывает параметр Satiety"""
        self.creature.params[Satiety].value += self.amount
        self.creature.params[Tiredness].value -= 2.0
        return f'вы покормили питомца на {self.amount} ед.'
        
        
class Give_to_drink(PlayerAction):
    name = 'напоить питомца'
    image = DATA_DIR / 'images/btn2.png'
    
    def __init__(
            self, 
            amount: float = 3.0,
            creature: 'Creature' = None, 
    ):
        self.amount = amount
        super().__init__(creature)
    
    def do(self) -> str:
        """Пересчитывает параметр Thirst"""
        self.creature.params[Thirst].value -= self.amount
        self.creature.params[Tiredness].value -= 1.0
        return f'вы напоили питомца на {self.amount} ед.'

        
class PlayPet(PlayerAction):
    name = 'поиграть с питомцем'
    image = DATA_DIR / 'images/btn5.png'
    
    def do(self):
        """Пересчитывает параметы существа"""
        self.creature.params[Mood].value += 1.5
        self.creature.params[Satiety].value -= 0.5
        self.creature.params[Tiredness].value += 1.0
        self.creature.params[Thirst].value += 0.5
        return f'вы поиграли с питомцем'
        
        
class TrainPet(PlayerAction):
    name = 'дрессировать питомца'
    image = DATA_DIR / 'images/btn6.png'
    
    def do(self):
        """Пересчитывает параметы существа"""
        self.creature.params[Mood].value -= 0.5
        self.creature.params[Satiety].value -= 0.5
        self.creature.params[Tiredness].value += 0.5
        self.creature.params[Thirst].value += 0.5
        return f'вы подрессировали питомца'

        
class TeaseHead(PlayerAction):
    name = 'почесать голову'
    image = DATA_DIR / 'images/btn3.png'
    
    def do(self) -> str:
        """Пересчитывает параметр Mood"""
        self.creature.params[Mood].value += 1
        return 'вы почесали голову питомцу'
        

class NoAction(PlayerAction):
    name = 'бездействие'
    image = DATA_DIR / 'images/no_action.png'
    state = 'disabled'
    
    def do(self) -> None:
        print('бездействует')
        
        
class CreatureAction(Action):
    """Описывает действие питомца"""
    image: Path
    
    def __init__(
            self,
            rand_coeff: float,
            creature: 'Creature' = None, 
    ):
        self.rand_coeff = rand_coeff
        super().__init__(creature)


class ChaseTail(CreatureAction):
    name = 'гоняться за своим хвостом'
    image = DATA_DIR / 'images/btn4.png'
    
    """Пересчитывает параметр Mood"""
    def do(self) -> str:
        self.creature.params[Mood].value += 1
        self.creature.params[Tiredness].value += 1
        return f'{self.creature.name} бегает за своим хвостом'
        
        
class Sleep(CreatureAction):
    name = 'питомец спит'
    image = DATA_DIR / 'images/dog_sleep.png'
    
    def do(self) -> str:
        """Пересчитывает параметр Tiredness"""
        self.creature.params[Tiredness].value -= 3.0
        return f'{self.creature.name} спит'
        

class Miss(Action):
    name = 'питомец скучает'
    image = DATA_DIR / 'images/dog_miss.png'

    def do(self) -> str:
        """Пересчитывает параметр Mood"""
        self.creature.params[Mood].value -= 2.0
        return f'{self.creature.name} скучает'


class MaturePhase:
    """Описывает фазы возраста(зрелости) питомца. 
    Включает: колличество дней на определенной фазе возраста, список параметров питомца, список действий игрока, список активностей питомца.
    """
    def __init__(
            self, 
            days: int,
            *parameters: KindParameter,
            player_actions: Iterable[PlayerAction],
            creature_actions: Iterable[CreatureAction],
    ):
        self.days = days
        self.params = set(parameters)
        self.player_actions = set(player_actions)
        self.creature_actions = set(creature_actions)


class Kind(DictOfRanges):
    def __init__(
            self, 
            name: str, 
            image: Path,
            *mature_phases: MaturePhase
    ):
        self.name = name
        self.image = image
        
        phases = {}
        left = 0
        for phase in mature_phases:
            key = left, left + phase.days - 1
            phases[key] = phase
            left = left + phase.days
        super().__init__(phases)
        
        self.max_age = left - 1


@dataclass
class State:
    age: int
    
    def __repr__(self):
        return '/'.join(v for v in self.__dict__.values())


class History(list):
    """Описывает историю сохраненных состояний"""
    def get_param(self, param: Type) -> list[float]:
        return [
            getattr(state, param.__name__)
            for state in self
        ]


class Creature:
    """Описывает создаваемое существо (питомца)"""
    def __init__(
            self, 
            kind: Kind,
            name: str,
    ):
        self.kind = kind
        self.name = name
        self.__age: int = 0
        self.params: dict[Type, CreatureParameter] = {}
        for param in kind[0].params:
            cls = Parameters[param.name].value
            self.params[cls] = cls(
                initial=param.initial,
                left=param.min,
                right=param.max,
                creature=self,
            )
        self.player_actions: set[PlayerAction]
        self.creature_actions: set[CreatureAction]
        self.__set_actions()
        self.history: History = History()
    
    def __repr__(self):
        title = f'({self.kind.name}) {self.name}: {self.age} ИД'
        params = '\n'.join(
            f'{p.name}: {p.value:.1f}' 
            for p in self.params.values()
        )
        return f'{title}\n{params}'
        # return f'{params}'
    
    def __set_actions(self) -> None:
        self.player_actions = {
            action.__class__(**{**action.__dict__, 'creature': self})
            for action in self.kind[self.age].player_actions
        }
        self.creature_actions = {
            action.__class__(**{**action.__dict__, 'creature': self})
            for action in self.kind[self.age].creature_actions
        }
    
    def update(self) -> None:
        """Обновляет параметры существа."""
        for param in self.params.values():
            param.update()
        self.save()
    
    @property
    def age(self) -> int:
        return self.__age
    
    @age.setter
    def age(self, new_value: int):
        old_phase = self.kind.get_range(self.__age)
        new_phase = self.kind.get_range(new_value)
        self.__age = new_value
        if old_phase != new_phase:
            self._grow_up()
    
    def _grow_up(self) -> None:
        for param in self.kind[self.age].params:
            cls = Parameters[param.name].value
            initial = param.initial or self.params[cls].value
            self.params[cls] = cls(
                initial=initial,
                left=param.min,
                right=param.max,
                creature=self,
            )
        self.__set_actions()
    
    def random_action(self) -> None:
        action = choice(tuple(self.creature_actions))
        no_action = NoAction()
        prob = int(action.rand_coeff * 100)
        choice(sample([action, no_action], counts=[prob, 100-prob], k=100)).do()
    
    def save(self) -> State:
        state = State(self.age)
        for cls, param in self.params.items():
            setattr(state, cls.__name__, param.value)
        self.history.append(state)
        return state


