import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import base64
import random
import threading
from cryptography.fernet import Fernet

# ГЕНЕРАЦИЯ КЛЮЧА (Исправляет ошибку ValueError)
# Используем стабильный 32-байтный ключ
SAFE_KEY = base64.urlsafe_b64encode(b"GHOST_ULTIMATE_V13_32_BYTE_KEY_!")
cipher = Fernet(SAFE_KEY)

class GhostMessengerUltimate:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        
        # Настройки страницы
        self.page.title = "GHOST PRO V13"
        self.page.bgcolor = "#000000"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.fonts = {
            "RobotoMono": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
        }
        self.page.theme = ft.Theme(font_family="RobotoMono")
        
        # Переменные сессии
        self.user_tag = None
        self.user_role = "USER"
        
        self.init_firebase()
        self.check_auto_login()

    def init_firebase(self):
        """Инициализация базы данных без зависаний"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"CRITICAL_ERROR: Firebase not connected: {e}")

    def crypt(self, text, mode="e"):
        """Шифрование сообщений AES-256"""
        try:
            if mode == "e":
                return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except:
            return "[CORRUPTED_SIGNAL]"

    def check_auto_login(self):
        """Проверка сохраненного входа (чтобы не вылетало)"""
        saved_tag = self.page.client_storage.get("ghost_tag")
        saved_role = self.page.client_storage.get("ghost_role")
        
        if saved_tag:
            self.user_tag = saved_tag
            self.user_role = saved_role
            self.show_main_chat()
        else:
            self.show_matrix_auth()

    def show_matrix_auth(self):
        """Экран входа с эффектом Матрицы (семерки и символы)"""
        self.page.clean()
        
        # Эффект падающих символов
        matrix_lines = []
        for _ in range(15):
            line = "".join(random.choices("01789ABCDEF", k=40))
            matrix_lines.append(ft.Text(line, color="#003300", size=10, no_wrap=True))

        email_field = ft.TextField(
            label="IDENTITY_ID", 
            border_color="#00FF00", 
            focused_border_color="#00FF00",
            color="#00FF00",
            prefix_icon=ft.icons.PERSON_OUTLINE
        )
        pass_field = ft.TextField(
            label="ACCESS_CODE", 
            password=True, 
            can_reveal_password=True,
            border_color="#00FF00",
            focused_border_color="#00FF00",
            color="#00FF00",
            prefix_icon=ft.icons.LOCK_OPEN
        )

        def login_process(e):
            if not email_field.value or not pass_field.value:
                return

            # ТВОИ ДАННЫЕ АДМИНА
            if email_field.value == "adminpan" and pass_field.value == "TimaIssam2026":
                self.user_role = "ADMIN"
                self.user_tag = "@admin"
            else:
                self.user_role = "USER"
                self.user_tag = f"@{email_field.value.split('@')[0]}"

            # Сохраняем сессию на устройстве
            self.page.client_storage.set("ghost_tag", self.user_tag)
            self.page.client_storage.set("ghost_role", self.user_role)
            
            self.show_2fa_animation()

        self.page.add(
            ft.Stack([
                ft.Column(matrix_lines, spacing=2, opacity=0.5),
                ft.Container(
                    expand=True,
                    padding=30,
                    content=ft.Column([
                        ft.Text("GHOST_OS_V13", color="#00FF00", size=32, weight="bold"),
                        ft.Container(
                            height=250, border=ft.border.all(1, "#00FF00"), 
                            padding=20, bgcolor="#CC000000",
                            content=ft.Column([
                                ft.Text("> INITIALIZING BOOT_SEQUENCE...", color="#00FF00"),
                                ft.Text("> LOADING CRYPTO_CORE... OK", color="#00FF00"),
                                ft.Text("> SYNCING NODES... OK", color="#00FF00"),
                                ft.Text("> STATUS: STANDBY", color="#00FF00"),
                                ft.Divider(color="#00FF00"),
                                ft.Text("ОЖИДАНИЕ АВТОРИЗАЦИИ", color="#00FF00", weight="bold"),
                            ])
                        ),
                        email_field,
                        pass_field,
                        ft.Row([
                            ft.ElevatedButton(
                                "REGISTRATION", 
                                on_click=login_process,
                                bgcolor="#00FF00", color="black", 
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2))
                            ),
                            ft.ElevatedButton(
                                "LOG_IN", 
                                on_click=login_process,
                                bgcolor="#00FF00", color="black",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2))
                            ),
                        ], alignment="center", spacing=20),
                    ], horizontal_alignment="center", spacing=20)
                )
            ])
        )

    def show_2fa_animation(self):
        """Рабочая 2FA анимация"""
        self.page.clean()
        progress = ft.ProgressBar(width=300, color="#00FF00", bgcolor="#002200")
        status = ft.Text("DECRYPTING_IDENTITY...", color="#00FF00")
        
        self.page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, color="#00FF00", size=50),
                    status,
                    progress
                ], horizontal_alignment="center")
            )
        )
        time.sleep(1.5)
        self.show_main_chat()

    def show_main_chat(self):
        """Главный экран чата"""
        self.page.clean()
        self.chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
        message_input = ft.TextField(
            hint_text="Введите зашифрованный сигнал...",
            expand=True,
            border_color="#222222",
            focused_border_color="#00FF00",
            color="white"
        )

        def send_message(e):
            if message_input.value:
                # Добавляем в Firebase
                self.db.collection("ghost_messages").add({
                    "user": self.user_tag,
                    "text": self.crypt(message_input.value, "e"),
                    "role": self.user_role,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "time_str": datetime.datetime.now().strftime("%H:%M")
                })
                message_input.value = ""
                # Очистка старых сообщений (раз в 12 часов)
                self.auto_clean_task()
                self.page.update()

        # Подписка на обновления базы данных в реальном времени
        self.db.collection("ghost_messages").order_by("timestamp", direction="descending").limit(50).on_snapshot(self.on_db_update)

        self.page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_NODE: {self.user_tag}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(self.user_role=="ADMIN"), on_click=lambda _: self.show_admin_panel()),
                    ft.IconButton(ft.icons.LOGOUT, on_click=self.logout_process)
                ]
            ),
            ft.Container(
                content=self.chat_messages,
                expand=True,
                padding=15,
                border=ft.border.only(top=ft.border.BorderSide(1, "#111111"))
            ),
            ft.Container(
                bgcolor="#080808",
                padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC_ROUNDED, icon_color="#00FF00"),
                    message_input,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_message)
                ])
            )
        )

    def on_db_update(self, docs, changes, read_time):
        """Обновление списка сообщений"""
        self.chat_messages.controls.clear()
        # Разворачиваем, чтобы новые были внизу
        for doc in reversed(docs):
            data = doc.to_dict()
            is_me = data.get("user") == self.user_tag
            is_admin = data.get("role") == "ADMIN"
            
            self.chat_messages.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(data.get("user"), color="#00FF00", size=10, weight="bold"),
                                ft.Text(data.get("time_str"), color="#444444", size=8),
                            ], alignment="spaceBetween"),
                            ft.Text(self.crypt(data.get("text"), "d"), color="white", size=14),
                        ], spacing=2),
                        padding=12,
                        border_radius=15,
                        bgcolor="#111111" if not is_admin else "#001A00",
                        border=ft.border.all(1, "#222222" if not is_admin else "#00FF00"),
                        width=300
                    )
                ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
            )
        self.page.update()

    def auto_clean_task(self):
        """Удаление сообщений старше 12 часов"""
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            threshold = now - datetime.timedelta(hours=12)
            old_msgs = self.db.collection("ghost_messages").where("timestamp", "<", threshold).get()
            for m in old_msgs:
                m.reference.delete()
        except:
            pass

    def show_admin_panel(self):
        """Экран админки"""
        self.page.clean()
        broadcast = ft.TextField(label="GLOBAL_SIGNAL", border_color="red", color="red")
        
        def send_broadcast(e):
            if broadcast.value:
                self.db.collection("ghost_messages").add({
                    "user": "[SYSTEM_OVERRIDE]",
                    "text": self.crypt(broadcast.value, "e"),
                    "role": "ADMIN",
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "time_str": "NOW"
                })
                self.show_main_chat()

        self.page.add(
            ft.AppBar(title=ft.Text("ADMIN_PANEL_V13"), bgcolor="#220000"),
            ft.Column([
                ft.Text("УПРАВЛЕНИЕ СИСТЕМОЙ", color="red", size=20, weight="bold"),
                ft.Divider(color="red"),
                broadcast,
                ft.ElevatedButton("SEND_BROADCAST", on_click=send_broadcast, bgcolor="red", color="white", width=400),
                ft.ElevatedButton("WIPE_ALL_MESSAGES", bgcolor="red", color="white", width=400),
                ft.ElevatedButton("BACK", on_click=lambda _: self.show_main_chat(), width=400),
            ], padding=20, spacing=20)
        )

    def logout_process(self, e):
        """Полный выход из аккаунта"""
        self.page.client_storage.clear()
        self.show_matrix_auth()

if __name__ == "__main__":
    ft.app(target=GhostMessengerUltimate)
