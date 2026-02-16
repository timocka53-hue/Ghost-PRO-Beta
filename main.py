import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import base64

def main(page: ft.Page):
    # --- СИСТЕМНЫЕ НАСТРОЙКИ ---
    page.title = "GHOST PRO V13: ELITE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850

    class Session:
        db = None
        user = "GHOST"
        role = "USER"
        is_auth = False

    st = Session()

    # --- КРИПТО-ЗАГЛУШКА (ШИФРОВАНИЕ) ---
    def encrypt_data(text):
        return base64.b64encode(text.encode()).decode()

    def decrypt_data(text):
        try: return base64.b64decode(text.encode()).decode()
        except: return text

    # --- FIREBASE ENGINE ---
    def connect_matrix():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except: return False

    main_container = ft.Column(expand=True, spacing=0)
    page.add(main_container)

    # --- КОМПОНЕНТЫ: ЧАТ И ЛОГИ ---
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
    ticket_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def sync_matrix(docs, changes, read_time):
        chat_messages.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_messages.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=11, color="#00FF00" if is_adm else "#555555", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#222222")
                        ], justify="spaceBetween"),
                        ft.Text(decrypt_data(m.get("t")), color="#FFFFFF", size=14),
                        ft.Image(src=m.get("img"), width=200, visible=bool(m.get("img")))
                    ], spacing=5),
                    padding=15, bgcolor="#080808" if not is_adm else "#001500",
                    border=ft.border.all(1, "#111111" if not is_adm else "#00FF00"),
                    border_radius=15, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # --- ЭКРАН 1: ВХОД (adminpan / TimaIssam2026) ---
    def show_auth():
        u_in = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@")
        p_in = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00", can_reveal_password=True)
        
        def run_login(e):
            if u_in.value == "adminpan" and p_in.value == "TimaIssam2026":
                st.role = "ADMIN"
            st.user = f"@{u_in.value}"
            if connect_matrix(): show_hub()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("CRITICAL: NO serviceAccountKey.json FOUND"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        main_container.controls.clear()
        main_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.VAPES, size=100, color="#00FF00"),
                    ft.Text("GHOST PRO V13", size=40, weight="bold", color="#00FF00"),
                    ft.Text("ENCRYPTED DEEP-NET TERMINAL", size=10, color="#00FF00"),
                    ft.Divider(height=40, color="transparent"),
                    u_in, p_in,
                    ft.ElevatedButton("INITIALIZE UPLINK", on_click=run_login, bgcolor="#002200", color="#00FF00", width=350, height=60)
                ], horizontal_alignment="center", alignment="center"),
                expand=True, padding=40
            )
        )
        page.update()

    # --- ЭКРАН 2: ОСНОВНОЙ ХАБ ---
    def show_hub():
        msg_input = ft.TextField(hint_text="Enter data packet...", expand=True, border_color="#1A1A1A")
        
        def send_packet(e):
            if msg_input.value and st.db:
                st.db.collection("messages").add({
                    "u": st.user, "t": encrypt_data(msg_input.value), "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                page.update()

        # Слушатель базы
        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(40).on_snapshot(sync_matrix)

        main_container.controls.clear()
        main_container.controls.append(
            ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text("STATUS: SECURE", color="#00FF00", size=9),
                            ft.Text(st.user, size=18, weight="bold", color="white")
                        ]),
                        ft.Row([
                            ft.IconButton(ft.icons.SUPPORT_AGENT, icon_color="#00FF00", on_click=lambda _: show_support()),
                            ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=(st.role=="ADMIN"), on_click=lambda _: show_admin())
                        ])
                    ], justify="spaceBetween"),
                    padding=20, bgcolor="#0A0A0A"
                ),
                # Tabs
                ft.Tabs(
                    selected_index=0,
                    tabs=[ft.Tab(text="MATRIX_NET", icon=ft.icons.HUB), ft.Tab(text="PROFILE", icon=ft.icons.PERSON)],
                    expand=False
                ),
                # Chat Area
                ft.Container(content=chat_messages, expand=True, padding=10),
                # Input
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#333333"),
                        msg_input,
                        ft.IconButton(ft.icons.SEND_ROUNDED, icon_color="#00FF00", on_click=send_packet)
                    ]),
                    padding=20, bgcolor="#050505"
                )
            ], expand=True, spacing=0)
        )
        page.update()

    # --- АДМИН ПАНЕЛЬ ---
    def show_admin():
        main_container.controls.clear()
        main_container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("ADMIN TERMINAL"), bgcolor="#990000"),
                ft.ListTile(title=ft.Text("BAN ALL USERS"), icon=ft.icons.BLOCK, on_click=lambda _: print("Banned")),
                ft.ListTile(title=ft.Text("CLEAR MATRIX"), icon=ft.icons.DELETE_FOREVER, on_click=lambda _: st.db.collection("messages").get().remove()),
                ft.ElevatedButton("BACK TO HUB", on_click=lambda _: show_hub())
            ])
        )
        page.update()

    # --- ТЕХ ПОДДЕРЖКА (ТИКЕТЫ) ---
    def show_support():
        main_container.controls.clear()
        main_container.controls.append(
            ft.Column([
                ft.AppBar(title=ft.Text("SUPPORT TICKETS"), bgcolor="#004400"),
                ft.Text("Open your request to administration", padding=10),
                ft.TextField(label="Ticket Content", multiline=True),
                ft.ElevatedButton("SUBMIT TICKET"),
                ft.ElevatedButton("BACK", on_click=lambda _: show_hub())
            ])
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)
