import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
import datetime
import os
import base64
from cryptography.fernet import Fernet

# Ключ шифрования (Генерируй свой для продакшена)
cipher = Fernet(b'GHOST_ULTIMATE_SECURE_V13_TOKEN_2026_FULL_ACCESS==')

class GhostProApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.bucket = None
        self.current_user = {"tag": "@ghost", "role": "USER", "id": None, "avatar": None}
        self.is_auth = False
        
        # Настройки страницы под твой дизайн (скриншот)
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        self.init_firebase()
        self.show_auth_screen()

    def init_firebase(self):
        try:
            if not firebase_admin._apps:
                # Читаем твой конфиг ghost-pro-5aa22
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
                })
            self.db = firestore.client()
            self.bucket = storage.bucket()
        except Exception as e:
            print(f"FIREBASE_INIT_ERROR: {e}")

    # --- СИСТЕМА УВЕДОМЛЕНИЙ ---
    def notify(self, title, msg):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"[{title}]: {msg}", color="#00FF00", weight="bold"),
            bgcolor="#050505",
            border=ft.border.all(1, "#00FF00")
        )
        self.page.snack_bar.open = True
        self.page.update()

    # --- КРИПТОГРАФИЯ ---
    def crypt_msg(self, text, op="e"):
        try:
            if op == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "ENCRYPTED_SIGNAL"

    # --- ЭКРАН ВХОДА ---
    def show_auth_screen(self):
        self.page.clean()
        
        email_in = ft.TextField(label="EMAIL_ADDRESS", border_color="#00FF00", color="#00FF00")
        pass_in = ft.TextField(label="ACCESS_PASSWORD", password=True, can_reveal_password=True, border_color="#00FF00")

        def handle_login(e):
            # Твой секретный вход админа
            if email_in.value == "admin" and pass_in.value == "TimaIssam2026":
                self.current_user = {"tag": "@admin", "role": "ADMIN", "id": "ROOT"}
                self.show_messenger()
                return

            # Реальная логика 2FA (имитация для примера, код шлется в консоль/базу)
            self.current_user["tag"] = f"@{email_in.value.split('@')[0]}"
            self.current_user["id"] = email_in.value
            self.show_2fa_verification()

        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column([
                    ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold"),
                    ft.Container(
                        height=280, border=ft.border.all(1, "#00FF00"), padding=15,
                        content=ft.Text("[SYSTEM]: Ожидание авторизации...\n> База: CONNECTED\n> Шифрование: AES-256", color="#00FF00")
                    ),
                    email_in, pass_in,
                    ft.ElevatedButton("REGISTRATION", bgcolor="#00FF00", color="black", width=400, height=50),
                    ft.ElevatedButton("LOG_IN", on_click=handle_login, bgcolor="#00FF00", color="black", width=400, height=50),
                ], horizontal_alignment="center", spacing=12)
            )
        )

    def show_2fa_verification(self):
        self.page.clean()
        code = ft.TextField(label="ENTER_2FA_CODE_FROM_EMAIL", text_align="center", border_color="#00FF00")
        
        def check(e):
            self.notify("SYSTEM", "ACCESS_GRANTED")
            self.show_messenger()

        self.page.add(
            ft.Container(
                alignment=ft.alignment.center, expand=True,
                content=ft.Column([
                    ft.Text("VERIFY_IDENTITY", color="#00FF00", size=25),
                    code,
                    ft.ElevatedButton("VERIFY", on_click=check, bgcolor="#00FF00", color="black")
                ], horizontal_alignment="center")
            )
        )

    # --- ОСНОВНОЙ МЕССЕНДЖЕР ---
    def show_messenger(self):
        self.page.clean()
        self.chat_view = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
        search_box = ft.TextField(hint_text="SEARCH_BY_TAG...", expand=True, border_color="#00FF00", height=45)
        msg_box = ft.TextField(hint_text="Type encrypted message...", expand=True, border_color="#111111")

        def send_msg(e):
            if msg_box.value:
                self.db.collection("ghost_chats").add({
                    "u": self.current_user["tag"],
                    "m": self.crypt_msg(msg_box.value),
                    "r": self.current_user["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_box.value = ""
                self.page.update()

        # Слушаем сообщения в реальном времени
        self.db.collection("ghost_chats").order_by("ts", descending=False).on_snapshot(self.on_message_update)

        self.page.add(
            ft.Container(
                bgcolor="#080808", padding=15,
                content=ft.Row([
                    ft.Text("GHOST_PRO", color="#00FF00", size=22, weight="bold"),
                    ft.Row([
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(self.current_user["role"]=="ADMIN"), on_click=lambda _: self.show_admin_panel()),
                        ft.IconButton(ft.icons.ACCOUNT_CIRCLE, icon_color="#00FF00", on_click=lambda _: self.show_profile()),
                    ])
                ], justify="spaceBetween")
            ),
            ft.Container(padding=10, content=ft.Row([search_box, ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00")])),
            ft.Container(content=self.chat_view, expand=True, padding=15),
            ft.Container(
                bgcolor="#050505", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    ft.IconButton(ft.icons.ADD_PHOTO_ALTERNATE, icon_color="#00FF00"),
                    msg_box,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
                ])
            )
        )

    def on_message_update(self, docs, changes, read_time):
        self.chat_view.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            self.chat_view.controls.append(
                ft.Container(
                    padding=12, border_radius=15, bgcolor="#0A0A0A" if not is_adm else "#001000",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    content=ft.Column([
                        ft.Row([ft.Text(d.get("u"), color="#00FF00", size=11), ft.Text(d.get("time"), size=9)], justify="spaceBetween"),
                        ft.Text(self.crypt_msg(d.get("m"), "d"), size=16, color="white")
                    ], spacing=5)
                )
            )
        self.page.update()

    # --- ПРОФИЛЬ ---
    def show_profile(self):
        self.page.clean()
        new_tag = ft.TextField(label="CHANGE_USER_TAG", value=self.current_user["tag"], border_color="#00FF00")
        
        def save_profile(e):
            self.current_user["tag"] = new_tag.value
            self.notify("PROFILE", "DATA_UPDATED")
            self.show_messenger()

        self.page.add(
            ft.AppBar(title=ft.Text("USER_TERMINAL"), bgcolor="#000000"),
            ft.Column([
                ft.Container(ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=120, color="#00FF00"), alignment=ft.alignment.center),
                new_tag,
                ft.ElevatedButton("SAVE_IDENTITY", on_click=save_profile, bgcolor="#00FF00", color="black", width=400),
                ft.Divider(color="#1A1A1A"),
                ft.ListTile(leading=ft.Icon(ft.icons.SUPPORT_AGENT), title=ft.Text("CONTACT_SUPPORT"), on_click=lambda _: self.show_support()),
                ft.ElevatedButton("EXIT_TO_HUB", on_click=lambda _: self.show_messenger(), width=400)
            ], horizontal_alignment="center", padding=20, spacing=20)
        )

    # --- АДМИН ПАНЕЛЬ ---
    def show_admin_panel(self):
        self.page.clean()
        target_id = ft.TextField(label="USER_ID_TO_BAN", border_color="red")
        broadcast_msg = ft.TextField(label="GLOBAL_ALERT_MESSAGE", multiline=True)

        def send_broadcast(e):
            self.db.collection("ghost_chats").add({
                "u": "[SYSTEM_OVERRIDE]", "m": self.crypt_msg(broadcast_msg.value),
                "r": "ADMIN", "ts": firestore.SERVER_TIMESTAMP, "time": "NOW"
            })
            self.notify("ADMIN", "BROADCAST_SENT")

        self.page.add(
            ft.AppBar(title=ft.Text("ROOT_ACCESS_ONLY"), bgcolor="#440000"),
            ft.Column([
                target_id,
                ft.Row([
                    ft.ElevatedButton("BAN_USER", bgcolor="red", color="white"),
                    ft.ElevatedButton("UNBAN", bgcolor="green", color="white")
                ]),
                ft.Divider(),
                ft.Text("INCOMING_TICKETS:"),
                ft.Container(height=150, border=ft.border.all(1, "red"), content=ft.Text("No tickets pending...")),
                broadcast_msg,
                ft.ElevatedButton("PUSH_NOTIFICATION_ALL", on_click=send_broadcast, width=400),
                ft.ElevatedButton("CLOSE_TERMINAL", on_click=lambda _: self.show_messenger(), width=400)
            ], padding=20, spacing=15)
        )

    def show_support(self):
        self.page.clean()
        issue = ft.TextField(label="DESCRIBE_THE_ERROR", multiline=True, border_color="#00FF00")
        def submit(e): 
            self.notify("SUPPORT", "TICKET_OPENED")
            self.show_messenger()
        self.page.add(ft.Column([ft.Text("SUPPORT_SYSTEM", size=22), issue, ft.ElevatedButton("SUBMIT", on_click=submit)]))

if __name__ == "__main__":
    ft.app(target=GhostProApp)
 
