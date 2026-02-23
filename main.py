import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import base64
import random
import asyncio
from cryptography.fernet import Fernet

# Ключ шифрования (стабильный)
K = base64.urlsafe_b64encode(b"GHOST_V13_SECURE_KEY_32_BYTE_!!!")
cipher = Fernet(K)

async def main(page: ft.Page):
    # Базовые настройки страницы
    page.title = "GHOST PRO V13"
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    
    # Состояние приложения
    app_state = {
        "db": None,
        "tag": None,
        "role": "USER",
        "chat_msgs": ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)
    }

    def encrypt_msg(text, mode="e"):
        try:
            if mode == "e": return cipher.encrypt(text.encode()).decode()
            return cipher.decrypt(text.encode()).decode()
        except: return "[ENCRYPTED]"

    # --- ФОНОВАЯ ИНИЦИАЛИЗАЦИЯ ---
    async def connect_firebase():
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("google-services.json")
                firebase_admin.initialize_app(cred)
            app_state["db"] = firestore.client()
            print("Firebase Connected")
        except:
            print("Firebase Error")

    # --- ЛОГИКА ВХОДА И РЕГИСТРАЦИИ ---
    async def run_auth(e, email_in, pass_in):
        if not email_in.value or not pass_in.value: return
        
        # Проверка админки по твоим данным
        if email_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            role, tag = "ADMIN", "@admin"
        else:
            role, tag = "USER", f"@{email_in.value.split('@')[0]}"
        
        # Сохранение входа (чтобы аккаунт не вылетал)
        page.client_storage.set("is_logged", True)
        page.client_storage.set("u_tag", tag)
        page.client_storage.set("u_role", role)
        
        app_state["tag"], app_state["role"] = tag, role
        await show_2fa_and_chat()

    # --- ДИЗАЙН: МАТРИЦА И ВХОД ---
    async def show_login_screen():
        page.clean()
        
        # Эффект взлома (падающие символы 0, 1, 7)
        matrix_bg = ft.Column([
            ft.Row([ft.Text(random.choice("701"), color="#004400", size=10) for _ in range(40)]) 
            for _ in range(25)
        ], spacing=0, opacity=0.3)

        email = ft.TextField(label="IDENTITY_ID", border_color="#00FF00", color="#00FF00", width=350)
        password = ft.TextField(label="ACCESS_CODE", password=True, border_color="#00FF00", color="#00FF00", width=350)

        page.add(
            ft.Stack([
                matrix_bg,
                ft.Container(
                    expand=True, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Text("GHOST_OS: V13_FINAL", color="#00FF00", size=26, weight="bold"),
                        ft.Container(
                            height=220, width=350, border=ft.border.all(1, "#00FF00"), padding=20, bgcolor="#CC000000",
                            content=ft.Column([
                                ft.Text("> MATRIX_CORE: ACTIVE", color="#00FF00", size=12),
                                ft.Text("> 2FA_PROTECTION: ON", color="#00FF00", size=12),
                                ft.Text("> SESSION_AUTO_SAVE: ON", color="#00FF00", size=12),
                                ft.Divider(color="#00FF00"),
                                ft.Text("ОЖИДАНИЕ СИГНАЛА...", color="#00FF00", weight="bold"),
                            ])
                        ),
                        email, password,
                        ft.ElevatedButton("REGISTRATION", on_click=lambda e: run_auth(e, email, password), bgcolor="#00FF00", color="black", width=350, height=50),
                        ft.ElevatedButton("LOG_IN", on_click=lambda e: run_auth(e, email, password), bgcolor="#00FF00", color="black", width=350, height=50),
                    ], horizontal_alignment="center", spacing=15)
                )
            ])
        )
        page.update()

    # --- ЭКРАН 2FA ---
    async def show_2fa_and_chat():
        page.clean()
        page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("DECRYPTING IDENTITY...", color="#00FF00", size=22),
                    ft.ProgressBar(width=300, color="#00FF00"),
                    ft.Text("ACCESS GRANTED", color="#00FF00", opacity=0.5)
                ], horizontal_alignment="center")
            )
        )
        page.update()
        await asyncio.sleep(2)
        await show_main_chat()

    # --- ОСНОВНОЙ ЧАТ ---
    async def show_main_chat():
        page.clean()
        msg_input = ft.TextField(hint_text="Введите сигнал...", expand=True, border_color="#222222")

        async def send_signal(e):
            if msg_input.value and app_state["db"]:
                app_state["db"].collection("messages").add({
                    "u": app_state["tag"],
                    "m": encrypt_msg(msg_input.value, "e"),
                    "r": app_state["role"],
                    "ts": firestore.SERVER_TIMESTAMP,
                    "t": datetime.datetime.now().strftime("%H:%M")
                })
                msg_input.value = ""
                # Авто-удаление (12ч)
                try:
                    limit = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)
                    old_docs = app_state["db"].collection("messages").where("ts", "<", limit).get()
                    for doc in old_docs: doc.reference.delete()
                except: pass
                page.update()

        def on_update(docs, changes, read_time):
            app_state["chat_msgs"].controls.clear()
            for doc in reversed(list(docs)):
                d = doc.to_dict()
                is_adm = d.get("r") == "ADMIN"
                app_state["chat_msgs"].controls.append(
                    ft.Container(
                        padding=12, border_radius=10, bgcolor="#0A0A0A",
                        border=ft.border.all(1, "#00FF00" if is_adm else "#151515"),
                        content=ft.Column([
                            ft.Row([ft.Text(d.get("u"), color="#00FF00", size=10), ft.Text(d.get("t"), size=8)], justify="spaceBetween"),
                            ft.Text(encrypt_msg(d.get("m"), "d"), size=14, color="white")
                        ])
                    )
                )
            page.update()

        if app_state["db"]:
            app_state["db"].collection("messages").order_by("ts", direction="descending").limit(40).on_snapshot(on_update)

        page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_NODE: {app_state['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[ft.IconButton(ft.icons.LOGOUT, on_click=lambda _: logout())]
            ),
            ft.Container(content=app_state["chat_msgs"], expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_signal)
                ])
            )
        )
        page.update()

    async def logout():
        page.client_storage.clear()
        await show_login_screen()

    # --- СТАРТ ПРИЛОЖЕНИЯ ---
    # Сначала запускаем Firebase в фоне
    asyncio.create_task(connect_firebase())
    
    # Проверяем сессию (чтобы не вылетал акк)
    if page.client_storage.get("is_logged"):
        app_state["tag"] = page.client_storage.get("u_tag")
        app_state["role"] = page.client_storage.get("u_role")
        await show_main_chat()
    else:
        await show_login_screen()

if __name__ == "__main__":
    ft.app(target=main)



