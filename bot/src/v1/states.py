# Aiogram
from aiogram.fsm.state import State, StatesGroup


class Master(StatesGroup):
    select = State()
    pat_number = State()
    doc_number = State()
    reg = State()


class Doctor(StatesGroup):
    add_patient = State()
    add_tests = State()
    wait_doc = State()
    break_state = State()


class Patient(StatesGroup):
    dialog = State()
