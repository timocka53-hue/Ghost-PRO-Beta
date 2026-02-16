import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    # Состояние системы
    class State:
        db = None
        uid = None
        role = "USER"
        is_auth = False

    st = State()

    # Контейнер для смены экранов
    main_container = ft.Column(expand=True, spacing=0)
    page.add(main_container)

    # --- ИНИЦИАЛИЗАЦИЯ DATABASE ---
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except Exception:
            return False

    # --- ВИЗУАЛЬНЫЕ КОМПОНЕНТЫ ЧАТА ---
    messages_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def on_snapshot(docs, changes, read_time):
        messages_list.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_adm = data.get("r") == "ADMIN"
            messages_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), size=10, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(data.get("t"), color="#FFFFFF", size=15),
                    ], spacing=2),
                    padding=12,
                    bgcolor="#0A0A0A" if not is_adm else "#001100",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=12,
                    margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН 1: ВХОД (БЕЗ INPUT) ---
    def show_auth():
        main_container.controls.clear()
        
        u_field = ft.TextField(
            label="GHOST_ID", 
            border_color="#00FF00", 
            focused_border_color="#FFFFFF",
            prefix_text="@"
        )
        p_field = ft.TextField(
            label="2FA_KEY", 
            password=True, 
            border_color="#00FF00", 
            can_reveal_password=True
        )

        def attempt_login(e):
            if u_field.value:
                st.uid = f"@{u_field.value}"
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if init_db():
                    show_terminal()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("DATABASE ERROR"))
                    page.snack_bar.open = True
                    page.update()

        main_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=45, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED NETWORK", size=12, color="#00FF00"),
                    ft.Divider(height=50, color="transparent"),
                    u_field, 
                    p_field,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton(
                        "ESTABLISH CONNECTION", 
                        on_click=attempt_login,
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

    # --- ЭКРАН 2: ТЕРМИНАЛ ---
    def show_terminal():
        main_container.controls.clear()
        
        msg_input = ft.TextField(
            hint_text="Type encrypted message...",
            expand=True,
            border_color="#1A1A1A",
            bgcolor="#0A0A0A",
            text_size=14
        )

        def send_msg(e):
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

        # Запуск прослушивания
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(30).on_snapshot(on_snapshot)

        # Интерфейс терминала
        main_container.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"ST_ACTIVE: {st.uid}", color="#00FF00", weight="bold"),
                        ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                ft.Container(content=messages_list, expand=True, padding=10),
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.SEARCH, icon_color="#555555"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_msg)
                    ]),
                    padding=15, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    # СТРОГО БЕЗ ПАРАМЕТРОВ ДЛЯ ТЕРМИНАЛА
    ft.app(target=main)

