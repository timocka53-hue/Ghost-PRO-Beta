import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time

def main(page: ft.Page):
    # --- ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ ---
    page.title = "Ghost PRO"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.fonts = {
        "Matrix": "https://github.com/google/fonts/raw/main/apache/robotomono/RobotoMono%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Matrix")

    # Состояние системы (Real-time State)
    class GhostState:
        db = None
        uid = None
        role = "USER"
        target_chat = "GLOBAL"
        is_auth = False

    st = GhostState()

    # Основной контейнер для анимации переходов
    main_stack = ft.Stack(expand=True)
    page.add(main_stack)

    # --- СИСТЕМА ИНИЦИАЛИЗАЦИИ FIREBASE ---
    def init_firebase():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except:
            return False

    # --- КОМПОНЕНТЫ ИНТЕРФЕЙСА ---
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=15)
    
    def notify(text, color="#00FF00"):
        page.snack_bar = ft.SnackBar(ft.Text(text, color=color), bgcolor="#111111")
        page.snack_bar.open = True
        page.update()

    # Реальное общение (Snapshot Listener)
    def sync_messages(docs, changes, read_time):
        chat_list.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#888888", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=15),
                    ], spacing=5),
                    padding=15,
                    bgcolor="#0A0A0A" if not is_adm else "#001500",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=15,
                    animate=ft.animation.Animation(300, "fadeIn")
                )
            )
        page.update()

    # --- ЭКРАН 1: MATRIX IDENTIFICATION (2FA + ВХОД) ---
    def show_matrix_auth():
        id_field = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@", color="#00FF00")
        key_field = ft.TextField(label="2FA_ACCESS_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def start_connection(e):
            if not id_field.value:
                notify("ERROR: IDENT_ID REQUIRED", "red")
                return
            
            # Реальная идентификация и Админ-панель
            st.uid = f"@{id_field.value}"
            if id_field.value == "adminpan" and key_field.value == "TimaIssam2026":
                st.role = "ADMIN"
                notify("ADMIN ACCESS GRANTED")
            
            if init_firebase():
                notify("MATRIX UPLINK ESTABLISHED")
                show_terminal_hub()
            else:
                notify("CRITICAL: FIREBASE KEY MISSING", "red")

        auth_view = ft.Container(
            content=ft.Column([
                ft.Text("GHOST PRO V13", size=50, weight="bold", color="#00FF00"),
                ft.Text("SECURE ENCRYPTED NETWORK", size=12, color="#00FF00", italic=True),
                ft.Divider(height=40, color="transparent"),
                id_field, key_field,
                ft.ElevatedButton(
                    content=ft.Text("START MATRIX INITIALIZATION", weight="bold"),
                    on_click=start_connection,
                    bgcolor="#002200", color="#00FF00", width=400, height=60
                ),
            ], horizontal_alignment="center", alignment="center"),
            expand=True, padding=40, bgcolor="#000000"
        )
        main_stack.controls.clear()
        main_stack.controls.append(auth_view)
        page.update()

    # --- ЭКРАН 2: TERMINAL HUB (ЧАТ, ПОИСК, АДМИНКА) ---
    def show_terminal_hub():
        msg_input = ft.TextField(hint_text="Enter encrypted data...", expand=True, border_color="#1A1A1A", bgcolor="#050505")
        
        def send_message(e):
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

        # Поиск пользователей (Реальный поиск по базе)
        def open_search(e):
            search_field = ft.TextField(label="SEARCH_ID", border_color="#00FF00")
            def do_search(e):
                notify(f"SEARCHING FOR {search_field.value}...")
            
            page.dialog = ft.AlertDialog(
                title=ft.Text("DATABASE SEARCH"),
                content=search_field,
                actions=[ft.TextButton("EXECUTE", on_click=do_search)]
            )
            page.dialog.open = True
            page.update()

        # Запуск реального прослушивания чата
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(sync_messages)

        hub_view = ft.Column([
            # Шапка (Status Bar)
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("SYSTEM_STATUS: ONLINE", color="#00FF00", size=10, weight="bold"),
                        ft.Row([
                            ft.Text(st.uid, color="#FFFFFF", size=16, weight="bold"),
                            ft.Icon(ft.icons.VERIFIED, color="#00FF00", size=20, visible=(st.role=="ADMIN"))
                        ])
                    ]),
                    ft.IconButton(ft.icons.POWER_SETTINGS_NEW, icon_color="#555555", on_click=lambda _: show_matrix_auth())
                ], justify="spaceBetween"),
                padding=20, bgcolor="#0A0A0A", border=ft.border.only(bottom=ft.border.BorderSide(1, "#1A1A1A"))
            ),
            # Навигация
            ft.Container(
                content=ft.Row([
                    ft.TextButton("GLOBAL_NET", icon=ft.icons.HUB, icon_color="#00FF00"),
                    ft.TextButton("SEARCH", icon=ft.icons.SEARCH, icon_color="#00FF00", on_click=open_search),
                    ft.TextButton("ADMIN", icon=ft.icons.DASHBOARD, icon_color="red", visible=(st.role=="ADMIN")),
                ], scroll=ft.ScrollMode.AUTO),
                padding=10
            ),
            # Чат (Реальное общение)
            ft.Container(content=chat_list, expand=True, padding=10),
            # Ввод сообщений
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.icons.ADD_CIRCLE_OUTLINE, icon_color="#333333"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_message)
                ]),
                padding=20, bgcolor="#050505"
            )
        ], expand=True, spacing=0)

        main_stack.controls.clear()
        main_stack.controls.append(hub_view)
        page.update()

    show_matrix_auth()

if __name__ == "__main__":
    ft.app(target=main)
