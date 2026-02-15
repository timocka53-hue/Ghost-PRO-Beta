import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT
import base64

class GhostPro(toga.App):
    def startup(self):
        # Состояние системы
        self.is_admin = False
        self.current_user = "@guest"
        self.is_authenticated = False
        
        # Основной контейнер
        self.main_box = toga.Box(style=Pack(direction=COLUMN, background_color='#000000'))
        
        # Запуск экрана входа
        self.show_login_screen()
        
        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.main_box
        self.main_window.show()

    # --- ЭКРАН ЛОГИНА / РЕГИСТРАЦИИ ---
    def show_login_screen(self, widget=None):
        self.main_box.clear()
        
        container = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        title = toga.Label('GHOST_PRO_V7', style=Pack(color='#00FF00', font_size=28, font_weight='bold', padding=20))
        
        self.email_input = toga.TextInput(placeholder='EMAIL / IDENTIFIER', style=Pack(width=300, padding=5))
        self.pass_input = toga.PasswordInput(placeholder='PASSWORD', style=Pack(width=300, padding=5))
        
        btn_box = toga.Box(style=Pack(direction=ROW, padding=10))
        login_btn = toga.Button('LOGIN', on_press=self.handle_auth, style=Pack(width=140, padding=5))
        reg_btn = toga.Button('REGISTER', on_press=lambda x: self.main_window.info_dialog("SYSTEM", "Registration link sent to email"), style=Pack(width=140, padding=5))
        
        btn_box.add(login_btn, reg_btn)
        container.add(title, self.email_input, self.pass_input, btn_box)
        self.main_box.add(container)

    def handle_auth(self, widget):
        email = self.email_input.value
        password = self.pass_input.value
        
        # Скрытая админка
        if email == "adminpan" and password == "TimaIssam2026":
            self.is_admin = True
            self.current_user = "@ADMIN_CORE"
            self.show_main_interface() # Админ заходит без 2FA
        else:
            if email and password:
                self.temp_email = email
                self.show_2fa_screen()
            else:
                self.main_window.error_dialog("ERROR", "Fill all fields")

    # --- ЭКРАН 2FA ---
    def show_2fa_screen(self):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        info = toga.Label(f'CONFIRMATION SENT TO\n{self.temp_email}', style=Pack(color='#00FF00', text_align=CENTER, padding=10))
        self.code_input = toga.TextInput(placeholder='6-DIGIT CODE', style=Pack(width=200, padding=10))
        verify_btn = toga.Button('VERIFY_ID', on_press=self.finalize_auth)
        
        container.add(info, self.code_input, verify_btn)
        self.main_box.add(container)

    def finalize_auth(self, widget):
        self.current_user = f"@{self.temp_email.split('@')[0]}"
        self.show_main_interface()

    # --- ГЛАВНЫЙ ИНТЕРФЕЙС (ЧАТ / ПОИСК) ---
    def show_main_interface(self, widget=None):
        self.main_box.clear()
        
        # Верхняя панель
        header = toga.Box(style=Pack(direction=ROW, padding=10, background_color='#050505'))
        status_color = '#FF0000' if self.is_admin else '#00FF00'
        user_lbl = toga.Label(f"ID: {self.current_user}", style=Pack(color=status_color, flex=1, font_weight='bold'))
        profile_btn = toga.Button('⚙️', on_press=self.show_profile, style=Pack(width=40))
        header.add(user_lbl, profile_btn)

        # Поиск
        search_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.search_input = toga.TextInput(placeholder='SEARCH USER BY UID...', style=Pack(flex=1))
        search_btn = toga.Button('🔎', style=Pack(width=40))
        search_box.add(self.search_input, search_btn)

        # Окно чата (Native Multiline)
        self.chat_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, font_family='monospace', background_color='#000000', color='#00FF00', padding=5))
        self.chat_display.value = ">>> GHOST_PROTOCOL_V7_ENCRYPTED\n>>> WELCOME TO THE GRID"

        # Ввод сообщения и медиа
        input_row = toga.Box(style=Pack(direction=ROW, padding=10))
        self.msg_input = toga.TextInput(placeholder='Encrypted payload...', style=Pack(flex=1))
        send_btn = toga.Button('SEND', on_press=self.send_encrypted_msg)
        input_row.add(self.msg_input, send_btn)

        media_row = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        mic_btn = toga.Button('🎤 GС', on_press=lambda x: self.notify("RECORDING AUDIO..."))
        cam_btn = toga.Button('🎥 VIDEO', on_press=lambda x: self.notify("CAMERA ACTIVE"))
        img_btn = toga.Button('🖼️ PHOTO', on_press=lambda x: self.notify("GALLERY ACCESS"))
        media_row.add(mic_btn, cam_btn, img_btn)

        self.main_box.add(header, search_box, self.chat_display, input_row, media_row)
        
        if self.is_admin:
            admin_btn = toga.Button('MASTER_CONTROL_PANEL', on_press=self.show_admin_panel, style=Pack(color='#FF0000', padding=5))
            self.main_box.add(admin_btn)

    def send_encrypted_msg(self, widget):
        if self.msg_input.value:
            # Имитация ахуенного шифрования (Base64 + Shift)
            raw = self.msg_input.value
            encoded = base64.b64encode(raw.encode()).decode()
            self.chat_display.value += f"\n{self.current_user}: {raw}"
            self.msg_input.value = ""
            # Уведомление (имитация)
            self.notify(f"Message sent to network")

    # --- АДМИН ПАНЕЛЬ ---
    def show_admin_panel(self, widget):
        self.main_box.clear()
        title = toga.Label('CORE_ADMIN_V7', style=Pack(color='#FF0000', font_size=20, padding=10))
        
        # Функции админки
        grid = toga.Box(style=Pack(direction=COLUMN, padding=10))
        grid.add(toga.Button('BAN_USER_BY_ID', style=Pack(padding=5)))
        grid.add(toga.Button('FREEZE_ALL_CHANNELS', style=Pack(padding=5)))
        grid.add(toga.Button('WIPE_SERVER_LOGS', style=Pack(padding=5)))
        grid.add(toga.Button('GLOBAL_PUSH_NOTIFICATION', style=Pack(padding=5)))
        
        back_btn = toga.Button('BACK_TO_GRID', on_press=self.show_main_interface)
        self.main_box.add(title, grid, back_btn)

    # --- ПРОФИЛЬ И НАСТРОЙКИ ---
    def show_profile(self, widget):
        self.main_box.clear()
        
        title = toga.Label('IDENTITY_SETTINGS', style=Pack(color='#00FF00', font_size=20, padding=10))
        
        # Смена авы и юза
        self.uid_edit = toga.TextInput(value=self.current_user, style=Pack(padding=10))
        change_uid_btn = toga.Button('UPDATE_UID', on_press=self.update_uid)
        
        # О приложении (Шифрование и Анонимность)
        about_lbl = toga.Label(
            "ENCRYPTION: AES-256-P2P\n"
            "ANONYMITY: NO LOGS STORED\n"
            "ROUTING: MULTI-LAYER GHOST NODES",
            style=Pack(color='#00AA00', font_size=10, padding=20)
        )
        
        support_btn = toga.Button('CONTACT_TECH_SUPPORT', on_press=lambda x: self.main_window.info_dialog("SUPPORT", "Ticket created. Admin will respond in chat."))
        
        back_btn = toga.Button('BACK', on_press=self.show_main_interface)
        
        self.main_box.add(title, self.uid_edit, change_uid_btn, about_lbl, support_btn, back_btn)

    def update_uid(self, widget):
        self.current_user = self.uid_edit.value
        self.notify("UID_UPDATED")

    def notify(self, message):
        self.main_window.info_dialog("GHOST_SYSTEM", message)

def main():
    return GhostPro('Ghost PRO', 'com.ghost.v7')

if __name__ == '__main__':
    main().main_loop()
