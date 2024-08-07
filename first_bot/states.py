from aiogram.fsm.state import State, StatesGroup


class AddNewAdvertisement(StatesGroup):
    TASK_NAME = State()
    IMAGE = State()
    DESCRIPTION = State()
    GROUPS = State()
    DAY_RANGE = State()
    NIGHT_RANGE = State()


class ChangeDescription(StatesGroup):
    DESCRIPTION = State()


class ChangeImage(StatesGroup):
    IMAGE = State()


class ChangeDayRange(StatesGroup):
    DAY_RANGE = State()


class ChangeNightRange(StatesGroup):
    NIGHT_RANGE = State()


class ChangeGroupsList(StatesGroup):
    GROUPS_LIST = State()


class DeleteTask(StatesGroup):
    TASK_ID = State()
    CONFIRM = State()


class AddNewGroup(StatesGroup):
    GROUP_RANGE = State()
    GROUP_LINK = State()

class DeleteGroup(StatesGroup):
    GROUP = State()
