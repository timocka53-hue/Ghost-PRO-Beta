import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import base64
import random
import time
from cryptography.fernet import Fernet

# ГАРАНТИРОВАННО ПРАВИЛЬНЫЙ КЛЮЧ (32 байта base64)
# Исправляет ValueError и Incorrect padding
SAFE_KEY = base64.urlsafe_b64encode(b"GHOST_ULTIMATE_SECURE_KEY_V13_32")
cipher = Fernet(SAFE_KEY)

class GhostV13:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        
        # Настройки страницы под твой дизайн
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_full_screen = True
        
        self.init_firebase()
        self.run_system_check()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"FIREBASE_ERROR: {e}")

    def crypt(self, text, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[ENCRYPTED_SIGNAL]"

    def run_system_check(self):
        # Проверяем, залогинен ли юзер (Сохранение сессии)
        saved_tag = self.page.client_storage.get("user_tag")
        if saved_tag:
            self.user = {
                "tag": saved_tag, 
                "role": self.page.client_storage.get("user_role")
            }
            self.show_main_interface()
        else:
            self.show_auth_screen()

    def show_auth_screen(self):
        self.page.clean()
        
        # ЭФФЕКТ МАТРИЦЫ (Падающие семерки и символы)
        matrix_bg = ft.Column([
            ft.Row([
                ft.Text(random.choice("017"), color="#003300", size=12, opacity=0.3) 
                for _ in range(30)
            ], alignment="center") for _ in range(40)
        ], spacing=0)

        email = ft.TextField(
            label="EMAIL_ADDRESS", 
            border_color="#00FF00", 
            color="#00FF00",
            bgcolor="#11000000"
        )
        password = ft.TextField(
            label="ACCESS_PASSWORD", 
            password=True, 
            border_color="#00FF00", 
            color="#00FF00"
        )

        def login_action(e):
            if not email.value or not password.value: return
            
            # Твои данные для входа
            if email.value == "adminpan" and password.value == "TimaIssam2026":
                role, tag = "ADMIN", "@admin"
            else:
                role, tag = "USER", f"@{email.value.split('@')[0]}"
            
            # Сохранение сессии (Чтобы не вылетало)
            self.page.client_storage.set("user_tag", tag)
            self.page.client_storage.set("user_role", role)
            self.user = {"tag": tag, "role": role}
            
            self.show_2fa_loading()

        self.page.add(
            ft.Stack([
                matrix_bg,
                ft.Container(
                    expand=True, padding=25, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=24, weight="bold"),
                        ft.Container(
                            height=250, border=ft.border.all(1, "#00FF00"), padding=15, bgcolor="#DD000000",
                            content=ft.Column([
                                ft.Text("> LOADING MATRIX_ENGINE... OK", color="#00FF00", size=12),
                                ft.Text("> SECURE_TUNNEL: ACTIVE", color="#00FF00", size=12),
                                ft.Text("> AUTO_WIPE_12H: ENABLED", color="#00FF00", size=12),
                                ft.Divider(color="#00FF00"),
                                ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ])
                        ),
                        email, password,
                        ft.ElevatedButton("REGISTRATION", on_click=login_action, bgcolor="#00FF00", color="black", width=400, height=50),
                        ft.ElevatedButton("LOG_IN", on_click=login_action, bgcolor="#00FF00", color="black", width=400, height=50),
                    ], horizontal_alignment="center", spacing=15)
                )
            ])
        )

    def show_2fa_loading(self):
        self.page.clean()
        pb = ft.ProgressBar(width=300, color="#00FF00", bgcolor="#002200")
        self.page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("SYNCHRONIZING 2FA...", color="#00FF00", size=20),
                    pb,
                    ft.Text("DECRYPTING NODES...", color="#00FF00", size=10, opacity=0.5)
                ], horizontal_alignment="center", spacing=20)
            )
        )
        time.sleep(2) # Имитация взлома
        self.show_main_interface()

    def show_main_interface(self):
        self.page.clean()
        self.chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
        msg_input = ft.TextField(hint_text="Enter signal...", expand=True, border_color="#1A1A1A")

        def send_signal(e):
            if msg_input.value:
                # Отправка в Firebase
                self.db.collection("ghost_v13").add({
                    "u": self.user["tag"],
                    "m": self.crypt(msg_input.value, "e"),
                    "r": self.user["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.clean_old_data() # Очистка 12ч при каждом сообщении
                self.page.update()

        # Слушатель базы (Real-time)
        self.db.collection("ghost_v13").order_by("ts", direction="descending").limit(40).on_snapshot(self.update_chat)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_CORE: {self.user['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user["role"]=="ADMIN"), on_click=lambda _: self.show_admin_panel()),
                    ft.IconButton(ft.icons.LOGOUT, on_click=self.logout)
                ]
            ),
            ft.Container(content=self.chat_messages, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_signal)
                ])
            )
        )

    def update_chat(self, docs, changes, read_time):
        self.chat_messages.controls.clear()
        for doc in reversed(list(docs)):
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_messages.controls.append(
                ft.Container(
                    padding=12, border_radius=10, bgcolor="#0A0A0A",
                    border=ft.border.all(1, "#00FF00" if is_admin else "#151515"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                        ft.Text(self.crypt(d.get("m"), "d"), size=14, color="white")
                    ])
                )
            )
        self.page.update()

    def clean_old_data(self):
        # Авто-удаление сообщений старше 12 часов
        now = datetime.datetime.now(datetime.timezone.utc)
        limit = now - datetime.timedelta(hours=12)
        old_docs = self.db.collection("ghost_v13").where("ts", "<", limit).get()
        for doc in old_docs: doc.reference.delete()

    def show_admin_panel(self):
        self.page.clean()
        broadcast = ft.TextField(label="GLOBAL_OVERRIDE", border_color="red")
        
        def push_system(e):
            self.db.collection("ghost_v13").add({
                "u": "[ROOT_SYSTEM]", "m": self.crypt(broadcast.value, "e"),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "t": "NOW"
            })
            broadcast.value = ""
            self.show_main_interface()

        self.page.add(
            ft.AppBar(title=ft.Text("ADMIN_OVERRIDE"), bgcolor="#330000"),
            ft.Column([
                ft.Text("SYSTEM CONTROL UNIT", color="red", size=22, weight="bold"),
                broadcast,
                ft.ElevatedButton("EXECUTE BROADCAST", on_click=push_system, bgcolor="red", color="white", width=400),
                ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_interface(), width=400)
            ], padding=20, spacing=20)
        )

    def logout(self, e):
        self.page.client_storage.clear()
        self.show_auth_screen()

if __name__ == "__main__":
    ft.app(target=GhostV13)

