import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import datetime
import os
import base64
from cryptography.fernet import Fernet

# Твой ключ шифрования (в идеале тянуть из секретов)
SECRET_KEY = b'GHOST_ULTIMATE_SECURE_KEY_2026_V13_GHOSTPRO=='
cipher = Fernet(SECRET_KEY)

class GhostMessenger:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = None
        self.role = "USER"
        self.setup_ui()
        self.init_firebase()
        self.show_auth_page()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                # Используем твой конфиг из google-services.json
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
            self.bucket = storage.bucket()
        except Exception as e:
            self.error_msg(f"DATABASE_OFFLINE: {e}")

    def setup_ui(self):
        self.page.title = "GHOST PRO"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 10

    def error_msg(self, text):
        self.page.snack_bar = ft.SnackBar(ft.Text(text, color="#FF0000"))
        self.page.snack_bar.open = True
        self.page.update()

    # --- ШИФРОВАНИЕ ---
    def encrypt(self, data):
        return cipher.encrypt(data.encode()).decode()

    def decrypt(self, data):
        try: return cipher.decrypt(data.encode()).decode()
        except: return "[ENCRYPTED_DATA]"

    # --- АУТЕНТИФИКАЦИЯ И 2FA ---
    def show_auth_page(self):
        self.page.clean()
        email_f = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00")
        pass_f = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")
        
        def handle_auth(e):
            # Секретный вход админа
            if email_f.value == "admin" and pass_f.value == "TimaIssam2026":
                self.user = "SYSTEM_ADMIN"
                self.role = "ADMIN"
                self.show_main_hub()
                return
            
            # Реальная логика (симуляция 2FA для Flet)
            try:
                # В реале тут: auth.get_user_by_email(email_f.value)
                self.show_2fa_step(email_f.value)
            except: self.error_msg("USER_NOT_FOUND")

        self.page.add(
            ft.Column([
                ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=24, weight="bold"),
                ft.Container(height=200, border=ft.border.all(1, "#00FF00"), content=ft.Text("SYSTEM: Ожидание входа...", color="#00FF00"), padding=10),
                email_f, pass_f,
                ft.ElevatedButton("INITIALIZE LOG_IN", on_click=handle_auth, bgcolor="#00FF00", color="black", width=400)
            ], horizontal_alignment="center")
        )

    def show_2fa_step(self, email):
        self.page.clean()
        code_f = ft.TextField(label="ENTER_2FA_CODE (SENT TO EMAIL)", border_color="#00FF00")
        
        def verify(e):
            if code_f.value == "1234": # Пример, тут должна быть проверка из БД/Email
                self.user = email.split('@')[0]
                self.show_main_hub()
            else: self.error_msg("WRONG_CODE")

        self.page.add(ft.Column([code_f, ft.ElevatedButton("VERIFY", on_click=verify, bgcolor="#00FF00", color="black")]))

    # --- ГЛАВНЫЙ ХАБ ---
    def show_main_hub(self):
        self.page.clean()
        chat_col = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_input = ft.TextField(hint_text="Type encrypted message...", expand=True)

        def send_msg(e):
            if msg_input.value:
                self.db.collection("messages").add({
                    "u": self.user, "t": self.encrypt(msg_input.value), "ts": firestore.SERVER_TIMESTAMP,
                    "type": "text"
                })
                msg_input.value = ""
                self.page.update()

        # Поток сообщений в реальном времени
        def on_snapshot(docs, changes, read_time):
            chat_col.controls.clear()
            for doc in docs:
                m = doc.to_dict()
                chat_col.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(m.get("u"), color="#00FF00", size=10),
                            ft.Text(self.decrypt(m.get("t")), size=16)
                        ]),
                        padding=10, border=ft.border.all(1, "#111111"), border_radius=10
                    )
                )
            self.page.update()

        self.db.collection("messages").order_by("ts").on_snapshot(on_snapshot)

        self.page.add(
            ft.AppBar(title=ft.Text(f"GHOST: {self.user}"), bgcolor="#0A0A0A", actions=[
                ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.role=="ADMIN"), on_click=lambda _: self.show_admin())
            ]),
            ft.Container(content=chat_col, expand=True),
            ft.Row([
                ft.IconButton(ft.icons.MIC, icon_color="#00FF00"), # Для голосовых
                ft.IconButton(ft.icons.IMAGE, icon_color="#00FF00"), # Для фото/видео
                msg_input,
                ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
            ])
        )

    # --- АДМИНКА ---
    def show_admin(self):
        self.page.clean()
        user_id = ft.TextField(label="USER_TAG_TO_BAN")
        
        def broadcast(e):
            self.db.collection("messages").add({
                "u": "SYSTEM", "t": self.encrypt("ВНИМАНИЕ: ОБНОВИТЕ ПРИЛОЖЕНИЕ В ТГ!"),
                "ts": firestore.SERVER_TIMESTAMP, "type": "alert"
            })

        self.page.add(
            ft.Text("ROOT_PANEL", color="red", size=30),
            user_id,
            ft.Row([
                ft.ElevatedButton("BAN", bgcolor="red", color="white"),
                ft.ElevatedButton("UNBAN", bgcolor="green", color="white"),
            ]),
            ft.ElevatedButton("SEND GLOBAL NOTIFICATION", on_click=broadcast, width=400),
            ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_hub())
        )

ft.app(target=GhostMessenger)

