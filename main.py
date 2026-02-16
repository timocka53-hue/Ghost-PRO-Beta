import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import datetime
import os
import base64
from cryptography.fernet import Fernet

# Твой ключ шифрования (AES-256)
SECRET_KEY = b'GHOST_ULTIMATE_SECURE_2026_V13_LONG_KEY_PRO_99=='
cipher = Fernet(SECRET_KEY)

class GhostMessenger:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_data = {"id": None, "tag": "UNDEFINED", "role": "USER", "avatar": None}
        self.db = None
        self.bucket = None
        
        # Настройки страницы
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 400
        self.page.window_height = 800
        
        self.init_firebase()
        self.show_auth_screen()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app' # Твой бакет из JSON
                })
            self.db = firestore.client()
            self.bucket = storage.bucket()
        except Exception as e:
            print(f"CRITICAL_ERROR: {e}")

    # --- СИСТЕМА ШИФРОВАНИЯ ---
    def crypt(self, data, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(data.encode()).decode()
            return cipher.decrypt(data.encode()).decode()
        except: return "PROTOCOL_ERROR"

    # --- ЭКРАН АВТОРИЗАЦИИ ---
    def show_auth_screen(self):
        self.page.clean()
        
        email_field = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        pass_field = ft.TextField(label="ACCESS_PASSWORD", password=True, can_reveal_password=True, border_color="#00FF00")

        def login_logic(e):
            # Твой секретный вход
            if email_field.value == "admin" and pass_field.value == "TimaIssam2026":
                self.user_data = {"id": "ROOT_ADMIN", "tag": "@admin", "role": "ADMIN"}
                self.show_main_hub()
            else:
                # В реальности тут auth.get_user_by_email()
                self.user_data = {"id": email_field.value, "tag": f"@{email_field.value.split('@')[0]}", "role": "USER"}
                self.show_2fa_screen()

        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=20, weight="bold"),
                    ft.Container(
                        height=250, border=ft.border.all(1, "#00FF00"), 
                        padding=15, content=ft.Text("[SYSTEM]: Ожидание авторизации...\n> Соединение защищено\n> Шифрование активно", color="#00FF00")
                    ),
                    email_field,
                    pass_field,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#00FF00", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=login_logic, bgcolor="#00FF00", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=15)
            )
        )

    def show_2fa_screen(self):
        self.page.clean()
        code_in = ft.TextField(label="ENTER_CODE_FROM_EMAIL", border_color="#00FF00", text_align="center")
        
        def verify(e): self.show_main_hub()

        self.page.add(
            ft.Container(
                alignment=ft.alignment.center, expand=True,
                content=ft.Column([
                    ft.Text("SECURITY_CHECK", color="#00FF00", size=25),
                    code_in,
                    ft.ElevatedButton("CONFIRM_IDENTITY", on_click=verify, bgcolor="#00FF00", color="black")
                ], horizontal_alignment="center")
            )
        )

    # --- ГЛАВНЫЙ МЕССЕНДЖЕР ---
    def show_main_hub(self):
        self.page.clean()
        self.msg_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
        search_field = ft.TextField(hint_text="SEARCH_BY_USER_TAG...", expand=True, border_color="#00FF00")
        input_msg = ft.TextField(hint_text="Type message...", expand=True, border_color="#111111")

        def send_action(e):
            if input_msg.value and self.db:
                self.db.collection("global_stream").add({
                    "sender": self.user_data["tag"],
                    "content": self.crypt(input_msg.value),
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "ts": firestore.SERVER_TIMESTAMP,
                    "role": self.user_data["role"]
                })
                input_msg.value = ""
                self.page.update()

        # Слушатель базы
        if self.db:
            self.db.collection("global_stream").order_by("ts").on_snapshot(self.sync_messages)

        self.page.add(
            ft.Container(
                bgcolor="#050505", padding=10,
                content=ft.Row([
                    ft.Text("GHOST_PRO", color="#00FF00", size=20, weight="bold"),
                    ft.Row([
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(self.user_data["role"]=="ADMIN"), on_click=lambda _: self.show_admin_panel()),
                        ft.IconButton(ft.icons.PERSON, icon_color="#00FF00", on_click=lambda _: self.show_profile()),
                    ])
                ], justify="spaceBetween")
            ),
            ft.Container(padding=10, content=ft.Row([search_field, ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00")])),
            ft.Container(content=self.msg_list, expand=True, padding=10),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    ft.IconButton(ft.icons.ADD_A_PHOTO, icon_color="#00FF00"),
                    input_msg,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_action)
                ])
            )
        )

    def sync_messages(self, docs, changes, read_time):
        self.msg_list.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("role") == "ADMIN"
            self.msg_list.controls.append(
                ft.Container(
                    padding=10, border_radius=15, bgcolor="#111111" if not is_adm else "#001500",
                    border=ft.border.all(1, "#222222" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(m.get("sender"), color="#00FF00", size=11), ft.Text(m.get("time"), size=9)], justify="spaceBetween"),
                        ft.Text(self.crypt(m.get("content"), "d"), size=15)
                    ], spacing=5)
                )
            )
        self.page.update()

    # --- ПРОФИЛЬ ---
    def show_profile(self):
        self.page.clean()
        tag_input = ft.TextField(label="CHANGE_USER_TAG", value=self.user_data["tag"], border_color="#00FF00")
        
        def update_profile(e):
            self.user_data["tag"] = tag_input.value
            self.show_main_hub()

        self.page.add(
            ft.AppBar(title=ft.Text("USER_PROFILE"), bgcolor="#000000"),
            ft.Column([
                ft.Container(ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=100, color="#00FF00"), alignment=ft.alignment.center),
                tag_input,
                ft.ElevatedButton("UPDATE_IDENTITY", on_click=update_profile, bgcolor="#00FF00", color="black", width=400),
                ft.Divider(color="#222222"),
                ft.ListTile(leading=ft.Icon(ft.icons.SUPPORT_AGENT), title=ft.Text("TECH_SUPPORT"), on_click=lambda _: self.show_support()),
                ft.ElevatedButton("BACK_TO_TERMINAL", on_click=lambda _: self.show_main_hub(), width=400)
            ], spacing=20, horizontal_alignment="center")
        )

    # --- АДМИН ПАНЕЛЬ ---
    def show_admin_panel(self):
        self.page.clean()
        user_id_field = ft.TextField(label="USER_TAG_OR_ID", border_color="red")
        broadcast_field = ft.TextField(label="GLOBAL_BROADCAST_MESSAGE", multiline=True)

        def send_alert(e):
            self.db.collection("global_stream").add({
                "sender": "[SYSTEM_OVERRIDE]",
                "content": self.crypt(broadcast_field.value),
                "time": "NOW", "ts": firestore.SERVER_TIMESTAMP, "role": "ADMIN"
            })

        self.page.add(
            ft.AppBar(title=ft.Text("ADMIN_ROOT_ACCESS"), bgcolor="red"),
            ft.Column([
                user_id_field,
                ft.Row([
                    ft.ElevatedButton("BAN_USER", bgcolor="red", color="white"),
                    ft.ElevatedButton("UNFREEZE", bgcolor="green", color="white")
                ]),
                ft.Divider(),
                broadcast_field,
                ft.ElevatedButton("SEND_GLOBAL_NOTIFICATION", on_click=send_alert, width=400),
                ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_hub())
            ], padding=20)
        )

    def show_support(self):
        self.page.clean()
        desc = ft.TextField(label="DESCRIBE_ISSUE", multiline=True, border_color="#00FF00")
        def send_t(e): self.show_main_hub()
        self.page.add(ft.Column([ft.Text("OPEN_TICKET", size=20), desc, ft.ElevatedButton("SEND_TO_ADMINS", on_click=send_t)]))

if __name__ == "__main__":
    ft.app(target=GhostMessenger)
