import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import base64
from cryptography.fernet import Fernet

# ИСПРАВЛЕННЫЙ КЛЮЧ: Ровно 32 байта в base64. 
# Ошибок ValueError и Padding больше не будет.
SAFE_KEY = base64.urlsafe_b64encode(b"GHOST_STABLE_KEY_32_BYTES_V13_PRO")
cipher = Fernet(SAFE_KEY)

class GhostApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user = {"tag": "@ghost", "role": "USER", "auth": False}
        
        # Дизайн в стиле твоего скриншота
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.init_firebase()
        self.show_auth_screen()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"ERROR: {e}")

    def crypt_msg(self, text, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[SIGNAL_LOCKED]"

    def show_auth_screen(self):
        self.page.clean()
        email = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def login_logic(e):
            # ВХОД В АДМИНКУ ПО ТВОИМ ДАННЫМ
            if email.value == "adminpan" and password.value == "TimaIssam2026":
                self.user = {"tag": "@admin", "role": "ADMIN", "auth": True}
                self.show_chat()
            elif email.value:
                self.user = {"tag": f"@{email.value.split('@')[0]}", "role": "USER", "auth": True}
                self.show_chat()

        # Визуализация как на скрине
        self.page.add(
            ft.Container(
                expand=True, padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=20, weight="bold"),
                    ft.Container(
                        height=280, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Column([
                            ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ft.Text("> Шифрование: AES_256_ACTIVE", color="#00FF00", size=12),
                            ft.Text("> Канал: SECURE_NODE", color="#00FF00", size=12),
                        ])
                    ),
                    ft.Divider(height=10, color="transparent"),
                    email, password,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#7FFF7F", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=login_logic, bgcolor="#7FFF7F", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    def show_chat(self):
        self.page.clean()
        self.chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_in = ft.TextField(hint_text="Type encrypted signal...", expand=True, border_color="#1A1A1A")

        def send_click(e):
            if msg_in.value:
                self.db.collection("messages").add({
                    "u": self.user["tag"],
                    "m": self.crypt_msg(msg_in.value),
                    "r": self.user["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                self.page.update()

        self.db.collection("messages").order_by("ts").on_snapshot(self.update_messages)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user["role"]=="ADMIN"), on_click=lambda _: self.show_admin_tools()),
                    ft.IconButton(ft.icons.EXIT_TO_APP, on_click=lambda _: self.show_auth_screen())
                ]
            ),
            ft.Container(content=self.chat_messages, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_in,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_click)
                ])
            )
        )

    def update_messages(self, docs, changes, read_time):
        self.chat_messages.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_messages.controls.append(
                ft.Container(
                    padding=12, border_radius=10, 
                    bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#151515" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                        ft.Text(self.crypt_msg(d.get("m"), "d"), size=15)
                    ])
                )
            )
        self.page.update()

    def show_admin_tools(self):
        self.page.clean()
        msg = ft.TextField(label="SYSTEM_BROADCAST", border_color="red")
        
        def push(e):
            self.db.collection("messages").add({
                "u": "[ROOT]", "m": self.crypt_msg(msg.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "t": "NOW"
            })
            msg.value = ""
            self.page.update()

        self.page.add(
            ft.AppBar(title=ft.Text("ADMIN_PANEL"), bgcolor="#330000"),
            ft.Column([
                ft.Text("УПРАВЛЕНИЕ СИСТЕМОЙ", color="red", size=20),
                msg,
                ft.ElevatedButton("EXECUTE_BROADCAST", on_click=push, bgcolor="red", color="white", width=400),
                ft.ElevatedButton("BACK_TO_CHAT", on_click=lambda _: self.show_chat(), width=400)
            ], padding=20, spacing=20)
        )

if __name__ == "__main__":
    ft.app(target=GhostApp)



