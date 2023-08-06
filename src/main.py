from settings import Settings
from windows import App


def main():
    """main function"""
    SETTINGS_FILE = "./settings.json"
    eg_settings = Settings(SETTINGS_FILE)
    eg_app = App(eg_settings)

    print("Programm EyesGuard started!")
    eg_app.mainloop()


# application entry point
if __name__ == "__main__":
    main()


# SETTINGS_FILE = './tests/data/test_config_invalid1.json'
