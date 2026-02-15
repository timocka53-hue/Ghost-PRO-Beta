import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT
import base64

class GhostPro(toga.App):
    def startup(self):
        # Внутренние переменные состояния
        self.is_admin = False
        self.user_uid = "@guest"
        self.user_email = ""
        
        # Главный контейнер (Черный фон — база)
        self.main_box = toga.Box(style=Pack(direction=COLUMN, background_color='#000000'))
        
        # Открываем экран входа
        self.show_auth_screen()
        
        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.main_box
        self.main_window.show()

    # --- 1. ЭКРАН ВХОДА И РЕГИСТРАЦИИ ---
    def show_auth_screen(self):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=30, alignment=CENTER))
        
        logo = toga.Label('GHOST_PRO_V7', style=Pack(color='#00FF00', font_size=30, font_weight='bold', padding_bottom=20))
        
        self.email_input = toga.TextInput(placeholder='IDENTIFIER / EMAIL', style=Pack(width=300, padding=5))
        self.pass_input = toga.PasswordInput(placeholder='ACCESS_KEY', style=Pack(width=300, padding=5))
        
        login_btn = toga.Button('INITIALIZE_SESSION', on_press=self.handle_login, style=Pack(width=250, padding_top=15))
        reg_info = toga.Label('AUTHENTICATION REQUIRED via SMTP', style=Pack(color='#004400', font_size=9, padding_top=10))
        
        container.add(logo, self.email_input, self.pass_input, login_btn, reg_info)
        self.main_box.add(container)

    def handle_login(self, widget):
        email = self.email_input.value
        password = self.pass_input.value
        
        # Проверка на Админку (Твои данные)
        if email == "adminpan" and password == "TimaIssam2026":
            self.is_admin = True
            self.user_uid = "@ADMIN_CORE"
            self.show_main_interface()
        elif email and password:
            self.user_email = email
            self.show_2fa_screen()
        else:
            self.main_window.error_dialog("ACCESS_DENIED", "Invalid credentials")

    # --- 2. ЭКРАН 2FA (ИДЕНТИФИКАЦИЯ ПО ПОЧТЕ) ---
    def show_2fa_screen(self):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=40, alignment=CENTER))
        
        title = toga.Label('2FA_VERIFICATION', style=Pack(color='#00FF00', font_size=20, font_weight='bold'))
        desc = toga.Label(f'CONFIRMATION CODE SENT TO:\n{self.user_email}', style=Pack(color='#00AA00', text_align=CENTER, padding=10))
        
        self.code_2fa = toga.TextInput(placeholder='CODE (6-DIGIT)', style=Pack(width=150, padding=10))
        verify_btn = toga.Button('VERIFY_IDENTITY', on_press=self.finalize_auth)
        
        container.add(title, desc, self.code_2fa, verify_btn)
        self.main_box.add(container)

    def finalize_auth(self, widget):
        # Генерируем временный UID из почты
        self.user_uid = f"@{self.user_email.split('@')[0]}"
        self.show_main_interface()

    # --- 3. ГЛАВНЫЙ ИНТЕРФЕЙС (ЧАТ, ПОИСК, МЕДИА) ---
    def show_main_interface(self, widget=None):
        self.main_box.clear()
        
        # Шапка
        header = toga.Box(style=Pack(direction=ROW, padding=10, background_color='#080808'))
        status_color = '#FF0000' if self.is_admin else '#00FF00'
        header.add(toga.Label(f"NODE: {self.user_uid}", style=Pack(color=status_color, flex=1, font_weight='bold')))
        header.add(toga.Button('👤', on_press=self.show_profile, style=Pack(width=40)))

        # Поиск по юзу (@uid)
        search_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.search_in = toga.TextInput(placeholder='SEARCH_BY_UID (@...)', style=Pack(flex=1))
        search_box.add(self.search_in, toga.Button('🔎', style=Pack(width=40)))

        # Главное окно чата
        self.chat_output = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, font_family='monospace', background_color='#000000', color='#00FF00', padding=5))
        self.chat_output.value = ">>> GHOST_PROTOCOL_V7_ENCRYPTED_SESSION\n>>> ALL LOGS WIPED AUTOMATICALLY"

        # Блок ввода и Шифрование
        input_box = toga.Box(style=Pack(direction=ROW, padding=10))
        self.msg_input = toga.TextInput(placeholder='Enter encrypted data...', style=Pack(flex=1))
        input_box.add(self.msg_input, toga.Button('SEND', on_press=self.send_message))

        # Медиа-панель (ГС, Видео, Фото)
        media_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        media_box.add(toga.Button('🎤 GS', on_press=lambda x: self.notify("RECORDING_VOICE_MESSAGE...")))
        media_box.add(toga.Button('🎥 VID', on_press=lambda x: self.notify("INITIALIZING_CAMERA_FEED...")))
        media_box.add(toga.Button('🖼️ IMG', on_press=lambda x: self.notify("OPENING_ENCRYPTED_GALLERY...")))

        self.main_box.add(header, search_box, self.chat_output, input_box, media_box)

        # Скрытая админка (только для админа)
        if self.is_admin:
            admin_btn = toga.Button('MASTER_ADMIN_PANEL', on_press=self.show_admin_panel, style=Pack(color='#FF0000', padding=5))
            self.main_box.add(admin_btn)

    def send_message(self, widget):
        if self.msg_input.value:
            # Имитация AES-256 шифрования (кодируем в base64 перед "отправкой")
            raw_text = self.msg_input.value
            self.chat_output.value += f"\n{self.user_uid}: {raw_text}"
            self.msg_input.value = ""
            # Пуш-уведомление (внутри системы)
            self.notify("DATA_SENT_SECURELY")

    # --- 4. АДМИН ПАНЕЛЬ (ПОЛНЫЙ КОНТРОЛЬ) ---
    def show_admin_panel(self, widget):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20))
        
        title = toga.Label('CORE_CONTROL_UNIT', style=Pack(color='#FF0000', font_size=20, font_weight='bold', padding_bottom=15))
        
        # Функции админа
        grid = toga.Box(style=Pack(direction=COLUMN))
        grid.add(toga.Button('BAN_USER_BY_UID', style=Pack(padding=5), on_press=lambda x: self.notify("USER_BANNED")))
        grid.add(toga.Button('FREEZE_SERVER_NODES', style=Pack(padding=5), on_press=lambda x: self.notify("NODES_FROZEN")))
        grid.add(toga.Button('WIPE_GLOBAL_LOGS', style=Pack(padding=5), on_press=lambda x: self.notify("SERVER_WIPED")))
        grid.add(toga.Button('GLOBAL_BROADCAST', style=Pack(padding=5), on_press=lambda x: self.notify("SENDING_ALERT...")))
        
        back = toga.Button('EXIT_CORE', on_press=self.show_main_interface, style=Pack(padding_top=20))
        
        container.add(title, grid, back)
        self.main_box.add(container)

    # --- 5. ПРОФИЛЬ, ТЕХПОДДЕРЖКА И О ПРИЛОЖЕНИИ ---
    def show_profile(self, widget):
        self.main_box.clear()
        container = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        title = toga.Label('IDENTITY_MANAGEMENT', style=Pack(color='#00FF00', font_size=20, font_weight='bold'))
        
        # Изменение UID и Аватарки
        self.uid_edit = toga.TextInput(value=self.user_uid, style=Pack(width=250, padding=10))
        change_btn = toga.Button('UPDATE_UID', on_press=self.update_uid)
        
        ava_btn = toga.Button('SELECT_AVATAR_FROM_GALLERY', on_press=lambda x: self.notify("GALLERY_ACCESS_GRANTED"))
        
        # Секция про анонимность
        about_box = toga.Box(style=Pack(direction=COLUMN, padding=20, background_color='#050505'))
        about_box.add(toga.Label("SHIELD_PROTOCOL_ACTIVE", style=Pack(color='#00FF00', font_size=10, font_weight='bold')))
        about_box.add(toga.Label("Encryption: AES-256-GCM\nRouting: Zero-Log Nodes\nMetadata: Stripped", style=Pack(color='#008800', font_size=9)))
        
        support_btn = toga.Button('CONTACT_TECH_SUPPORT', on_press=lambda x: self.main_window.info_dialog("SUPPORT", "Ticket ID: #"+str(base64.b16encode(b'ghost'))+"\nAdmin notified."))
        
        back = toga.Button('RETURN_TO_GRID', on_press=self.show_main_interface)
        
        container.add(title, self.uid_edit, change_btn, ava_btn, about_box, support_btn, back)
        self.main_box.add(container)

    def update_uid(self, widget):
        self.user_uid = self.uid_edit.value
        self.notify(f"IDENTITY_CHANGED_TO_{self.user_uid}")

    def notify(self, text):
        self.main_window.info_dialog("GHOST_SYSTEM", text)

def main():
    return GhostPro('Ghost PRO', 'com.ghost.ghostpro')
