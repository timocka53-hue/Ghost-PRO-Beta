import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ СИСТЕМЫ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.fonts = {
        "GhostFont": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="GhostFont")

    # Состояние приложения (State Management)
    class SystemState:
        db = None
        uid = None
        role = "USER"
        is_connected = False
        current_target = "GLOBAL"

    st = SystemState()

    # --- СИСТЕМА ИНИЦИАЛИЗАЦИИ FIREBASE ---
    def connect_to_matrix():
        try:
            if not firebase_admin._apps:
                # Файл должен быть в корне репозитория!
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except Exception as e:
            print(f"CRITICAL_ERROR: {e}")
            return False

    # --- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА (КОМПОНЕНТЫ) ---
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
    
    def create_msg_bubble(data):
        is_admin = data.get("r") == "ADMIN"
        is_me = data.get("u") == st.uid
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(data.get("u"), size=10, color="#00FF00" if is_admin else "#777777", weight="bold"),
                    ft.Text(data.get("time"), size=9, color="#444444")
                ], justify="spaceBetween"),
                ft.Text(data.get("t"), color="#FFFFFF", size=15),
            ], spacing=5),
            padding=15,
            bgcolor="#0A0A0A" if not is_admin else "#001100",
            border=ft.border.all(1, "#1A1A1A" if not is_admin else "#00FF00"),
            border_radius=12,
            margin=ft.margin.only(left=10, right=10)
        )

    def on_snapshot(docs, changes, read_time):
        chat_messages.controls.clear()
        for doc in docs:
            m_data = doc.to_dict()
            chat_messages.controls.append(create_msg_bubble(m_data))
        page.update()

    # --- ЭКРАН 1: АУТЕНТИФИКАЦИЯ (2FA) ---
    def show_auth():
        page.clean()
        
        login_input = ft.TextField(
            label="GHOST_ID", 
            border_color="#00FF00", 
            prefix_text="@",
            focused_border_color="#FFFFFF"
        )
        pass_input = ft.TextField(
            label="2FA_ACCESS_KEY", 
            password=True, 
            border_color="#00FF00",
            can_reveal_password=True
        )

        def login_process(e):
            if login_input.value:
                st.uid = f"@{login_input.value}"
                # Админ-панель: доступ по ключу
                if login_input.value == "adminpan" and pass_input.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                # Попытка подключения
                if connect_to_matrix():
                    show_main_terminal()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("DATABASE CONNECTION FAILED"))
                    page.snack_bar.open = True
                    page.update()

        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("SECURE MATRIX PROTOCOL", size=12, color="#00FF00", italic=True),
                    ft.Divider(height=50, color="transparent"),
                    login_input,
                    pass_input,
                    ft.ElevatedButton(
                        content=ft.Text("ESTABLISH UPLINK", weight="bold", size=18),
                        on_click=login_process,
                        bgcolor="#002200",
                        color="#00FF00",
                        width=350,
                        height=60,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                ], horizontal_alignment="center", alignment="center"),
                expand=True,
                padding=40
            )
        )

    # --- ЭКРАН 2: ОСНОВНОЙ ТЕРМИНАЛ ---
    def show_main_terminal():
        page.clean()
        
        msg_field = ft.TextField(
            hint_text="Type encrypted message...",
            expand=True,
            border_color="#1A1A1A",
            bgcolor="#0A0A0A",
            text_size=14
        )

        def send_click(e):
            if msg_field.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid,
                    "t": msg_field.value,
                    "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_field.value = ""
                page.update()

        # Запуск прослушивания базы в реальном времени
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(30).on_snapshot(on_snapshot)

        # Верхняя панель (Status Bar)
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("SYSTEM_ACTIVE", color="#00FF00", size=10, weight="bold"),
                    ft.Row([
                        ft.Text(st.uid, color="#FFFFFF", size=14, weight="bold"),
                        ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=18, visible=(st.role=="ADMIN"))
                    ])
                ]),
                ft.IconButton(ft.icons.LOGOUT, icon_color="#555555", on_click=lambda _: show_auth())
            ], justify="spaceBetween"),
            padding=20,
            bgcolor="#0A0A0A",
            border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
        )

        # Боковое/нижнее меню навигации
        nav_menu = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.icons.SEARCH, icon_color="#00FF00", tooltip="Поиск"),
                ft.IconButton(ft.icons.CHAT_BUBBLE, icon_color="#00FF00", tooltip="Чаты"),
                ft.IconButton(ft.icons.DASHBOARD, icon_color="red", visible=(st.role=="ADMIN"), tooltip="Админ панель"),
                ft.IconButton(ft.icons.SETTINGS, icon_color="#555555")
            ], justify="spaceAround"),
            padding=10,
            bgcolor="#050505"
        )

        page.add(
            ft.Column([
                header,
                ft.Container(content=chat_messages, expand=True, padding=10),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#333333"),
                        msg_field,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_click)
                    ]),
                    padding=15,
                    bgcolor="#000000"
                ),
                nav_menu
            ], expand=True, spacing=0)
        )

    show_auth()

if __name__ == "__main__":
    # Запуск без дополнительных флагов, чтобы избежать ошибок среды выполнения
    ft.app(target=main)
