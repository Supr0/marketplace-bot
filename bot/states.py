from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    lookup_state = State()

class FilterStates(StatesGroup):
    max_price_state = State()
    min_price_state = State()
    filter_state = State()
