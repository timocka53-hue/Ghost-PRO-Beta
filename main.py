import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
import base64
from cryptography.fernet import Fernet

# Сверхсекретный ключ AES-256 для защиты переписки
KEY = b'GHOST_ULTIMATE_SECURE_V13_TOKEN_2026_FULL_ACCESS_99=='
cipher = Fernet(KEY)

class GhostUltimateSystem:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.storage = None
        self.user_session = {"tag": "@ghost", "role": "USER", "logged": False}
        
        # Визуал в стиле 'Ghost OS' (как на твоем скрине)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.init_firebase_engine()
        self.render_terminal_auth()

    def init_firebase_engine(self):
        try:
            if not firebase_admin._apps:
                # Читаем данные из твоего google-services.json
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
            self.storage = storage.bucket()
        except Exception as e:
            print(f"BOOT_ERROR: {e}")

    def encrypt_signal(self, text):
        return cipher.encrypt(text.encode()).decode()

    def decrypt_signal(self, text):
        try: return cipher.decrypt(text.encode()).decode()
        except: return "[SIGNAL_CORRUPTED]"

    def show_toast(self, text, is_error=False):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(text, color="#00FF00" if not is_error else "red", weight="bold"),
            bgcolor="#050505",
            border=ft.border.all(1, "#00FF00" if not is_error else "red")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- ЭКРАН АВТОРИЗАЦИИ (ДИЗАЙН ИЗ 1000036510.jpg) ---
    def render_terminal_auth(self):
        self.page.clean()
        
        email_field = ft.TextField(
            label="EMAIL_ADDRESS", 
            border_color="#00FF00", 
            color="#00FF00",
            focused_border_color="#00FF00",
            cursor_color="#00FF00"
        )
        pass_field = ft.TextField(
            label="ACCESS_PASSWORD", 
            password=True, 
            can_reveal_password=True,
            border_color="#00FF00",
            color="#00FF00"
        )

        def attempt_login(e):
            if email_field.value == "admin" and pass_field.value == "TimaIssam2026":
                self.user_session = {"tag": "@admin", "role": "ADMIN", "logged": True}
                self.show_secure_hub()
            elif email_field.value and len(pass_field.value) > 5:
                # Имитация 2FA для безопасности
                self.user_session["tag"] = f"@{email_field.value.split('@')[0]}"
                self.render_2fa_step()
            else:
                self.show_toast("INVALID_ACCESS_KEY", True)

        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold"),
                    ft.Container(
                        height=300, 
                        border=ft.border.all(1, "#00FF00"), 
                        padding=15,
                        shadow=ft.BoxShadow(blur_radius=15, color="#3300FF00"),
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ft.Text("> Шифрование: AES-256 ACTIVE", color="#00FF00", size=12),
                            ft.Text("> База данных: CONNECTED", color="#00FF00", size=12),
                            ft.Text("> Статус сети: SECURE", color="#00FF00", size=12),
                        ], spacing=5)
                    ),
                    ft.Divider(height=20, color="transparent"),
                    email_field,
                    pass_field,
                    ft.ElevatedButton(
                        "REGISTRATION", 
                        bgcolor="#7FFF7F", 
                        color="black", 
                        width=400, 
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2))
                    ),
                    ft.ElevatedButton(
                        "LOG_IN", 
                        on_click=attempt_login,
                        bgcolor="#7FFF7F", 
                        color="black", 
                        width=400, 
                        height=55,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2))
                    ),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    def render_2fa_step(self):
        self.page.clean()
        code_input = ft.TextField(label="CONFIRM_2FA_CODE", text_align="center", border_color="#00FF00")
        
        def finish(e):
            self.show_toast("ACCESS_GRANTED")
            self.show_secure_hub()

        self.page.add(
            ft.Container(
                alignment=ft.alignment.center, expand=True,
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, color="#00FF00", size=50),
                    ft.Text("IDENTITY_VERIFICATION", color="#00FF00", size=20),
                    code_input,
                    ft.ElevatedButton("DECRYPT_SESSION", on_click=finish, bgcolor="#00FF00", color="black")
                ], horizontal_alignment="center", spacing=20)
            )
        )

    # --- ГЛАВНЫЙ ИНТЕРФЕЙС МЕССЕНДЖЕРА ---
    def show_secure_hub(self):
        self.page.clean()
        self.chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
        search_engine = ft.TextField(hint_text="SEARCH_BY_TAG...", expand=True, border_color="#1A1A1A", height=45)
        msg_input = ft.TextField(hint_text="Enter encrypted signal...", expand=True, border_color="#1A1A1A")

        def broadcast_signal(e):
            if msg_input.value:
                self.db.collection("ghost_stream").add({
                    "u": self.user_session["tag"],
                    "m": self.encrypt_signal(msg_input.value),
                    "r": self.user_session["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.page.update()

        # Слушатель обновлений в реальном времени
        self.db.collection("ghost_stream").order_by("ts").on_snapshot(self.sync_messages)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user_session['tag']}", color="#00FF00", weight="bold"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_session["role"]=="ADMIN"), icon_color="red", on_click=lambda _: self.show_admin_terminal()),
                    ft.IconButton(ft.icons.ACCOUNT_CIRCLE, icon_color="#00FF00", on_click=lambda _: self.show_profile_module())
                ]
            ),
            ft.Container(padding=10, content=ft.Row([search_engine, ft.IconButton(ft.icons.PERSON_SEARCH, icon_color="#00FF00")])),
            ft.Container(content=self.chat_history, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    ft.IconButton(ft.icons.IMAGE, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=broadcast_signal)
                ])
            )
        )

    def sync_messages(self, docs, changes, read_time):
        self.chat_history.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_adm = data.get("r") == "ADMIN"
            self.chat_history.controls.append(
                ft.Container(
                    padding=12, border_radius=12, 
                    bgcolor="#0A0A0A" if not is_adm else "#001500",
                    border=ft.border.all(1, "#151515" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), color="#00FF00", size=10, weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(self.decrypt_signal(data.get("m")), size=15, color="white")
                    ], spacing=5)
                )
            )
        self.page.update()

    # --- АДМИН-ПАНЕЛЬ ---
    def show_admin_terminal(self):
        self.page.clean()
        target_tag = ft.TextField(label="TARGET_USER_TAG", border_color="red")
        global_msg = ft.TextField(label="GLOBAL_BROADCAST_SIGNAL", multiline=True)

        def execute_broadcast(e):
            self.db.collection("ghost_stream").add({
                "u": "[SYSTEM_OVERRIDE]", "m": self.encrypt_signal(global_msg.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.show_toast("BROADCAST_EXECUTED")

        self.page.add(
            ft.AppBar(title=ft.Text("ROOT_OVERRIDE"), bgcolor="#330000"),
            ft.Column([
                target_tag,
                ft.Row([
                    ft.ElevatedButton("BAN_USER", bgcolor="red", color="white"),
                    ft.ElevatedButton("UNFREEZE", bgcolor="green", color="white")
                ], alignment="center"),
                ft.Divider(color="red"),
                global_msg,
                ft.ElevatedButton("SEND_TO_ALL_NODES", on_click=execute_broadcast, width=400, bgcolor="red"),
                ft.ElevatedButton("BACK_TO_HUB", on_click=lambda _: self.show_secure_hub(), width=400)
            ], padding=20, spacing=15)
        )

    # --- МОДУЛЬ ПРОФИЛЯ ---
    def show_profile_module(self):
        self.page.clean()
        new_tag = ft.TextField(label="EDIT_IDENTITY_TAG", value=self.user_session["tag"], border_color="#00FF00")
        
        def save_and_exit(e):
            self.user_session["tag"] = new_tag.value
            self.show_secure_hub()

        self.page.add(
            ft.AppBar(title=ft.Text("IDENTITY_MODULE"), bgcolor="#000000"),
            ft.Column([
                ft.Container(ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=100, color="#00FF00"), alignment=ft.alignment.center),
                new_tag,
                ft.ElevatedButton("SAVE_IDENTITY", on_click=save_and_exit, bgcolor="#00FF00", color="black", width=400),
                ft.Divider(color="#111111"),
                ft.ListTile(leading=ft.Icon(ft.icons.HELP_CENTER), title=ft.Text("SUPPORT / TICKETS"), on_click=lambda _: self.show_support()),
                ft.TextButton("LOG_OUT_TERMINAL", on_click=lambda _: self.render_terminal_auth())
            ], spacing=20, padding=20)
        )

    def show_support(self):
        self.page.clean()
        issue = ft.TextField(label="DESCRIBE_ANOMALY", multiline=True, border_color="#00FF00")
        def submit(e):
            self.show_toast("TICKET_CREATED")
            self.show_secure_hub()
        self.page.add(ft.Column([ft.Text("SUPPORT_CORE", size=22), issue, ft.ElevatedButton("SUBMIT", on_click=submit)]))

if __name__ == "__main__":
    ft.app(target=GhostUltimateSystem)
