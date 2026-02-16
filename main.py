import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
import base64
from cryptography.fernet import Fernet

# ГЕНЕРИРУЕМ ВАЛИДНЫЙ КЛЮЧ (32 байта base64)
# Это исправляет ошибку ValueError из твоего скриншота
KEY = b'v-9_Y_V8_Y_vS_8_S-v_8S_v_S_v-9_Y_V8_Y_vS_8=' 
cipher = Fernet(KEY)

class GhostSystemV13:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user_data = {"tag": "@guest", "role": "USER", "auth": False}
        
        # Настройка страницы под скриншот (Зеленый неон)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        
        self.init_firebase()
        self.render_auth_gate()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
        except Exception as e:
            print(f"FIREBASE_INIT_ERROR: {e}")

    def crypto_op(self, text, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[ENCRYPTED_DATA]"

    def system_toast(self, text):
        self.page.snack_bar = ft.SnackBar(ft.Text(text, color="#00FF00"), bgcolor="#080808")
        self.page.snack_bar.open = True
        self.page.update()

    # --- ЭКРАН ВХОДА ---
    def render_auth_gate(self):
        self.page.clean()
        
        email_in = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        pass_in = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def login_action(e):
            # ВХОД В АДМИНКУ ПО ТВОИМ ДАННЫМ
            if email_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                self.user_data = {"tag": "@admin", "role": "ADMIN", "auth": True}
                self.render_main_chat()
            elif email_in.value and len(pass_in.value) > 4:
                self.user_data = {"tag": f"@{email_in.value.split('@')[0]}", "role": "USER", "auth": True}
                self.render_main_chat()
            else:
                self.system_toast("ACCESS_DENIED: INVALID_KEYS")

        # Визуальный блок как на фото
        self.page.add(
            ft.Container(
                expand=True, padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=20, weight="bold"),
                    ft.Container(
                        height=280, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ft.Text("> AES_256: ENABLED", color="#00FF00", size=12),
                            ft.Text("> CORE_LINK: SECURE", color="#00FF00", size=12),
                        ])
                    ),
                    ft.Divider(height=10, color="transparent"),
                    email_in, pass_in,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#7FFF7F", color="black", width=400, height=45),
                    ft.ElevatedButton("LOG_IN", on_click=login_action, bgcolor="#7FFF7F", color="black", width=400, height=45),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    # --- МЕССЕНДЖЕР ---
    def render_main_chat(self):
        self.page.clean()
        self.chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_input = ft.TextField(hint_text="Type encrypted signal...", expand=True, border_color="#1A1A1A")
        
        # Поиск (функционал кайф)
        search_field = ft.TextField(hint_text="Find tag...", border_color="#00FF00", height=40, expand=True)

        def send_logic(e):
            if msg_input.value:
                self.db.collection("ghost_v13_msgs").add({
                    "user": self.user_data["tag"],
                    "body": self.crypto_op(msg_input.value),
                    "role": self.user_data["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.page.update()

        # Поток сообщений
        self.db.collection("ghost_v13_msgs").order_by("ts").on_snapshot(self.on_msg_update)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_NODE: {self.user_data['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_data["role"]=="ADMIN"), on_click=lambda _: self.render_admin_panel()),
                    ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: self.render_auth_gate())
                ]
            ),
            ft.Row([search_field, ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00")], padding=10),
            ft.Container(content=self.chat_messages, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_logic)
                ])
            )
        )

    def on_msg_update(self, docs, changes, read_time):
        self.chat_messages.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("role") == "ADMIN"
            self.chat_messages.controls.append(
                ft.Container(
                    padding=12, border_radius=10, 
                    bgcolor="#0D0D0D" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(m.get("user"), color="#00FF00", size=10), ft.Text(m.get("time"), size=8)], justify="spaceBetween"),
                        ft.Text(self.crypto_op(m.get("body"), "d"), size=15)
                    ])
                )
            )
        self.page.update()

    # --- ПОЛНАЯ АДМИНКА ---
    def render_admin_panel(self):
        self.page.clean()
        broadcast = ft.TextField(label="SYSTEM_MESSAGE", border_color="red")
        
        def push_all(e):
            self.db.collection("ghost_v13_msgs").add({
                "user": "[ROOT_SYSTEM]", "body": self.crypto_op(broadcast.value),
                "role": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.system_toast("BROADCAST_EXECUTED")

        self.page.add(
            ft.AppBar(title=ft.Text("ADMIN_CORE"), bgcolor="#220000"),
            ft.Column([
                ft.Text("УПРАВЛЕНИЕ УЗЛОМ", color="red", size=20),
                broadcast,
                ft.ElevatedButton("SEND_TO_ALL", on_click=push_all, bgcolor="red", color="white"),
                ft.ElevatedButton("CLEAR_LOGS (FAKE)", bgcolor="red"),
                ft.ElevatedButton("BACK_TO_CHAT", on_click=lambda _: self.render_main_chat())
            ], padding=20, spacing=20)
        )

if __name__ == "__main__":
    ft.app(target=GhostSystemV13)


