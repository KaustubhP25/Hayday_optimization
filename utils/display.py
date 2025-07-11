class Display:
    @staticmethod
    def menu(arr):
        menu_options = arr
        index=1
        if menu_options[-1].lower()!="exit":
            menu_options.append("EXIT")
        for option in menu_options:
            if option.lower() == "exit":
                print(f"[0] - {option}")
                break
            print(f"[{index}] - {option}")
            index+=1

    @staticmethod
    def result():
        pass