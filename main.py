import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import base64
from cryptography.fernet import Fernet

# ГЕНЕРАЦИЯ ПРАВИЛЬНОГО КЛЮЧА
# Это убирает ошибку ValueError
def get_secure_cipher():
    # Ровно 32 байта, закодированные в base64
    key = base64.urlsafe_b64encode(b"GHOST_PRO_V13_SECURE_KEY_32B_STB")
    return Fernet(key)

cipher = get_secure_cipher()

class GhostMessenger:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.user_session = {"tag": "@ghost", "role": "USER"}
        
        # Дизайн в стиле твоего скриншота
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.connect_db()
        self.render_auth()

    def connect_db(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"DATABASE_OFFLINE: {e}")

    def safe_crypt(self, text, op="e"):
        try:
            if op == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[SIGNAL_ENCRYPTED]"

    # --- ЭКРАН ВХОДА ---
    def render_auth(self):
        self.page.clean()
        email = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ACCESS_PASSWORD", password=True, border_color="#00FF00")

        def login_logic(e):
            # ТВОИ ДАННЫЕ ДЛЯ АДМИНКИ
            if email.value == "adminpan" and password.value == "TimaIssam2026":
                self.user_session = {"tag": "@admin", "role": "ADMIN"}
                self.show_main_hub()
            elif email.value:
                self.user_session["tag"] = f"@{email.value.split('@')[0]}"
                self.show_main_hub()

        # Визуал терминала
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
                        ])
                    ),
                    ft.Divider(height=10, color="transparent"),
                    email, password,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#7FFF7F", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=login_logic, bgcolor="#7FFF7F", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=10)
            )
        )

    # --- ОСНОВНОЙ ЧАТ ---
    def show_main_hub(self):
        self.page.clean()
        self.msg_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
        search_input = ft.TextField(hint_text="SEARCH_BY_TAG...", expand=True, border_color="#1A1A1A", height=45)
        msg_input = ft.TextField(hint_text="Enter encrypted signal...", expand=True, border_color="#1A1A1A")

        def send_msg(e):
            if msg_input.value:
                self.db.collection("ghost_v13").add({
                    "u": self.user_session["tag"],
                    "m": self.safe_crypt(msg_input.value),
                    "r": self.user_session["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.page.update()

        # Слушаем базу данных
        self.db.collection("ghost_v13").order_by("ts").on_snapshot(self.sync_chat)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user_session['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_session["role"]=="ADMIN"), on_click=lambda _: self.show_admin_panel()),
                    ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: self.render_auth())
                ]
            ),
            ft.Container(padding=10, content=ft.Row([search_input, ft.IconButton(ft.icons.PERSON_SEARCH, icon_color="#00FF00")])),
            ft.Container(content=self.msg_column, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
                ])
            )
        )

    def sync_chat(self, docs, changes, read_time):
        self.msg_column.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.msg_column.controls.append(
                ft.Container(
                    padding=12, border_radius=10, 
                    bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#151515" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                        ft.Text(self.safe_crypt(d.get("m"), "d"), size=15)
                    ])
                )
            )
        self.page.update()

    # --- АДМИН-ПАНЕЛЬ ---
    def show_admin_panel(self):
        self.page.clean()
        broadcast_msg = ft.TextField(label="GLOBAL_BROADCAST", border_color="red")
        
        def push_all(e):
            self.db.collection("ghost_v13").add({
                "u": "[ROOT_SYSTEM]", "m": self.safe_crypt(broadcast_msg.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "t": "NOW"
            })
            broadcast_msg.value = ""
            self.page.update()

        self.page.add(
            ft.AppBar(title=ft.Text("ROOT_OVERRIDE"), bgcolor="#330000"),
            ft.Column([
                ft.Text("УПРАВЛЕНИЕ УЗЛАМИ", color="red", size=20),
                broadcast_msg,
                ft.ElevatedButton("SEND_TO_ALL", on_click=push_all, bgcolor="red", color="white", width=400),
                ft.ElevatedButton("BACK_TO_CHAT", on_click=lambda _: self.show_main_hub(), width=400)
            ], padding=20, spacing=20)
        )

if __name__ == "__main__":
    ft.app(target=GhostMessenger)




