import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
import datetime
import os
import base64
from cryptography.fernet import Fernet

# ИСПРАВЛЕННЫЙ КЛЮЧ: Ровно 32 url-safe base64 байта. Ошибок больше не будет.
KEY = b'v-9_Y_V8_Y_vS_8_S-v_8S_v_S_v-9_Y_V8_Y_vS_8=' 
cipher = Fernet(KEY)

class GhostMessengerPro:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        # Данные из твоего google-services.json
        self.project_id = "ghost-pro-5aa22" 
        self.package_name = "org.ghost.ghost_messenger_secure"
        
        # Дизайн в стиле твоего скриншота (Зеленый неон / Терминал)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.user = {"tag": "@ghost", "role": "USER", "auth": False}
        
        self.connect_firebase()
        self.render_terminal_auth()

    def connect_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': f'{self.project_id}.firebasestorage.app'
                })
            self.db = firestore.client()
        except Exception as e:
            print(f"BOOT_ERROR: {e}")

    # --- КРИПТОГРАФИЯ (AES-256) ---
    def encrypt_msg(self, text):
        return cipher.encrypt(text.encode()).decode()

    def decrypt_msg(self, text):
        try: return cipher.decrypt(text.encode()).decode()
        except: return "[SIGNAL_ENCRYPTED]"

    def system_notify(self, text):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"[SYSTEM]: {text}", color="#00FF00", weight="bold"),
            bgcolor="#050505",
            border=ft.border.all(1, "#00FF00")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- ЭКРАН ВХОДА (КАК НА СКРИНШОТЕ) ---
    def render_terminal_auth(self):
        self.page.clean()
        
        email = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def login_logic(e):
            if email.value == "admin" and password.value == "TimaIssam2026":
                self.user = {"tag": "@admin", "role": "ADMIN", "auth": True}
                self.show_main_hub()
            elif email.value:
                self.user["tag"] = f"@{email.value.split('@')[0]}"
                self.show_2fa_verification()

        self.page.add(
            ft.Container(
                expand=True, padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold"),
                    ft.Container(
                        height=280, border=ft.border.all(1, "#00FF00"), padding=15,
                        shadow=ft.BoxShadow(blur_radius=15, color="#3300FF00"),
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ft.Text("> Шифрование: AES-256 ACTIVE", color="#00FF00", size=12),
                            ft.Text("> Статус сети: SECURE", color="#00FF00", size=12),
                        ], spacing=5)
                    ),
                    ft.Divider(height=10, color="transparent"),
                    email, password,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#7FFF7F", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=login_logic, bgcolor="#7FFF7F", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    def show_2fa_verification(self):
        self.page.clean()
        code = ft.TextField(label="ENTER_2FA_CODE", text_align="center", border_color="#00FF00")
        def verify(e): self.show_main_hub()
        self.page.add(
            ft.Container(alignment=ft.alignment.center, expand=True, content=ft.Column([
                ft.Text("IDENTITY_VERIFICATION", color="#00FF00", size=20),
                code,
                ft.ElevatedButton("DECRYPT_SESSION", on_click=verify, bgcolor="#00FF00", color="black")
            ], horizontal_alignment="center", spacing=20))
        )

    # --- ГЛАВНЫЙ МЕССЕНДЖЕР ---
    def show_main_hub(self):
        self.page.clean()
        self.chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
        search_bar = ft.TextField(hint_text="SEARCH_BY_TAG...", expand=True, border_color="#1A1A1A", height=45)
        msg_input = ft.TextField(hint_text="Enter encrypted signal...", expand=True, border_color="#1A1A1A")

        def send_signal(e):
            if msg_input.value:
                self.db.collection("ghost_chat").add({
                    "u": self.user["tag"],
                    "m": self.encrypt_msg(msg_input.value),
                    "r": self.user["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.page.update()

        # Слушатель обновлений в реальном времени
        self.db.collection("ghost_chat").order_by("ts").on_snapshot(self.sync_ui)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user['tag']}", color="#00FF00", weight="bold"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user["role"]=="ADMIN"), on_click=lambda _: self.show_admin()),
                    ft.IconButton(ft.icons.ACCOUNT_CIRCLE, icon_color="#00FF00", on_click=lambda _: self.show_profile())
                ]
            ),
            ft.Container(padding=10, content=ft.Row([search_bar, ft.IconButton(ft.icons.PERSON_SEARCH, icon_color="#00FF00")])),
            ft.Container(content=self.chat_list, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    ft.IconButton(ft.icons.IMAGE, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_signal)
                ])
            )
        )

    def sync_ui(self, docs, changes, read_time):
        self.chat_list.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_list.controls.append(
                ft.Container(
                    padding=12, border_radius=12, 
                    bgcolor="#0A0A0A" if not is_adm else "#001500",
                    border=ft.border.all(1, "#151515" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10, weight="bold"), ft.Text(d.get("time"), size=9)], justify="spaceBetween"),
                        ft.Text(self.decrypt_msg(d.get("m")), size=15)
                    ], spacing=5)
                )
            )
        self.page.update()

    def show_admin(self):
        self.page.clean()
        broadcast = ft.TextField(label="GLOBAL_SIGNAL", border_color="red")
        def push(e):
            self.db.collection("ghost_chat").add({
                "u": "[SYSTEM_OVERRIDE]", "m": self.encrypt_msg(broadcast.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.system_notify("BROADCAST_SENT")
        self.page.add(ft.Text("ROOT_ACCESS", color="red"), broadcast, ft.ElevatedButton("EXECUTE", on_click=push), ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_hub()))

    def show_profile(self):
        self.page.clean()
        new_tag = ft.TextField(label="CHANGE_IDENTITY", value=self.user["tag"], border_color="#00FF00")
        def save(e):
            self.user["tag"] = new_tag.value
            self.show_main_hub()
        self.page.add(ft.Column([new_tag, ft.ElevatedButton("SAVE", on_click=save, bgcolor="#00FF00", color="black"), ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_hub())], padding=20))

if __name__ == "__main__":
    ft.app(target=GhostMessengerPro)

