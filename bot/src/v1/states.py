# Aiogram
from aiogram.fsm.state import State, StatesGroup


class Master(StatesGroup):
    select = State()
    pat_number = State()
    doc_number = State()
    reg = State()
