import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
from cryptography.fernet import Fernet

# Твой ключ (храни в секрете!)
cipher = Fernet(b'GHOST_FINAL_STABLE_KEY_2026_PRO_V13_SECURE_TOKEN==')

class GhostUltimate:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user_tag = "@ghost"
        self.is_admin = False
        
        # Дизайн из твоего скриншота
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.padding = 0
        
        self.init_system()
        self.show_auth()

    def init_system(self):
        try:
            if not firebase_admin._apps:
                # Используем данные из твоего google-services.json
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
        except: pass

    # --- УВЕДОМЛЕНИЯ ---
    def send_notification(self, title, message):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color="#00FF00"),
                ft.Text(f"{title}: {message}", color="#00FF00")
            ]),
            bgcolor="#080808",
            border=ft.border.all(1, "#00FF00")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- ШИФРОВАНИЕ ---
    def safe_data(self, text, op="e"):
        try:
            if op == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "DATA_CORRUPTED"

    # --- ИНТЕРФЕЙС АВТОРИЗАЦИИ (КАК НА СКРИНШОТЕ) ---
    def show_auth(self):
        self.page.clean()
        
        email = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def do_login(e):
            if email.value == "admin" and password.value == "TimaIssam2026":
                self.is_admin = True
                self.user_tag = "@ADMIN"
            else:
                self.user_tag = f"@{email.value.split('@')[0]}"
            
            self.send_notification("SYSTEM", "IDENTITY_VERIFIED")
            self.show_messenger()

        self.page.add(
            ft.Container(
                expand=True,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=20, weight="bold"),
                    ft.Container(
                        height=300, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16)
                    ),
                    email, password,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#77FF77", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=do_login, bgcolor="#77FF77", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=10),
                padding=20
            )
        )

    # --- ГЛАВНЫЙ МЕССЕНДЖЕР ---
    def show_messenger(self):
        self.page.clean()
        self.chat = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_in = ft.TextField(hint_text="Type encrypted message...", expand=True, border_color="#111111")

        def send(e):
            if msg_in.value:
                self.db.collection("messages").add({
                    "u": self.user_tag, "m": self.safe_data(msg_in.value),
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                self.page.update()

        # Слушаем базу в реальном времени
        self.db.collection("messages").order_by("ts").on_snapshot(self.on_msg)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_PRO: {self.user_tag}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=self.is_admin, on_click=lambda _: self.show_admin()),
                    ft.IconButton(ft.icons.PERSON_OUTLINED, on_click=lambda _: self.show_profile())
                ]
            ),
            ft.Container(content=self.chat, expand=True, padding=10),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00"),
                    msg_in,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send)
                ])
            )
        )

    def on_msg(self, docs, changes, read_time):
        self.chat.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            self.chat.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(m.get("u"), color="#00FF00", size=10),
                        ft.Text(self.safe_data(m.get("m"), "d"), size=16)
                    ]),
                    padding=10, bgcolor="#111111", border_radius=10
                )
            )
        # Если пришло новое сообщение - шлем уведомление
        if changes: self.send_notification("NEW_MESSAGE", "Encrypted data received")
        self.page.update()

    def show_admin(self):
        self.page.clean()
        broadcast = ft.TextField(label="GLOBAL_BROADCAST")
        
        def send_all(e):
            self.db.collection("messages").add({
                "u": "[SYSTEM]", "m": self.safe_data(broadcast.value),
                "ts": firestore.SERVER_TIMESTAMP, "t": "NOW"
            })
            self.send_notification("ADMIN", "Broadcast sent")

        self.page.add(
            ft.Text("ROOT_ACCESS", color="red", size=25),
            broadcast,
            ft.ElevatedButton("SEND_TO_ALL_USERS", on_click=send_all, bgcolor="red", color="white", width=400),
            ft.ElevatedButton("BACK", on_click=lambda _: self.show_messenger())
        )

    def show_profile(self):
        self.page.clean()
        self.page.add(
            ft.Text("USER_PROFILE", color="#00FF00", size=25),
            ft.CircleAvatar(radius=50, content=ft.Icon(ft.icons.PERSON)),
            ft.Text(f"TAG: {self.user_tag}"),
            ft.ElevatedButton("BACK", on_click=lambda _: self.show_messenger())
        )

ft.app(target=GhostUltimate)

