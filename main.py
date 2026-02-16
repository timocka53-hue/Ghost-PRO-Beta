import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
from cryptography.fernet import Fernet

# Ключ для шифрования (AES)
KEY = b'GHOST_ULTIMATE_SECURE_2026_V13_LONG_KEY_PRO_99=='
cipher = Fernet(KEY)

class GhostMessenger:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user = {"tag": "@ghost", "role": "USER", "auth": False}
        
        # Визуальные настройки как на скриншоте
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        
        self.init_firebase()
        self.show_auth()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
        except: pass

    def crypt(self, t, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(t.encode()).decode()
            return cipher.decrypt(t.encode()).decode()
        except: return "DATA_LOCKED"

    def notify(self, txt):
        self.page.snack_bar = ft.SnackBar(ft.Text(txt, color="#00FF00"), bgcolor="#080808")
        self.page.snack_bar.open = True
        self.page.update()

    # --- ТЕРМИНАЛЬНЫЙ ЭКРАН ВХОДА ---
    def show_auth(self):
        self.page.clean()
        
        email = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def login_trigger(e):
            if email.value == "admin" and password.value == "TimaIssam2026":
                self.user = {"tag": "@admin", "role": "ADMIN", "auth": True}
                self.show_chat()
            elif email.value:
                self.user = {"tag": f"@{email.value.split('@')[0]}", "role": "USER", "auth": True}
                self.show_chat()

        self.page.add(
            ft.Container(
                expand=True, padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=20, weight="bold"),
                    ft.Container(
                        height=280, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00"),
                            ft.Text("> Шифрование: ACTIVE", color="#00FF00", size=12),
                            ft.Text("> Канал связи: SECURE", color="#00FF00", size=12),
                        ])
                    ),
                    email, password,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#7FFF7F", color="black", width=400, height=45),
                    ft.ElevatedButton("LOG_IN", on_click=login_trigger, bgcolor="#7FFF7F", color="black", width=400, height=45),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    # --- ЭКРАН МЕССЕНДЖЕРА ---
    def show_chat(self):
        self.page.clean()
        self.messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_input = ft.TextField(hint_text="Type encrypted signal...", expand=True, border_color="#1A1A1A")

        def send_logic(e):
            if msg_input.value:
                self.db.collection("global_chat").add({
                    "u": self.user["tag"],
                    "m": self.crypt(msg_input.value),
                    "r": self.user["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.page.update()

        # Слушаем Firebase
        self.db.collection("global_chat").order_by("ts").on_snapshot(self.update_ui)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user["role"]=="ADMIN"), on_click=lambda _: self.show_admin()),
                    ft.IconButton(ft.icons.SETTINGS, on_click=lambda _: self.show_profile())
                ]
            ),
            ft.Container(content=self.messages, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_logic)
                ])
            )
        )

    def update_ui(self, docs, changes, read_time):
        self.messages.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.messages.controls.append(
                ft.Container(
                    padding=10, border_radius=10, 
                    bgcolor="#111111" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#222222" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                        ft.Text(self.crypt(d.get("m"), "d"), size=14)
                    ])
                )
            )
        self.page.update()

    def show_admin(self):
        self.page.clean()
        broadcast = ft.TextField(label="SYSTEM_WIDE_MESSAGE", border_color="red")
        
        def push(e):
            self.db.collection("global_chat").add({
                "u": "[SYSTEM]", "m": self.crypt(broadcast.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "t": "NOW"
            })
            self.notify("Global broadcast sent")

        self.page.add(
            ft.Text("ROOT_OVERRIDE", color="red", size=20),
            broadcast,
            ft.ElevatedButton("EXECUTE", on_click=push, bgcolor="red"),
            ft.ElevatedButton("BACK", on_click=lambda _: self.show_chat())
        )

    def show_profile(self):
        self.page.clean()
        new_tag = ft.TextField(label="CHANGE_TAG", value=self.user["tag"])
        def save(e):
            self.user["tag"] = new_tag.value
            self.show_chat()
        self.page.add(new_tag, ft.ElevatedButton("SAVE", on_click=save), ft.ElevatedButton("BACK", on_click=lambda _: self.show_chat()))

if __name__ == "__main__":
    ft.app(target=GhostMessenger)
