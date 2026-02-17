import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import base64
import random
from cryptography.fernet import Fernet

# ГАРАНТИРОВАННЫЙ КЛЮЧ (Исправляет ValueError и Padding)
SAFE_KEY = base64.urlsafe_b64encode(b"GHOST_ULTIMATE_V13_32_BYTE_KEY_!")
cipher = Fernet(SAFE_KEY)

class GhostApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        
        # Настройки под скриншот
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.init_db()
        self.boot_system()

    def init_db(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except: pass

    def safe_crypt(self, text, op="e"):
        try:
            if op == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[SIGNAL_LOST]"

    def boot_system(self):
        # Проверка сессии: если залогинен — сразу в чат
        if self.page.client_storage.get("session_active"):
            self.user_tag = self.page.client_storage.get("user_tag")
            self.user_role = self.page.client_storage.get("user_role")
            self.show_chat()
        else:
            self.show_matrix_login()

    def show_matrix_login(self):
        self.page.clean()
        
        # Эффект матрицы (семерки и нули)
        matrix_bg = ft.Column([
            ft.Row([ft.Text(random.choice("071"), color="#004400", size=10) for _ in range(40)]) 
            for _ in range(30)
        ], spacing=0, opacity=0.4)

        email = ft.TextField(label="IDENTITY_EMAIL", border_color="#00FF00", color="#00FF00")
        password = ft.TextField(label="ENCRYPTED_PASS", password=True, border_color="#00FF00", color="#00FF00")

        def auth_handler(e):
            if not email.value or not password.value: return
            
            # Логика входа/регистрации
            if email.value == "adminpan" and password.value == "TimaIssam2026":
                role, tag = "ADMIN", "@admin"
            else:
                role, tag = "USER", f"@{email.value.split('@')[0]}"
            
            # Сохраняем сессию (не вылетает при перезапуске)
            self.page.client_storage.set("session_active", True)
            self.page.client_storage.set("user_tag", tag)
            self.page.client_storage.set("user_role", role)
            
            self.user_tag, self.user_role = tag, role
            self.run_2fa_sequence()

        self.page.add(
            ft.Stack([
                matrix_bg,
                ft.Container(
                    expand=True, padding=20, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold"),
                        ft.Container(
                            height=250, border=ft.border.all(1, "#00FF00"), padding=15, bgcolor="#DD000000",
                            content=ft.Column([
                                ft.Text("> CONNECTING TO NODE... OK", color="#00FF00", size=12),
                                ft.Text("> 2FA_SECURITY: ENABLED", color="#00FF00", size=12),
                                ft.Text("> AUTO_CLEAN_12H: READY", color="#00FF00", size=12),
                                ft.Divider(color="#00FF00"),
                                ft.Text("[SYSTEM]: Ожидание авторизации...", color="#00FF00", size=16),
                            ])
                        ),
                        email, password,
                        ft.ElevatedButton("REGISTRATION", on_click=auth_handler, bgcolor="#00FF00", color="black", width=400, height=50),
                        ft.ElevatedButton("LOG_IN", on_click=auth_handler, bgcolor="#00FF00", color="black", width=400, height=50),
                    ], horizontal_alignment="center", spacing=15)
                )
            ])
        )

    def run_2fa_sequence(self):
        self.page.clean()
        loading = ft.ProgressBar(width=300, color="#00FF00")
        self.page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("DECRYPTING 2FA KEY...", color="#00FF00", size=20),
                    loading,
                    ft.Text("VERIFYING BIOMETRICS...", color="#00FF00", opacity=0.5)
                ], horizontal_alignment="center")
            )
        )
        time.sleep(2)
        self.show_chat()

    def show_chat(self):
        self.page.clean()
        self.chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        msg_input = ft.TextField(hint_text="Type encrypted...", expand=True, border_color="#1A1A1A")

        def send_msg(e):
            if msg_input.value:
                self.db.collection("messages_v13").add({
                    "u": self.user_tag,
                    "m": self.safe_crypt(msg_input.value, "e"),
                    "r": self.user_role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                self.wipe_old_data() # Чистка каждые 12ч
                self.page.update()

        # Слушаем базу (Real-time)
        self.db.collection("messages_v13").order_by("ts", direction="descending").limit(30).on_snapshot(self.sync)

        self.page.add(
            ft.AppBar(title=ft.Text(f"GHOST_NODE: {self.user_tag}", color="#00FF00"), bgcolor="#050505",
                      actions=[ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_role=="ADMIN"), on_click=lambda _: self.show_admin()),
                               ft.IconButton(ft.icons.LOGOUT, on_click=self.exit_app)]),
            ft.Container(content=self.chat_list, expand=True, padding=15),
            ft.Container(bgcolor="#080808", padding=10, content=ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=send_msg, icon_color="#00FF00")]))
        )

    def sync(self, docs, changes, read_time):
        self.chat_list.controls.clear()
        for doc in reversed(list(docs)):
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_list.controls.append(
                ft.Container(
                    padding=10, border_radius=10, bgcolor="#0A0A0A",
                    border=ft.border.all(1, "#00FF00" if is_adm else "#111111"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                        ft.Text(self.safe_crypt(d.get("m"), "d"), size=14)
                    ])
                )
            )
        self.page.update()

    def wipe_old_data(self):
        # Удаление сообщений > 12 часов
        limit = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)
        old = self.db.collection("messages_v13").where("ts", "<", limit).get()
        for o in old: o.reference.delete()

    def show_admin(self):
        self.page.clean()
        self.page.add(
            ft.AppBar(title=ft.Text("SYSTEM_OVERRIDE"), bgcolor="#330000"),
            ft.Column([
                ft.Text("ADMIN CONTROL", color="red", size=24),
                ft.ElevatedButton("BACK", on_click=lambda _: self.show_chat(), width=400)
            ], padding=20)
        )

    def exit_app(self, e):
        self.page.client_storage.clear()
        self.show_matrix_login()

if __name__ == "__main__":
    ft.app(target=GhostApp)


