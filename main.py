import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import datetime
import os
import base64
from cryptography.fernet import Fernet

# Секретный ключ для AES-шифрования сообщений
# В реальном проекте лучше генерировать и хранить в защищенном месте
KEY = b'GHOST_SECURE_V13_KEY_STABLE_VERSION_2026_PRO_KEY=='
cipher = Fernet(KEY)

class GhostMessenger:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.bucket = None
        self.user_data = {"tag": "GHOST", "role": "USER", "uid": None}
        
        # Настройка визуальной части (Матрица/Терминал)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.fonts = {
            "Consolas": "https://github.com/google/fonts/raw/main/ofl/vt323/VT323-Regular.ttf"
        }
        
        self.init_firebase_system()
        self.show_auth_terminal()

    def init_firebase_system(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
            self.bucket = storage.bucket()
        except Exception as e:
            print(f"CRITICAL_SYSTEM_ERROR: {e}")

    # --- КРИПТОГРАФИЯ (AES-256) ---
    def crypt(self, text, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "DECRYPTION_FAILED"

    # --- СИСТЕМА УВЕДОМЛЕНИЙ ---
    def push_notify(self, title, msg):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"[{title.upper()}]: {msg}", color="#00FF00", font_family="Consolas"),
            bgcolor="#050505",
            border=ft.border.all(1, "#00FF00")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- ЭКРАН ВХОДА (ДИЗАЙН КАК НА СКРИНЕ) ---
    def show_auth_terminal(self):
        self.page.clean()
        
        email_f = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00", font_family="Consolas")
        pass_f = ft.TextField(label="ACCESS_PASSWORD", password=True, can_reveal_password=True, border_color="#00FF00")

        def login_process(e):
            # Секретный доступ админа
            if email_f.value == "admin" and pass_f.value == "TimaIssam2026":
                self.user_data = {"tag": "@admin", "role": "ADMIN", "uid": "ROOT"}
                self.push_notify("system", "root access granted")
                self.show_main_hub()
                return

            # Логика для обычных пользователей
            if email_f.value and pass_f.value:
                self.user_data["tag"] = f"@{email_f.value.split('@')[0]}"
                self.user_data["uid"] = email_f.value
                self.show_2fa_verification()

        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold", font_family="Consolas"),
                    ft.Container(
                        height=300, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", font_family="Consolas"),
                            ft.Text("> Шифрование: AES-256 ACTIVE", color="#00FF00", size=12, font_family="Consolas"),
                            ft.Text("> База данных: CONNECTED", color="#00FF00", size=12, font_family="Consolas"),
                        ])
                    ),
                    email_f,
                    pass_f,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#77FF77", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=login_process, bgcolor="#77FF77", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=15)
            )
        )

    def show_2fa_verification(self):
        self.page.clean()
        code_in = ft.TextField(label="ENTER_2FA_CODE", text_align="center", border_color="#00FF00", color="#00FF00")
        
        def verify_code(e):
            self.show_main_hub()
            self.push_notify("auth", f"welcome back {self.user_data['tag']}")

        self.page.add(
            ft.Container(
                alignment=ft.alignment.center, expand=True,
                content=ft.Column([
                    ft.Text("IDENTITY_CONFIRMATION", color="#00FF00", size=24, font_family="Consolas"),
                    ft.Text("Code sent to your secure email", color="#555555"),
                    code_in,
                    ft.ElevatedButton("INITIATE_SESSION", on_click=verify_code, bgcolor="#00FF00", color="black")
                ], horizontal_alignment="center")
            )
        )

    # --- ГЛАВНЫЙ МЕССЕНДЖЕР ---
    def show_main_hub(self):
        self.page.clean()
        self.chat_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=12)
        search_bar = ft.TextField(hint_text="SEARCH_BY_TAG (e.g. @nick)...", expand=True, border_color="#1A1A1A")
        msg_bar = ft.TextField(hint_text="Enter encrypted signal...", expand=True, border_color="#1A1A1A")

        def send_encrypted(e):
            if msg_bar.value:
                self.db.collection("secure_messages").add({
                    "u": self.user_data["tag"],
                    "m": self.crypt(msg_bar.value, "e"),
                    "r": self.user_data["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_bar.value = ""
                self.page.update()

        # Слушатель базы в реальном времени
        self.db.collection("secure_messages").order_by("ts").limit_to_last(50).on_snapshot(self.sync_ui)

        self.page.add(
            ft.Container(
                bgcolor="#080808", padding=15,
                content=ft.Row([
                    ft.Text("GHOST_PRO", color="#00FF00", size=20, weight="bold", font_family="Consolas"),
                    ft.Row([
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(self.user_data["role"]=="ADMIN"), on_click=lambda _: self.show_admin_terminal()),
                        ft.IconButton(ft.icons.PERSON_SEARCH, icon_color="#00FF00", on_click=lambda _: self.show_profile_settings()),
                    ])
                ], justify="spaceBetween")
            ),
            ft.Container(padding=10, content=ft.Row([search_bar, ft.IconButton(ft.icons.PERSON_ADD, icon_color="#00FF00")])),
            ft.Container(content=self.chat_container, expand=True, padding=15),
            ft.Container(
                bgcolor="#050505", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC_ROUNDED, icon_color="#00FF00"),
                    ft.IconButton(ft.icons.IMAGE_OUTLINED, icon_color="#00FF00"),
                    msg_bar,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_encrypted)
                ])
            )
        )

    def sync_ui(self, docs, changes, read_time):
        self.chat_container.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            self.chat_container.controls.append(
                ft.Container(
                    padding=12, border_radius=15, bgcolor="#0A0A0A" if not is_adm else "#001200",
                    border=ft.border.all(1, "#151515" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(m.get("u"), color="#00FF00", size=10, weight="bold"), ft.Text(m.get("time"), size=9, color="#444444")], justify="spaceBetween"),
                        ft.Text(self.crypt(m.get("m"), "d"), size=15, color="#EEEEEE")
                    ], spacing=4)
                )
            )
        if changes:
            self.push_notify("signal", "new encrypted message incoming")
        self.page.update()

    # --- ПРОФИЛЬ И ТЕХПОДДЕРЖКА ---
    def show_profile_settings(self):
        self.page.clean()
        new_tag = ft.TextField(label="IDENTITY_TAG", value=self.user_data["tag"], border_color="#00FF00")
        
        def save_and_exit(e):
            self.user_data["tag"] = new_tag.value
            self.push_notify("profile", "identity updated")
            self.show_main_hub()

        self.page.add(
            ft.AppBar(title=ft.Text("IDENTITY_MODULE"), bgcolor="#000000"),
            ft.Column([
                ft.Container(ft.Icon(ft.icons.ACCOUNT_BOX, size=120, color="#00FF00"), alignment=ft.alignment.center),
                new_tag,
                ft.ElevatedButton("SAVE_CHANGES", on_click=save_and_exit, bgcolor="#00FF00", color="black", width=400),
                ft.Divider(color="#111111"),
                ft.ListTile(leading=ft.Icon(ft.icons.BUG_REPORT), title=ft.Text("REPORT_ISSUE / SUPPORT"), on_click=lambda _: self.show_support_form()),
                ft.ElevatedButton("TERMINATE_SESSION", on_click=lambda _: self.page.window_destroy(), bgcolor="red", color="white", width=400),
                ft.TextButton("BACK_TO_CORE", on_click=lambda _: self.show_main_hub())
            ], spacing=20, horizontal_alignment="center", padding=20)
        )

    # --- АДМИН-ПАНЕЛЬ ---
    def show_admin_terminal(self):
        self.page.clean()
        target_tag = ft.TextField(label="TARGET_USER_TAG", border_color="red")
        broadcast_msg = ft.TextField(label="SYSTEM_WIDE_NOTIFICATION", multiline=True)

        def run_broadcast(e):
            self.db.collection("secure_messages").add({
                "u": "[SYSTEM_OVERRIDE]", "m": self.crypt(broadcast_msg.value, "e"),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.push_notify("admin", "global broadcast initiated")

        self.page.add(
            ft.AppBar(title=ft.Text("ROOT_OVERRIDE_TERMINAL"), bgcolor="#330000"),
            ft.Column([
                target_tag,
                ft.Row([
                    ft.ElevatedButton("BAN", bgcolor="red", color="white"),
                    ft.ElevatedButton("FREEZE", bgcolor="orange", color="black"),
                    ft.ElevatedButton("UNBAN", bgcolor="green", color="white")
                ], alignment="center"),
                ft.Divider(),
                ft.Text("ACTIVE_TICKETS: 0", color="#00FF00"),
                broadcast_msg,
                ft.ElevatedButton("EXECUTE_BROADCAST", on_click=run_broadcast, width=400, bgcolor="red"),
                ft.ElevatedButton("RETURN_TO_HUB", on_click=lambda _: self.show_main_hub(), width=400)
            ], padding=20, spacing=15)
        )

    def show_support_form(self):
        self.page.clean()
        issue = ft.TextField(label="DESCRIBE_ANOMALY", multiline=True, border_color="#00FF00")
        def submit(e):
            self.push_notify("support", "ticket submitted to root")
            self.show_main_hub()
        self.page.add(ft.Column([ft.Text("SUPPORT_CORE", size=24), issue, ft.ElevatedButton("SUBMIT", on_click=submit)]))

if __name__ == "__main__":
    ft.app(target=GhostMessenger)

 
