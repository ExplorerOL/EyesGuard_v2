from settings import eg_settings

def main():
    '''main function'''
    print("Programm EyesGuard started!")
    print(eg_settings)
    print("Settings applied!")
    eg_settings.save_settings_to_file()

# application entry point
if __name__ == "__main__":
    main()
