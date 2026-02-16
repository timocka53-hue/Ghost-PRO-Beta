import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import base64, datetime

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    # Конфиг админки
    ADM_USER = "adminpan"
    ADM_PASS = "TimaIssam2026"

    class State:
        db = None
        user = ""
        role = "USER"

    st = State()

    # Инициализация базы
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except: return False

    # Элементы чата
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    def on_msg(docs, changes, read_time):
        chat_list.controls.clear()
        for doc in docs:
            d = doc.to_dict()
            is_adm = d.get("r") == "ADMIN"
            chat_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{d.get('u')} | {d.get('time')}", size=10, color="#00FF00" if is_adm else "#555555"),
                        ft.Text(base64.b64decode(d.get('t')).decode(), size=16, color="white")
                    ]),
                    padding=10, bgcolor="#0A0A0A", border=ft.border.all(1, "#1A1A1A"), border_radius=10
                )
            )
        page.update()

    # Логин
    def login_click(e):
        if u_in.value == ADM_USER and p_in.value == ADM_PASS:
            st.role = "ADMIN"
        st.user = f"@{u_in.value}"
        if init_db(): show_chat()
        else: page.snack_bar = ft.SnackBar(ft.Text("DB Error!")); page.snack_bar.open = True; page.update()

    u_in = ft.TextField(label="ID", border_color="#00FF00")
    p_in = ft.TextField(label="KEY", password=True, border_color="#00FF00")
    
    auth_view = ft.Column([
        ft.Icon(ft.icons.SECURITY, size=100, color="#00FF00"),
        u_in, p_in,
        ft.ElevatedButton("CONNECT", on_click=login_click, bgcolor="#002200", color="#00FF00")
    ], horizontal_alignment="center", alignment="center")

    def show_chat():
        page.controls.clear()
        msg_in = ft.TextField(expand=True)
        
        def send(e):
            if msg_in.value:
                st.db.collection("chat").add({
                    "u": st.user, "r": st.role, 
                    "t": base64.b64encode(msg_in.value.encode()).decode(),
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        st.db.collection("chat").order_by("ts").on_snapshot(on_msg)
        
        page.add(ft.Column([
            ft.Text(f"GHOST SYSTEM: {st.user}", color="#00FF00"),
            chat_list,
            ft.Row([msg_in, ft.IconButton(ft.icons.SEND, on_click=send)])
        ], expand=True))
        page.update()

    page.add(auth_view)

ft.app(target=main)
