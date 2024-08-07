from aiogram.fsm.state import State, StatesGroup


class FormFill(StatesGroup):
    PRODUCT_MODEL = State()
    BRAND = State()
    MEMORY = State()
    BATERY = State()
    SCREEN_DEFECTS = State()
    BACK_PROBLEMS = State()
    OTHERS_DEFECTS = State()


class CreateUpdate(StatesGroup):
    MODEL = State()
    BRAND = State()
    BATERY_PRICE = State()
    PRICE = State()
    MIN_PRICE = State()
    SCREEN_DEFECTS = State()
    BACK_DEFECTS = State()
    OTHERS_DEFECTS = State()


class DeleteProduct(StatesGroup):
    START = State()


class ChangeProduct(StatesGroup):
    CHANGED_ELEMENT = State()
