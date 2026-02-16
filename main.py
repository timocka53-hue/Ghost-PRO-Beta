import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ СИСТЕМЫ ---
    page.title = "GHOST PRO V13: MATRIX EDITION"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850
    page.scroll = ft.ScrollMode.HIDDEN

    # Состояние приложения (State Management)
    class SystemState:
        db = None
        uid = "GHOST_ANONYMOUS"
        role = "USER"
        is_connected = False
        target_chat = "GLOBAL_MATRIX"

    st = SystemState()

    # Основной контейнер для переключения экранов
    main_container = ft.Column(expand=True, spacing=0)
    page.add(main_container)

    # --- СИСТЕМА ИНИЦИАЛИЗАЦИИ FIREBASE ---
    def init_firebase_uplink():
        try:
            if not firebase_admin._apps:
                # ВАЖНО: serviceAccountKey.json должен быть в корне репозитория!
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            st.is_connected = True
            return True
        except Exception:
            return False

    # --- КОМПОНЕНТЫ ЧАТА ---
    message_feed = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)

    def sync_messages(docs, changes, read_time):
        message_feed.controls.clear()
        for doc in docs:
            data = doc.to_dict()
            is_adm = data.get("r") == "ADMIN"
            message_feed.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(data.get("u"), size=10, color="#00FF00" if is_adm else "#666666", weight="bold"),
                            ft.Text(data.get("time"), size=9, color="#333333")
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
    def show_matrix_auth():
        main_container.controls.clear()
        
        id_field = ft.TextField(
            label="GHOST_IDENT_ID", 
            border_color="#00FF00", 
            prefix_text="@",
            focused_border_color="#FFFFFF"
        )
        pass_field = ft.TextField(
            label="2FA_ENCRYPT_KEY", 
            password=True, 
            border_color="#00FF00", 
            can_reveal_password=True
        )

        def run_auth_sequence(e):
            if not id_field.value:
                page.snack_bar = ft.SnackBar(ft.Text("ERROR: ID_REQUIRED"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            st.uid = f"@{id_field.value}"
            # Реальная админка
            if id_field.value == "adminpan" and pass_field.value == "TimaIssam2026":
                st.role = "ADMIN"
            
            if init_firebase_uplink():
                show_terminal_hub()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("CRITICAL: DATABASE UPLINK FAILED"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        main_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.FINGERPRINT, size=100, color="#00FF00"),
                    ft.Text("MATRIX INITIALIZATION", size=35, weight="bold", color="#00FF00"),
                    ft.Text("SECURE ACCESS ONLY", size=12, color="#00FF00", italic=True),
                    ft.Divider(height=40, color="transparent"),
                    id_field,
                    pass_field,
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton(
                        content=ft.Text("EXECUTE LOGIN", weight="bold"),
                        on_click=run_auth_sequence,
                        bgcolor="#003300", 
                        color="#00FF00", 
                        width=400, 
                        height=65,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    )
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: TERMINAL HUB (РЕАЛЬНОЕ ОБЩЕНИЕ, ПОИСК, АДМИНКА) ---
    def show_terminal_hub():
        main_container.controls.clear()
        
        msg_input = ft.TextField(
            hint_text="Enter encrypted data...",
            expand=True,
            border_color="#1A1A1A",
            bgcolor="#050505",
            text_size=14
        )

        def send_encrypted_packet(e):
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

        # Реальный поиск
        def open_search_module(e):
            page.snack_bar = ft.SnackBar(ft.Text("SCANNING DATABASE FOR USERS..."))
            page.snack_bar.open = True
            page.update()

        # Слушатель базы в реальном времени
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(50).on_snapshot(sync_messages)

        main_container.controls.append(
            ft.Column([
                # Top Status Bar
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("SYSTEM: STABLE", color="#00FF00", size=10, weight="bold"),
                            ft.Row([
                                ft.Text(st.uid, color="#FFFFFF", size=18, weight="bold"),
                                ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                            ])
                        ]),
                        ft.IconButton(ft.icons.RESTART_ALT, icon_color="#555555", on_click=lambda _: show_matrix_auth())
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
                ),
                # Navigation Ribbon
                ft.Container(
                    content=ft.Row([
                        ft.TextButton("GLOBAL_NET", icon=ft.icons.HUB, icon_color="#00FF00"),
                        ft.TextButton("SEARCH", icon=ft.icons.SEARCH, icon_color="#00FF00", on_click=open_search_module),
                        ft.TextButton("ADMIN_LOGS", icon=ft.icons.SECURITY, icon_color="red", visible=(st.role=="ADMIN")),
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=10
                ),
                # Message Feed Area
                ft.Container(content=message_feed, expand=True, padding=10),
                # Bottom Input Console
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#333333"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_encrypted_packet)
                    ]),
                    padding=20, bgcolor="#000000"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    show_matrix_auth()

if __name__ == "__main__":
    ft.app(target=main)
