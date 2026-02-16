import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

def main(page: ft.Page):
    # Настройки страницы
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    page.window_width = 450
    page.window_height = 850

    class State:
        db = None
        user = "GHOST"
        role = "USER"

    st = State()
    container = ft.Column(expand=True, spacing=0)
    page.add(container)

    # Инициализация базы (без консоли!)
    def init_db():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except:
            return False

    chat_feed = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def on_message(docs, changes, read_time):
        chat_feed.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_feed.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#888888", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=15),
                    ], spacing=5),
                    padding=12, bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=12, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # Экран логина
    def show_login():
        u_in = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@")
        p_in = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00")
        
        def do_login(e):
            if u_in.value:
                st.user = f"@{u_in.value}"
                if u_in.value == "adminpan" and p_in.value == "TimaIssam2026":
                    st.role = "ADMIN"
                if init_db():
                    show_chat()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("DB ERROR: Check serviceAccountKey.json"))
                    page.snack_bar.open = True
                    page.update()

        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.LOCK_PERSON, size=80, color="#00FF00"),
                    ft.Text("MATRIX AUTH", size=30, weight="bold", color="#00FF00"),
                    u_in, p_in,
                    ft.ElevatedButton("CONNECT", on_click=do_login, bgcolor="#002200", color="#00FF00", width=300, height=50)
                ], horizontal_alignment="center", alignment="center"),
                expand=True
            )
        )
        page.update()

    # Экран чата и админки
    def show_chat():
        msg_in = ft.TextField(hint_text="Type message...", expand=True, border_color="#1A1A1A")
        
        def send(e):
            if msg_in.value and st.db:
                st.db.collection("messages").add({
                    "u": st.user, "t": msg_in.value, "r": st.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
                msg_in.value = ""
                page.update()

        def clear_db(e): # Функция для админа
            if st.role == "ADMIN":
                docs = st.db.collection("messages").stream()
                for d in docs: d.reference.delete()

        if st.db:
            st.db.collection("messages").order_by("ts", descending=False).limit_to_last(50).on_snapshot(on_message)

        container.controls.clear()
        container.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"LOGGED: {st.user}", color="#00FF00", size=12),
                        ft.IconButton(ft.icons.DELETE_SWEEP, icon_color="red", visible=(st.role=="ADMIN"), on_click=clear_db)
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#0A0A0A"
                ),
                ft.Container(content=chat_feed, expand=True),
                ft.Container(
                    content=ft.Row([msg_in, ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send)]),
                    padding=15, bgcolor="#000000"
                )
            ], expand=True)
        )
        page.update()

    show_login()

if __name__ == "__main__":
    ft.app(target=main)


                        
