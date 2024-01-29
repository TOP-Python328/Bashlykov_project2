"""View (MVC): представление"""

from itertools import zip_longest, count
from pathlib import Path
from random import choice
from tkinter import Tk, PhotoImage, StringVar
from tkinter.ttk import Frame, Button, Label

import model
import controller


class RootWidget(Tk):
    """Корневой виджет (Главное окно)"""
    def __init__(
            self,
            app: controller.Application,
    ):
        super().__init__()
        self.app = app
        
        self.title('Тамагочи')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.width = screen_width // 3
        self.height = screen_height * 9 // 10
        x = screen_width // 2 - self.width // 2
        y = screen_height // 2 - self.height // 2

        self.geometry(f'{self.width}x{self.height}+{x}+{y}')
        # блокировка изменения размера окна
        self.resizable(False, False)

        self.mainframe: Frame = None
    
    def menu_frame(self, kinds: list[model.Kind]) -> None:
        try:
            self.mainframe.destroy()
        except AttributeError:
            pass
        self.mainframe = MainMenu(self, kinds)
        self.update()
    
    def game_frame(self) -> None:
        try:
            self.mainframe.destroy()
        except AttributeError:
            pass
        self.mainframe = Game(self)
        self.mainframe.check_params()
        self.mainframe.update_params()
        self.update()


class MainMenu(Frame):
    """Меню в главном окне с выбором вида. Описывает фрейм первого запуска игры и выбор питомца"""
    def __init__(
            self, 
            master: RootWidget, 
            kinds: list[model.Kind]
    ):
        super().__init__(master)
        pad = master.width // 100 + 1
        self.grid(
            row=0, column=0,
            padx=pad, pady=pad,
            sticky='nsew',
        )
        columns = 2
        img_size = (master.width - pad*2*(columns+1)) // columns - 10
        self._images: list[PhotoImage] = []
        for i, kind in enumerate(kinds):
            img = PhotoImage(file=kind.image)
            img_width, img_height = img.width(), img.height()
            if img_width != img_size or img_height != img_size:
                img = _resize_image(
                    img,
                    img_width,
                    img_height,
                    img_size,
                    img_size,
                )
            self._images.append(img)
            row, column = divmod(i, columns)
            btn = Button(
                self,
                image=self._images[i],
                # необходимо добавить параметр в lambda-функцию, чтобы каждая из создаваемых в цикле функций обращалась к соответствующему экземпляру action
                # иначе, функции обращаются к action только во время вызова, а не в момент создания
                # https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
                command=lambda k=kind: self.choose_kind(k)
            )
            btn.grid(
                row=row, column=column,
                sticky='nsew',
                padx=pad, pady=pad,
            )
    
    def choose_kind(self, kind: model.Kind) -> None:
        name = self.get_creature_name()
        self.master.app.new_creature(kind, name)
        self.master.game_frame()
    
    def get_creature_name(self) -> str:
        # вызвать новое окно с Entry и Button 'Подтвердить'
        ...
        # для теста:
        return choice(['Джек', 'Яра', 'Бобик'])


class Game(Frame):
    """ Виджет игры (создание кнопок)"""
    def __init__(
            self, 
            master: RootWidget, 
    ):
        super().__init__(master)
        pad = (master.width // 100 + 1) * 2
        ipad = pad // 4
        self.grid(
            row=0, column=0,
            sticky='nsew',
            padx=pad, pady=pad,
        )
        self._screen_size = master.width - pad * 2
        self._actions_height = (master.height - self._screen_size - pad*4) // 3
        self._text_height = self._actions_height * 2
        self.rowconfigure(0, minsize=self._text_height)
        self.rowconfigure(1, minsize=self._screen_size)
        self.rowconfigure(2, minsize=self._actions_height)
        self.columnconfigure(0, minsize=self._screen_size)

        text_panel = Frame(self)
        text_panel.grid(
            row=0, column=0,
            sticky='nsew',
            pady=(0, pad),
        )
        text_panel.rowconfigure(0, minsize=self._text_height)
        text_panel.columnconfigure(0, minsize=self._screen_size//7*5)
        text_panel.columnconfigure(1, minsize=self._screen_size//7*2)

        self.message = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.message,
            wraplength=self._screen_size//7*5,
            font=('Arial Narrow', 18, 'italic', 'bold'),
            anchor='nw',
            justify='left',
            # background='#ccc',
        ).grid(
            row=0, column=0,
            sticky='nsew',
            ipadx=ipad, ipady=ipad,
        )

        self.params = StringVar(self, '')
        Label(
            text_panel,
            textvariable=self.params,
            wraplength=self._screen_size//7*2,
            font=('Consolas', 10, 'bold'),
            anchor='ne',
            justify='right',
            # background='#ddd',
        ).grid(
            row=0, column=1,
            sticky='nsew',
            ipadx=ipad, ipady=ipad,
        )

        self._image: PhotoImage = None
        self.screen = Label(self)
        self.screen.grid(
            row=1, column=0,
            sticky='nsew',
            pady=(0, pad),
        )

        self.create_buttons()

    def create_buttons(self):
        """Создаёт кнопки активности игрока"""
        buttons_panel = Frame(self)
        buttons_panel.grid(
            row=2, column=0,
            sticky='nsew',
        )
        buttons = 5
        self.actions: list[Button] = []
        self._buttons_images: list[PhotoImage] = []
        paddings = ((self._screen_size - self._actions_height*6)//(buttons-1),)*(buttons-1) + (0,)
        img_size = self._actions_height - 10
        for action, i in zip_longest(
                self.master.app.creature.player_actions,
                range(buttons),
                fillvalue=model.NoAction()
        ):
            img = PhotoImage(file=action.image)
            img_width, img_height = img.width(), img.height()
            if img_width != img_size or img_height != img_size:
                img = _resize_image(
                    img,
                    img_width,
                    img_height,
                    img_size,
                    img_size,
                )
            self._buttons_images.append(img)
            btn = Button(
                buttons_panel,
                image=img,
                state=action.state,
                # необходимо добавить параметр в lambda-функцию, чтобы каждая из создаваемых в цикле функций обращалась к соответствующему экземпляру action
                # иначе, функции обращаются к action только во время вызова, а не в момент создания
                # https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
                # command=lambda act=action: self.change_message(f'{act}\n{act.do()}'),
                command=lambda act=action: self.change_message(f'{act.do()}'),
            )
            btn.grid(
                row=0, column=i,
                sticky='nsew',
                padx=(0, paddings[i]),
            )
            self.actions.append(btn)

    def change_message(self, text: str) -> None:
        """Назначает текст для Label действий игрока"""
        self.message.set(text)
        self.update_idletasks()

    def change_params(self, text: str) -> None:
        """Назначает текст для Label параметров питомца"""
        self.params.set(text)
        self.update_idletasks()

    def change_image(self, img_path: str | Path) -> None:
        """Назначает картинку фрейму"""
        self._image = PhotoImage(file=img_path)
        # img_width, img_height = self._image.width(), self._image.height()
        # if img_width != self._screen_size or img_height != self._screen_size:
            # self._image = _resize_image(
                # self._image,
                # img_width,
                # img_height,
                # self._screen_size,
                # self._screen_size,
            # )
        self.screen.configure(image=self._image)
        self.update_idletasks()
    
    def check_params(self):
        # if self.master.app.creature.params[...]
        self.change_image(self.master.app.creature.kind.image)
        
        self.after(3000, lambda: self.check_params())
        self.update()
    
    def update_params(self):
        """Обновляет параметры существа."""
        self.master.app.creature.update()
        self.change_params(repr(self.master.app.creature))
        self.after(3000, lambda: self.update_params())
        self.update()
        


def _resize_image(
        image: PhotoImage,
        old_width: int,
        old_height: int,
        new_width: int,
        new_height: int
) -> PhotoImage:
    """Изменяет размер картинки"""
    resized_image = PhotoImage(width=new_width, height=new_height)
    for x in range(new_width):
        for y in range(new_height):
            x_old = x * old_width // new_width
            y_old = y * old_height // new_height
            rgb = '#{:02x}{:02x}{:02x}'.format(*image.get(x_old, y_old))
            resized_image.put(rgb, (x, y))
    return resized_image

