import flet as ft
import flet_firebase as ff
import datetime

# ДАННЫЕ ТВОЕГО ПРОЕКТА
FB_CONFIG = {
    "apiKey": "AIzaSyAbiRCuR9egtHKg0FNzzBdL9dNqPqpPLNk",
    "authDomain": "ghost-pro-5aa22.firebaseapp.com",
    "projectId": "ghost-pro-5aa22",
    "storageBucket": "ghost-pro-5aa22.firebasestorage.app",
    "messagingSenderId": "332879455079",
    "appId": "1:332879455079:android:15c36642c62d13e0dd05c2"
}

def main(page: ft.Page):
    page.title = "GHOST PRO: GLOBAL"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10
    
    state = {"uid": None, "current_chat": "global"} # По умолчанию общий чат

    # Инициализация Firebase прямо в приложении
    fb = ff.Firebase(config=FB_CONFIG)

    chat_display = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
    
    # --- ФУНКЦИЯ УВЕДОМЛЕНИЙ И ОБНОВЛЕНИЯ ---
    def on_message_received(message):
        # Если пришло сообщение не от нас - шлем уведомление
        if message.data.get("user") != state["uid"]:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Новое сообщение от {message.data.get('user')}")))
        
        # Обновляем экран чата
        render_messages()

    # Подписка на коллекцию сообщений
    messages_ref = fb.firestore().collection("all_messages")

    def render_messages():
        # Получаем последние 50 сообщений
        docs = messages_ref.order_by("ts", descending=False).limit_to_last(50).get()
        chat_display.controls.clear()
        for d in docs:
            m = d.to_dict()
            is_me = m.get("user") == state["uid"]
            chat_display.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(m.get("user"), size=10, color="#00FF00"),
                        ft.Text(m.get("text"), color="white", size=16),
                    ]),
                    alignment=ft.alignment.center_right if is_me else ft.alignment.center_left,
                    bgcolor="#0A0A0A" if is_me else "#1A1A1A",
                    padding=10,
                    border_radius=ft.border_radius.only(
                        top_left=10, top_right=10, 
                        bottom_left=0 if is_me else 10, 
                        bottom_right=10 if is_me else 0
                    ),
                    border=ft.border.all(1, "#00FF00" if is_me else "#333333")
                )
            )
        page.update()

    def send_click(e):
        if msg_input.value:
            messages_ref.add({
                "user": state["uid"],
                "text": msg_input.value,
                "ts": datetime.datetime.now().timestamp()
            })
            msg_input.value = ""
            page.update()

    # --- ИНТЕРФЕЙС ---
    msg_input = ft.TextField(hint_text="Введите сообщение...", expand=True, border_color="#00FF00")
    search_input = ft.TextField(hint_text="Поиск юзера по нику...", expand=True, border_color="#555555")

    def login_action(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            # Регистрируем юзера в глобальном списке
            fb.firestore().collection("users").document(state["uid"]).set({"status": "online"})
            
            page.clean()
            page.add(
                ft.Column([
                    ft.Row([
                        ft.Text("GHOST_PRO", size=20, weight="bold", color="#00FF00"),
                        ft.IconButton(ft.icons.NOTIFICATIONS_ACTIVE, icon_color="#00FF00")
                    ], justify="spaceBetween"),
                    ft.Row([search_input, ft.IconButton(ft.icons.SEARCH, on_click=lambda _: page.show_snack_bar(ft.SnackBar(ft.Text("Поиск реализован в общей базе"))))]),
                    ft.Container(content=chat_display, expand=True),
                    ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=send_click)])
                ], expand=True)
            )
            # Запускаем прослушку
            messages_ref.on_snapshot(lambda docs, changes, time: render_messages())

    # Экран входа
    user_in = ft.TextField(label="ВАШ НИК", border_color="#00FF00")
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.LOCK_OPEN, size=100, color="#00FF00"),
                ft.Text("GLOBAL MATRIX NETWORK", size=24, weight="bold"),
                user_in,
                ft.ElevatedButton("ВОЙТИ В ЭФИР", on_click=login_action, bgcolor="#002200", color="#00FF00", width=250)
            ], horizontal_alignment="center", spacing=20),
            alignment=ft.alignment.center, expand=True
        )
    )

ft.app(target=main)
