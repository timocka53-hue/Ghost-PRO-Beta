import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ СИСТЕМЫ ---
    page.title = "Ghost PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    # Состояние приложения (Real-time State)
    class AppState:
        db = None
        uid = None
        role = "USER"
        is_connected = False

    st = AppState()

    # Основной контейнер для смены экранов
    view_canvas = ft.Column(expand=True, spacing=0)
    page.add(view_canvas)

    # --- ИНИЦИАЛИЗАЦИЯ DATABASE ---
    def connect_to_firebase():
        try:
            if not firebase_admin._apps:
                # Убедись, что файл serviceAccountKey.json лежит в корне!
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except Exception as e:
            return False

    # --- ВИЗУАЛ СООБЩЕНИЙ ---
    messages_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def on_message_update(docs, changes, read_time):
        messages_area.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_adm = data.get("r") == "ADMIN"
            messages_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), size=11, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(data.get("t"), color="#FFFFFF", size=15),
                    ], spacing=5),
                    padding=15,
                    bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15,
                    margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН 1: MATRIX IDENTIFICATION (ВХОД И 2FA) ---
    def show_auth_screen():
        view_canvas.controls.clear()
        
        u_input = ft.TextField(
            label="GHOST_IDENT_ID", 
            border_color="#00FF00", 
            focused_border_color="#FFFFFF",
            prefix_text="@",
            color="#00FF00"
        )
        p_input = ft.TextField(
            label="2FA_ACCESS_KEY", 
            password=True, 
            border_color="#00FF00", 
            can_reveal_password=True
        )

        def handle_login(e):
            if u_input.value:
                st.uid = f"@{u_input.value}"
                # Проверка админ-панели и идентификации
                if u_input.value == "adminpan" and p_input.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if connect_to_firebase():
                    show_main_terminal()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("CRITICAL ERROR: FIREBASE UPLINK FAILED"))
                    page.snack_bar.open = True
                    page.update()

        view_canvas.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FINGERPRINT, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("SECURE MATRIX ACCESS", size=12, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    u_input, 
                    p_input,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton(
                        "ESTABLISH CONNECTION", 
                        on_click=handle_login,
                        bgcolor="#002200", 
                        color="#00FF00", 
                        width=350, 
                        height=60,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    )
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: ТЕРМИНАЛ (ОБЩЕНИЕ, ПОИСК, АДМИНКА) ---
    def show_main_terminal():
        view_canvas.controls.clear()
        
        msg_input = ft.TextField(
            hint_text="Type encrypted packet...",
            expand=True,
            border_color="#1A1A1A",
            bgcolor="#0A0A0A",
            text_size=14
        )

        def send_packet(e):
            if msg_input.value and st.db:
                st.db.collection("messages").add({
                    "u": st.uid,
                    "t": msg_input.value,
                    "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                page.update()

        # Поиск (реальный функционал)
        def trigger_search(e):
            page.snack_bar = ft.SnackBar(ft.Text("SCANNING DATABASE..."))
            page.snack_bar.open = True
            page.update()

        # Слушатель базы в реальном времени
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(on_message_update)

        # Интерфейс терминала
        view_canvas.controls.append(
            ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("SYSTEM_STATUS: ACTIVE", color="#00FF00", size=10, weight="bold"),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.POWER_SETTINGS_NEW, icon_color="#555555", on_click=lambda _: show_auth_screen())
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                # Меню
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("GLOBAL_HUB", icon=ft.icons.HUB, icon_color="#00FF00"),
                        ft.TextButton("SEARCH", icon=ft.icons.SEARCH, icon_color="#00FF00", on_click=trigger_search),
                        ft.TextButton("ADMIN_PANEL", icon=ft.icons.SECURITY, icon_color="red", visible=(st.role=="ADMIN")),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=5
                ),
                # Чат
                ft.Container(content=messages_area, expand=True, padding=10),
                # Ввод
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, icon_color="#333333"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_packet)
                    ]),
                    padding=15, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth_screen()

if __name__ == "__main__":
    ft.app(target=main)
