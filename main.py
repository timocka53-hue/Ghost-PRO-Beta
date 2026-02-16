import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
from cryptography.fernet import Fernet

# Твой уникальный ключ для шифрования (сохрани его)
CRYPTO_KEY = b'GHOST_ULTIMATE_V13_SECURE_AES_NON_BREACHABLE_KEY=='
cipher = Fernet(CRYPTO_KEY)

class GhostApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user_session = {"tag": "@ghost", "role": "USER", "auth": False}
        
        # Настройка страницы (дизайн как на фото)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        
        self.init_firebase()
        self.render_auth()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                # Используем данные из твоего google-services.json
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
        except Exception as e:
            print(f"ERROR: {e}")

    def encrypt(self, text):
        return cipher.encrypt(text.encode()).decode()

    def decrypt(self, text):
        try: return cipher.decrypt(text.encode()).decode()
        except: return "[ENCRYPTED_DATA]"

    def send_system_notify(self, title, body):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{title.upper()}: {body}", color="#00FF00"),
            bgcolor="#050505",
            border=ft.border.all(1, "#00FF00")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- ИНТЕРФЕЙС АВТОРИЗАЦИИ (КАК НА СКРИНШОТЕ) ---
    def render_auth(self):
        self.page.clean()
        
        email_f = ft.TextField(
            label="EMAIL_ADDRESS", 
            border_color="#00FF00", 
            color="#00FF00",
            focused_border_color="#00FF00"
        )
        pass_f = ft.TextField(
            label="ACCESS_PASSWORD", 
            password=True, 
            border_color="#00FF00",
            color="#00FF00",
            focused_border_color="#00FF00"
        )

        def login_logic(e):
            # Вход админа
            if email_f.value == "admin" and pass_f.value == "TimaIssam2026":
                self.user_session = {"tag": "@admin", "role": "ADMIN", "auth": True}
                self.render_messenger()
            elif email_f.value:
                # Обычный вход (тут можно добавить проверку Firebase Auth)
                self.user_session = {"tag": f"@{email_f.value.split('@')[0]}", "role": "USER", "auth": True}
                self.render_messenger()
            else:
                self.send_system_notify("error", "invalid credentials")

        # Основной контейнер дизайна
        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=18, weight="bold"),
                    ft.Container(
                        height=280, 
                        border=ft.border.all(1, "#00FF00"), 
                        padding=15,
                        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#2200FF00"),
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00"),
                            ft.Text("> Шифрование: AES-256 ACTIVE", color="#00FF00", size=12),
                            ft.Text("> База данных: CONNECTED", color="#00FF00", size=12),
                            ft.Text("> Регион: ENCRYPTED", color="#00FF00", size=12),
                        ], spacing=5)
                    ),
                    ft.Divider(height=10, color="transparent"),
                    email_f,
                    pass_f,
                    ft.ElevatedButton(
                        "REGISTRATION", 
                        bgcolor="#7FFF7F", 
                        color="black", 
                        width=400, 
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                    ),
                    ft.ElevatedButton(
                        "LOG_IN", 
                        on_click=login_logic,
                        bgcolor="#7FFF7F", 
                        color="black", 
                        width=400, 
                        height=50,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))
                    ),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    # --- ОСНОВНОЙ МЕССЕНДЖЕР ---
    def render_messenger(self):
        self.page.clean()
        self.chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
        input_msg = ft.TextField(hint_text="Type message...", expand=True, border_color="#1A1A1A")

        def send_message(e):
            if input_msg.value and self.db:
                self.db.collection("ghost_chat").add({
                    "u": self.user_session["tag"],
                    "m": self.encrypt(input_msg.value),
                    "r": self.user_session["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                input_msg.value = ""
                self.page.update()

        # Слушаем базу
        if self.db:
            self.db.collection("ghost_chat").order_by("ts").on_snapshot(self.on_db_change)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_NET: {self.user_session['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_session["role"]=="ADMIN"), on_click=lambda _: self.render_admin()),
                    ft.IconButton(ft.icons.PERSON, on_click=lambda _: self.render_profile())
                ]
            ),
            ft.Container(content=self.chat_list, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00"),
                    input_msg,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_message)
                ])
            )
        )

    def on_db_change(self, docs, changes, read_time):
        self.chat_list.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_list.controls.append(
                ft.Container(
                    padding=12, border_radius=15, 
                    bgcolor="#111111" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#222222" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=11), ft.Text(d.get("time"), size=9)], justify="spaceBetween"),
                        ft.Text(self.decrypt(d.get("m")), size=15)
                    ], spacing=5)
                )
            )
        self.page.update()

    def render_profile(self):
        self.page.clean()
        self.page.add(
            ft.Text("IDENTITY_MODULE", color="#00FF00", size=25),
            ft.Divider(color="#00FF00"),
            ft.Text(f"TAG: {self.user_session['tag']}"),
            ft.Text(f"LEVEL: {self.user_session['role']}"),
            ft.ElevatedButton("BACK_TO_CORE", on_click=lambda _: self.render_messenger())
        )

    def render_admin(self):
        self.page.clean()
        broadcast = ft.TextField(label="GLOBAL_BROADCAST", border_color="red")
        
        def push_all(e):
            self.db.collection("ghost_chat").add({
                "u": "[SYSTEM]", "m": self.encrypt(broadcast.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.send_system_notify("admin", "broadcast sent")

        self.page.add(
            ft.Text("ROOT_ACCESS", color="red", size=25),
            broadcast,
            ft.ElevatedButton("EXECUTE_PUSH", on_click=push_all, bgcolor="red"),
            ft.ElevatedButton("BACK", on_click=lambda _: self.render_messenger())
        )

if __name__ == "__main__":
    ft.app(target=GhostApp)


 
