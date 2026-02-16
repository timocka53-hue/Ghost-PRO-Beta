import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- БАЗОВЫЕ НАСТРОЙКИ СИСТЕМЫ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 20
    page.window_width = 450
    page.window_height = 850
    
    # Состояние приложения
    state = {
        "db": None,
        "uid": None,
        "role": "USER",
        "chat_partner": "GLOBAL",
        "is_auth": False
    }

    # Сразу рисуем визуальный каркас (защита от черного экрана)
    main_container = ft.Column(expand=True)
    page.add(main_container)

    # --- ИНИЦИАЛИЗАЦИЯ DATABASE ---
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            state["db"] = firestore.client()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False

    # --- ЭЛЕМЕНТЫ ИНТЕРФЕЙСА ЧАТА ---
    messages_view = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
    message_input = ft.TextField(
        hint_text="Введите зашифрованное сообщение...",
        expand=True,
        border_color="#00FF00",
        bgcolor="#0A0A0A",
        color="#FFFFFF"
    )

    # --- ЛОГИКА ОБРАБОТКИ СООБЩЕНИЙ ---
    def send_msg(e):
        if message_input.value and state["db"]:
            msg_data = {
                "u": state["uid"],
                "t": message_input.value,
                "r": state["role"],
                "ts": firestore.SERVER_TIMESTAMP,
                "time": datetime.datetime.now().strftime("%H:%M")
            }
            state["db"].collection("messages").add(msg_data)
            message_input.value = ""
            page.update()

    def update_chat_snapshot(docs, changes, read_time):
        messages_view.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            messages_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=11, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=15),
                    ], spacing=2),
                    padding=12,
                    bgcolor="#0A0A0A" if not is_adm else "#001100",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=10
                )
            )
        page.update()

    # --- ЭКРАНЫ СИСТЕМЫ ---
    def show_auth_screen():
        u_field = ft.TextField(label="GHOST_ID", border_color="#00FF00", prefix_text="@")
        p_field = ft.TextField(label="2FA_ACCESS_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def attempt_login(e):
            if u_field.value:
                state["uid"] = f"@{u_field.value}"
                # Админ-панель: проверка прав
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    state["role"] = "ADMIN"
                
                init_db()
                show_terminal_screen()

        main_container.controls.clear()
        main_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED NETWORK ACCESS", size=12, color="#00FF00"),
                    ft.Divider(height=40, color="transparent"),
                    u_field, p_field,
                    ft.ElevatedButton(
                        "ESTABLISH CONNECTION", 
                        on_click=attempt_login,
                        bgcolor="#002200", 
                        color="#00FF00", 
                        width=350, 
                        height=60
                    )
                ], horizontal_alignment="center", alignment="center"),
                expand=True
            )
        )
        page.update()

    def show_terminal_screen():
        if state["db"]:
            state["db"].collection("messages").order_by("ts", descending=False).limit_to_last(25).on_snapshot(update_chat_snapshot)

        main_container.controls.clear()
        main_container.controls.append(
            ft.Column([
                # Шапка
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("SYSTEM_STATUS: ONLINE", color="#00FF00", size=10, weight="bold"),
                            ft.Text(f"SESSION: {state['uid']}", color="#FFFFFF", size=12),
                        ]),
                        ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=24, visible=(state["role"]=="ADMIN"))
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#0A0A0A", border_radius=10
                ),
                # Меню управления
                ft.Row([
                    ft.TextButton("ПОИСК", icon=ft.icons.SEARCH, icon_color="#00FF00"),
                    ft.TextButton("КАНАЛЫ", icon=ft.icons.HUB, icon_color="#00FF00"),
                    ft.TextButton("АДМИН", icon=ft.icons.DASHBOARD, icon_color="red", visible=(state["role"]=="ADMIN")),
                ], scroll=ft.ScrollMode.AUTO),
                # Чат
                ft.Container(content=messages_view, expand=True, padding=10),
                # Ввод
                ft.Row([
                    message_input,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)
                ])
            ], expand=True)
        )
        page.update()

    show_auth_screen()

# Запуск приложения без аргументов, вызывающих ошибки в Termux
if __name__ == "__main__":
    ft.app(target=main)
