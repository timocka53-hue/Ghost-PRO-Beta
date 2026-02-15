import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import base64

class GhostPro(toga.App):
    def startup(self):
        self.is_admin = False
        self.current_user = "@guest"
        self.main_box = toga.Box(style=Pack(direction=COLUMN, background_color='#000000'))
        self.show_login()
        
        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def show_login(self):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        title = toga.Label('GHOST_PRO_V7', style=Pack(color='#00FF00', font_size=24, font_weight='bold', padding=20))
        
        self.email_input = toga.TextInput(placeholder='EMAIL', style=Pack(width=300, padding=5))
        self.pass_input = toga.PasswordInput(placeholder='PASSWORD', style=Pack(width=300, padding=5))
        
        btn = toga.Button('INITIALIZE', on_press=self.handle_login, style=Pack(width=200, padding=10))
        container.add(title, self.email_input, self.pass_input, btn)
        self.main_box.add(container)

    def handle_login(self, widget):
        e, p = self.email_input.value, self.pass_input.value
        if e == "adminpan" and p == "TimaIssam2026":
            self.is_admin, self.current_user = True, "@ADMIN_CORE"
            self.show_main()
        elif e and p:
            self.current_user = f"@{e.split('@')[0]}"
            self.show_2fa()

    def show_2fa(self):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        info = toga.Label('ENTER 2FA CODE FROM EMAIL', style=Pack(color='#00FF00', padding=10))
        self.code_in = toga.TextInput(placeholder='000000', style=Pack(width=150))
        btn = toga.Button('VERIFY', on_press=self.show_main)
        container.add(info, self.code_in, btn)
        self.main_box.add(container)

    def show_main(self, widget=None):
        self.main_box.clear()
        # Поиск и Хедер
        header = toga.Box(style=Pack(direction=ROW, padding=10, background_color='#050505'))
        header.add(toga.Label(f"ID: {self.current_user}", style=Pack(color='#00FF00', flex=1)))
        header.add(toga.Button('👤', on_press=self.show_profile, style=Pack(width=40)))
        
        search = toga.TextInput(placeholder='SEARCH UID...', style=Pack(flex=1, padding=5))
        
        # Чат
        self.chat = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, background_color='#000000', color='#00FF00'))
        self.chat.value = ">>> SECURE_LINE_ACTIVE"

        # Ввод и Медиа
        input_row = toga.Box(style=Pack(direction=ROW, padding=10))
        self.msg = toga.TextInput(placeholder='Payload...', style=Pack(flex=1))
        input_row.add(self.msg, toga.Button('SEND', on_press=self.send_msg))

        media = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        media.add(toga.Button('🎤 GS', on_press=lambda x: self.main_window.info_dialog("GHOST", "REC_AUDIO")))
        media.add(toga.Button('🎥 VID', on_press=lambda x: self.main_window.info_dialog("GHOST", "REC_VIDEO")))

        self.main_box.add(header, search, self.chat, input_row, media)
        if self.is_admin:
            self.main_box.add(toga.Button('MASTER_CONSOLE', style=Pack(color='red', padding=5)))

    def send_msg(self, widget):
        if self.msg.value:
            self.chat.value += f"\n{self.current_user}: {self.msg.value}"
            self.msg.value = ""

    def show_profile(self, widget):
        self.main_box.clear()
        self.main_box.add(toga.Label('IDENTITY_SETTINGS', style=Pack(color='#00FF00', font_size=20, padding=10)))
        self.main_box.add(toga.Label('ENCRYPTION: AES-256-P2P\nANONYMITY: HIGH', style=Pack(color='#00AA00', padding=20)))
        self.main_box.add(toga.Button('TECH_SUPPORT', on_press=lambda x: self.main_window.info_dialog("SYS", "Ticket Created")))
        self.main_box.add(toga.Button('BACK', on_press=self.show_main))

def main():
    return GhostPro('Ghost PRO', 'com.ghost.ghostpro')
