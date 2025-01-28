import customtkinter
from multiplefilesframe import MultipleFilesFrame
from singlefileframe import SingleFileFrame

# Theme settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

#  CONSTANTS
WINDOW_WIDTH = 978
WINDOW_HEIGHT = 630
APP_TITLE = "Easy CHD"



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)

        # Font settings
        self.TITLE_FONT = customtkinter.CTkFont(size=30, weight="bold")

        # App title settings
        self.app_title_label = customtkinter.CTkLabel(
            master=self,
            text=APP_TITLE,
            font=self.TITLE_FONT,
            width=WINDOW_WIDTH
        )
        self.app_title_label.pack(
            padx=5,
            pady=(20, 10),
        )

        # Tab creation
        self.tabview = customtkinter.CTkTabview(master=self)
        self.tabview.pack(
            padx=20,
            pady=(0, 20),
            fill="both",
            expand=True
        )
        self.sf_tab = self.tabview.add("Single File")
        self.sf_view = SingleFileFrame(self.sf_tab)
        self.sf_view.pack()
        self.mf_tab = self.tabview.add("Multiple Files")
        self.mf_view = MultipleFilesFrame(self.mf_tab)
        self.mf_view.pack()
        self.tabview.set("Single File")



if __name__ == "__main__":
    app = App()
    app.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    app.resizable(width=False, height=False)
    app.eval('tk::PlaceWindow . center')
    app.mainloop()
