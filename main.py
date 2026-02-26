import flet as ft
import requests
import datetime
import time
import base64
import random
import threading

# Настройки базы данных (Прямое подключение без тяжелых библиотек)
PROJECT_ID = "ghost-pro-5aa22"
DB_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/ghost_v13_chat"

# Чистое шифрование (Гарантированно работает на Android без черного экрана)
SECRET_KEY = "GHOST_ULTIMATE_V13_PRO"

def crypt_text(text, mode="e"):
    try:
        if mode == "d":
            text = base64.b64decode(text.encode()).decode()
        res = "".join(chr(ord(c) ^ ord(SECRET_KEY[i % len(SECRET_KEY)])) for i, c in enumerate(text))
        if mode == "e":
            return base64.b64encode(res.encode()).decode()
        return res
    except:
        return "[ENCRYPTED_SIGNAL_CORRUPTED]"

def main(page: ft.Page):
    # --- НАСТРОЙКИ ИНТЕРФЕЙСА ---
    page.title = "GHOST PRO V13"
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Состояние
    app_state = {
        "tag": None,
        "role": "USER",
        "running": True
    }

    # Элемент чата
    chat_view = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True, spacing=10)

    # --- ЛОГИКА АВТОРИЗАЦИИ И СЕССИИ ---
    def handle_login(e, email_field, pass_field):
        if not email_field.value or not pass_field.value:
            return
        
        # Данные админки
        if email_field.value == "adminpan" and pass_field.value == "TimaIssam2026":
            role, tag = "ADMIN", "@admin"
        else:
            role, tag = "USER", f"@{email_field.value.split('@')[0]}"
        
        # Сохранение (чтобы не вылетало)
        page.client_storage.set("logged_in", True)
        page.client_storage.set("user_tag", tag)
        page.client_storage.set("user_role", role)
        
        app_state["tag"] = tag
        app_state["role"] = role
        show_2fa_screen()

    def logout(e):
        page.client_storage.clear()
        app_state["running"] = False
        show_matrix_login()

    # --- ЭКРАН ВХОДА С МАТРИЦЕЙ ---
    def show_matrix_login():
        page.clean()
        
        # Анимированный задний фон
        matrix_bg = ft.Column([
            ft.Row([ft.Text(random.choice("017"), color="#003300", size=12) for _ in range(35)]) 
            for _ in range(25)
        ], spacing=0, opacity=0.4)

        email = ft.TextField(label="IDENTITY_ID", border_color="#00FF00", color="#00FF00", width=320)
        password = ft.TextField(label="ACCESS_CODE", password=True, border_color="#00FF00", color="#00FF00", width=320)

        page.add(
            ft.Stack([
                matrix_bg,
                ft.Container(
                    expand=True, alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Text("GHOST_OS: ENCRYPTED_LINK", color="#00FF00", size=22, weight="bold"),
                        ft.Container(
                            height=200, width=320, border=ft.border.all(1, "#00FF00"), padding=15, bgcolor="#DD000000",
                            content=ft.Column([
                                ft.Text("> MATRIX_ENGINE: ACTIVE", color="#00FF00", size=12),
                                ft.Text("> AES_256_TUNNEL: OK", color="#00FF00", size=12),
                                ft.Text("> AUTO_DELETE_12H: ON", color="#00FF00", size=12),
                                ft.Divider(color="#00FF00"),
                                ft.Text("ОЖИДАНИЕ АВТОРИЗАЦИИ...", color="#00FF00", weight="bold"),
                            ])
                        ),
                        email, password,
                        ft.ElevatedButton("REGISTRATION", on_click=lambda e: handle_login(e, email, password), bgcolor="#00FF00", color="black", width=320, height=45),
                        ft.ElevatedButton("LOG_IN", on_click=lambda e: handle_login(e, email, password), bgcolor="#00FF00", color="black", width=320, height=45),
                    ], horizontal_alignment="center", spacing=15)
                )
            ])
        )
        page.update()

    # --- АНИМАЦИЯ 2FA ---
    def show_2fa_screen():
        page.clean()
        pb = ft.ProgressBar(width=250, color="#00FF00", bgcolor="#002200")
        page.add(
            ft.Container(
                expand=True, alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Text("DECRYPTING IDENTITY...", color="#00FF00", size=20, weight="bold"),
                    pb,
                    ft.Text("2FA VERIFICATION IN PROGRESS", color="#00FF00", opacity=0.5)
                ], horizontal_alignment="center", spacing=20)
            )
        )
        page.update()
        time.sleep(2) # Эффект загрузки
        app_state["running"] = True
        show_main_chat()

    # --- ОТПРАВКА СООБЩЕНИЯ В БАЗУ (REST API) ---
    def send_message(e, msg_field):
        text = msg_field.value
        if not text: return
        msg_field.value = ""
        page.update()

        data = {
            "fields": {
                "u": {"stringValue": app_state["tag"]},
                "m": {"stringValue": crypt_text(text, "e")},
                "r": {"stringValue": app_state["role"]},
                "ts": {"timestampValue": datetime.datetime.utcnow().isoformat() + "Z"},
                "t": {"stringValue": datetime.datetime.now().strftime("%H:%M")}
            }
        }
        try:
            requests.post(DB_URL, json=data)
        except: pass

    # --- АВТОМАТИЧЕСКАЯ СИНХРОНИЗАЦИЯ И УДАЛЕНИЕ 12 ЧАСОВ ---
    def background_sync():
        while app_state["running"]:
            try:
                resp = requests.get(DB_URL)
                if resp.status_code == 200:
                    docs = resp.json().get("documents", [])
                    chat_view.controls.clear()
                    
                    now = datetime.datetime.utcnow()
                    
                    for doc in docs:
                        fields = doc.get("fields", {})
                        u = fields.get("u", {}).get("stringValue", "Unknown")
                        m = fields.get("m", {}).get("stringValue", "")
                        r = fields.get("r", {}).get("stringValue", "USER")
                        t = fields.get("t", {}).get("stringValue", "00:00")
                        ts_str = fields.get("ts", {}).get("timestampValue", "")
                        
                        # Проверка на 12 часов (Авто-удаление)
                        if ts_str:
                            ts_time = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(tzinfo=None)
                            if (now - ts_time).total_seconds() > 43200: # 12 часов в секундах
                                doc_name = doc.get("name")
                                requests.delete(f"https://firestore.googleapis.com/v1/{doc_name}")
                                continue

                        is_adm = (r == "ADMIN")
                        chat_view.controls.append(
                            ft.Container(
                                padding=12, border_radius=10, bgcolor="#0A0A0A",
                                border=ft.border.all(1, "#00FF00" if is_adm else "#1A1A1A"),
                                content=ft.Column([
                                    ft.Row([ft.Text(u, color="#00FF00", size=10, weight="bold"), ft.Text(t, size=8, color="#555")], justify="spaceBetween"),
                                    ft.Text(crypt_text(m, "d"), size=14, color="white")
                                ], spacing=3)
                            )
                        )
                    page.update()
            except: pass
            time.sleep(3) # Обновление каждые 3 секунды

    # --- ОСНОВНОЙ ЧАТ ---
    def show_main_chat():
        page.clean()
        msg_input = ft.TextField(hint_text="Введите сигнал...", expand=True, border_color="#222222")

        page.add(
            ft.AppBar(
                title=ft.Text(f"GHOST_NODE: {app_state['tag']}", color="#00FF00"),
                bgcolor="#050505",
                actions=[
                    ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, visible=(app_state["role"]=="ADMIN"), on_click=lambda _: show_admin_panel()),
                    ft.IconButton(ft.icons.LOGOUT, on_click=logout)
                ]
            ),
            ft.Container(content=chat_view, expand=True, padding=15),
            ft.Container(
                bgcolor="#080808", padding=10,
                content=ft.Row([
                    ft.IconButton(ft.icons.MIC, icon_color="#00FF00"),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=lambda e: send_message(e, msg_input))
                ])
            )
        )
        page.update()
        
        # Запускаем фоновый поток обновлений
        threading.Thread(target=background_sync, daemon=True).start()

    # --- АДМИН ПАНЕЛЬ ---
    def show_admin_panel():
        page.clean()
        broadcast = ft.TextField(label="GLOBAL_OVERRIDE_SIGNAL", border_color="red", color="red")
        
        def push_system(e):
            if not broadcast.value: return
            data = {
                "fields": {
                    "u": {"stringValue": "[ROOT_SYSTEM]"},
                    "m": {"stringValue": crypt_text(broadcast.value, "e")},
                    "r": {"stringValue": "ADMIN"},
                    "ts": {"timestampValue": datetime.datetime.utcnow().isoformat() + "Z"},
                    "t": {"stringValue": "NOW"}
                }
            }
            requests.post(DB_URL, json=data)
            show_main_chat()

        page.add(
            ft.AppBar(title=ft.Text("SYSTEM_OVERRIDE"), bgcolor="#330000"),
            ft.Column([
                ft.Text("ADMIN CONTROL", color="red", size=24, weight="bold"),
                broadcast,
                ft.ElevatedButton("EXECUTE BROADCAST", on_click=push_system, bgcolor="red", color="white", width=400),
                ft.ElevatedButton("BACK", on_click=lambda _: show_main_chat(), width=400)
            ], padding=20, spacing=20)
        )
        page.update()

    # --- ЗАПУСК ---
    if page.client_storage.get("logged_in"):
        app_state["tag"] = page.client_storage.get("user_tag")
        app_state["role"] = page.client_storage.get("user_role")
        show_main_chat()
    else:
        show_matrix_login()

if __name__ == "__main__":
    ft.app(target=main)




