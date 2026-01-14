# main.py
from app_init import init_system
from gui_app import run_gui


if __name__ == "__main__":
    system = init_system()
    run_gui(system)
