import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

def main(page: ft.Page):
    # Настройки окна
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 0
    
    class System:
        db = None
        user = "GHOST"
        role = "USER"

    st = System()
    main_view = ft.Column(expand=True, spacing=0)
    page.add(main_view)

    # ПОДКЛЮЧЕНИЕ FIREBASE
    def connect():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            st.db = firestore.client()
            return True
        except: return False

    # ЭЛЕМЕНТЫ ЧАТА
    chat_box = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    def sync_data(docs, changes, read_time):
        chat_box.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            is_adm = m.get("r") == "ADMIN"
            chat_box.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(m.get("u"), size=10, color="#00FF00" if is_adm else "#777777", weight="bold"),
                            ft.Text(m.get("time"), size=9, color="#444444")
                        ], justify="spaceBetween"),
                        ft.Text(m.get("t"), color="#FFFFFF", size=14),
                    ], spacing=2),
                    padding=12, bgcolor="#0A0A0A" if not is_adm else "#001A00",
                    border=ft.border.all(1, "#1A1A1A" if not is_adm else "#00FF00"),
                    border_radius=10, margin=ft.margin.only(left=10, right=10)
                )
            )
        page.update()

    # ЭКРАН 1: АВТОРИЗАЦИЯ (ВМЕСТО КОНСОЛИ)
    def show_auth():
        u_field = ft.TextField(label="IDENT_ID", border_color="#00FF00", prefix_text="@")
        p_field = ft.TextField(label="2FA_KEY", password=True, border_color="#00FF00")
        
        def login_click(e):
            if u_field.value:
                st.user = f"@{u_field.value}"
                if u_field.value == "adminpan" and p_field.value == "TimaIssam2026":
                    st.role = "ADMIN"
                
                if connect(): show_hub()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("ERROR: serviceAccountKey.json NOT FOUND"))
                    page.snack_bar.open = True
                    page.update()

        main_view.controls.clear()
        main_view.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SECURITY, size=80, color="#00FF00"),
                    ft.Text("MATRIX LOGIN", size=30, weight="bold", color="#00FF00"),
                    u_field, p_field,
                    ft.ElevatedButton("CONNECT", on_click=login_click, bgcolor="#002200", color="#00FF00", width=300)
                ], horizontal_alignment="center", alignment="center"),
                expand=True
            )
        )
        page.update()

    # ЭКРАН 2: ХАБ (ЧАТ, ПОИСК, АДМИНКА)
    def show_hub():
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

        def delete_all(e): # ФУНКЦИЯ АДМИНА
            if st.role == "ADMIN":
                docs = st.db.collection("messages").stream()
                for d in docs: d.reference.delete()

        if st.db:
            st.db.collection("messages").order_by("ts").on_snapshot(sync_data)

        main_view.controls.clear()
        main_view.controls.append(
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"LOGGED AS: {st.user}", color="#00FF00", size=12),
                        ft.IconButton(ft.icons.DELETE_FOREVER, icon_color="red", visible=(st.role=="ADMIN"), on_click=delete_all)
                    ], justify="spaceBetween"),
                    padding=15, bgcolor="#0A0A0A"
                ),
                ft.Container(content=chat_box, expand=True),
                ft.Container(
                    content=ft.Row([msg_in, ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send)]),
                    padding=10
                )
            ], expand=True)
        )
        page.update()

    show_auth()

if __name__ == "__main__":
    ft.app(target=main)

                        
