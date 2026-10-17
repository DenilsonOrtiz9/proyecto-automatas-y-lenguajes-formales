import customtkinter as ctk
import re
import random
import string
import unicodedata

# Configuración inicial de CustomTkinter (Tema Vibrante Cyber-Tech)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ValidadorLexicoAutomatas:
    def __init__(self):
        # Alfabetos formales
        self.alfabeto_letras = string.ascii_letters
        self.alfabeto_pass_letras = string.ascii_letters + "ñÑ"
        self.alfabeto_digitos = string.digits
        self.alfabeto_simbolos = "!#$%&'*+-/=?^_`{|}~"
        self.regex_pass = r"^[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ0-9!#$%&'*+\-/=?^_`{|}~\.]{8,64}$"

        # Matriz de transición AFD para Correo (con soporte para Subdominios y Dominios Compuestos)
        self.afd_correo = {
            'q0': {'L': 'q1', 'D': 'q1', 'S': 'q1', '-': 'q1'}, 
            'q1': {'L': 'q1', 'D': 'q1', 'S': 'q1', '-': 'q1', '.': 'q_punto_local', '@': 'q2'},
            'q_punto_local': {'L': 'q1', 'D': 'q1', 'S': 'q1', '-': 'q1'}, 
            'q2': {'L': 'q3', 'D': 'q3'}, 
            'q3': {'L': 'q3', 'D': 'q3', '-': 'q_guion', '.': 'q4'},
            'q_guion': {'L': 'q3', 'D': 'q3'}, 
            'q4': {'L': 'q5', 'D': 'q3'}, 
            'q5': {'L': 'q6', 'D': 'q3', '-': 'q_guion', '.': 'q4'}, 
            'q6': {'L': 'q6', 'D': 'q3', '-': 'q_guion', '.': 'q4'}  
        }
        self.estados_aceptacion_correo = {'q6'}

    def _clasificar_caracter(self, char):
        if char in ['.', '@', '-']: return char
        if char in self.alfabeto_letras: return 'L'
        if char in self.alfabeto_digitos: return 'D'
        if char in self.alfabeto_simbolos: return 'S'
        return 'INVALIDO'

    def validar_correo_afd(self, correo):
        estado_actual = 'q0'
        reporte = f"Evaluando léxico: {correo}\n"
        
        for i, char in enumerate(correo):
            tipo = self._clasificar_caracter(char)
            if tipo == 'INVALIDO':
                return False, reporte + f"❌ Falla léxica: Carácter '{char}' no permitido por RFC 5322."
            
            if tipo in self.afd_correo.get(estado_actual, {}):
                estado_anterior = estado_actual
                estado_actual = self.afd_correo[estado_actual][tipo]
                reporte += f"[{char}] Transición: {estado_anterior} -> {estado_actual}\n"
            else:
                if char == '.' and estado_actual == 'q_punto_local':
                    return False, reporte + "❌ Falla sintáctica: Puntos consecutivos en parte local."
                if char == '@' and estado_actual != 'q1':
                    return False, reporte + "❌ Falla sintáctica: Delimitador '@' mal posicionado o duplicado."
                if char == '-' and estado_actual in ['q2', 'q4']:
                    return False, reporte + "❌ Falla sintáctica: El dominio o subdominio no puede iniciar con guion."
                if char == '.' and estado_actual in ['q2', 'q4', 'q_guion']:
                    return False, reporte + "❌ Falla sintáctica: Formato de dominio inválido (puntos consecutivos o posición indebida)."
                if estado_actual in ['q2', 'q3', 'q4', 'q5', 'q6', 'q_guion'] and tipo == 'S':
                    return False, reporte + f"❌ Falla sintáctica: El carácter especial '{char}' no está permitido en el dominio."
                return False, reporte + f"❌ Falla sintáctica al leer '{char}'."
                
        if estado_actual in self.estados_aceptacion_correo:
            return True, reporte + "✅ VÁLIDO: Alcanzó el estado de aceptación (q6)."
        if estado_actual in ['q4', 'q5']:
            return False, reporte + "❌ INVÁLIDO: El Dominio de Nivel Superior (TLD) debe tener al menos 2 letras."
        if estado_actual == 'q_guion':
            return False, reporte + "❌ INVÁLIDO: Las etiquetas del dominio no pueden terminar con guion."
        if estado_actual == 'q_punto_local':
            return False, reporte + "❌ INVÁLIDO: La parte local no puede terminar en punto."
        return False, reporte + "❌ INVÁLIDO: Estructura incompleta. Falta el Dominio de Nivel Superior (TLD)."

    def validar_contrasena(self, password):
        if not re.match(self.regex_pass, password):
            if len(password) < 8 or len(password) > 64:
                return False, f"❌ Falla de longitud: {len(password)} caracteres. Requerido: 8 a 64."
            return False, "❌ Falla léxica: Contiene caracteres prohibidos o espacios."
            
        longitud = len(password)
        if longitud >= 15: nivel = "Fuerte (NIST Factor Único)"
        elif longitud >= 12: nivel = "Media"
        else: nivel = "Baja (Mínimo Permitido)"
            
        return True, f"✅ CONTRASEÑA VÁLIDA.\nNivel de seguridad: {nivel}"

    def _normalizar_texto(self, texto):
        if not texto: return ""
        descompuesto = unicodedata.normalize('NFD', texto)
        sin_tildes = ''.join(c for c in descompuesto if unicodedata.category(c) != 'Mn')
        sin_tildes = sin_tildes.replace('ñ', 'n').replace('Ñ', 'N')
        limpio = re.sub(r'[^a-zA-Z0-9\s._-]', '', sin_tildes).strip().lower()
        return limpio

    NOMBRES_SEED = ['alex', 'sofia', 'carlos', 'lucia', 'mateo', 'elena', 'david', 'valeria', 'diego', 'samuel', 'camila', 'leo', 'adrian', 'paula', 'gabriel', 'fernando', 'daniela', 'javier']
    APELLIDOS_SEED = ['torres', 'vega', 'silva', 'rojas', 'castro', 'morales', 'vargas', 'navarro', 'rios', 'mendoza', 'guerrero', 'cordero', 'reyes', 'moran', 'delgado', 'soto']
    ROLES_SEED = ['dev', 'admin', 'contact', 'ventas', 'soporte', 'tech', 'cloud', 'qa', 'ops', 'info', 'staff', 'desk', 'lab', 'pro', 'corp', 'hub', 'inbox']

    def _limpiar_local(self, s):
        s = re.sub(r'\.+', '.', s)
        s = re.sub(r'[-_]{2,}', '-', s)
        s = s.strip('.-_')
        return s

    def _generar_parte_local_aleatoria(self):
        estado = 'q0'
        cadena = ""
        while True:
            opciones = ['L', 'D']
            if len(cadena) > 1 and not cadena.endswith('.'): opciones.append('.')
            eleccion = random.choice(opciones)
            if eleccion == 'L': char = random.choice(self.alfabeto_letras).lower()
            elif eleccion == 'D': char = random.choice(self.alfabeto_digitos)
            else: char = '.'
            tipo = self._clasificar_caracter(char)
            if tipo in self.afd_correo.get(estado, {}):
                cadena += char
                estado = self.afd_correo[estado][tipo]
            if len(cadena) >= random.randint(5, 9) and estado == 'q1': break
        return cadena

    def _generar_lista_locales(self, palabras_raw, cantidad=12):
        limpio = self._normalizar_texto(palabras_raw)
        palabras = [p for p in re.split(r'[\s._-]+', limpio) if p]
        patrones = []
        
        if not palabras:
            for _ in range(max(cantidad * 4, 30)):
                n = random.choice(self.NOMBRES_SEED)
                a = random.choice(self.APELLIDOS_SEED)
                r = random.choice(self.ROLES_SEED)
                num = random.randint(1, 99)
                year = random.choice([24, 25, 26, 2025, 2026])
                pats = [
                    f"{n}.{a}", f"{n[0]}{a}", f"{n}.{a}{num}", f"{n}_{a}", f"{n}-{a}",
                    f"{n}.{r}", f"{r}.{n}", f"{n}{year}", f"{a}.{n}", f"{n[0]}.{a}{num}",
                    f"{n}_{r}_{num}", f"{r}_{a}", f"{n}.{a}.{r}", f"{n}{num}", f"{n}_{num}"
                ]
                patrones.extend(pats)
        elif len(palabras) == 1:
            w = palabras[0]
            num_s = str(random.randint(1, 99))
            num_s2 = str(random.randint(100, 999))
            year = str(random.choice([24, 25, 26, 2025, 2026]))
            r = random.choice(self.ROLES_SEED)
            a = random.choice(self.APELLIDOS_SEED)
            patrones = [
                w,
                f"{w}.{num_s}", f"{w}_{num_s}", f"{w}-{num_s}", f"{w}{num_s}",
                f"{w}{num_s2}", f"{w}.{year}", f"{w}_{year}", f"{w}{year}",
                f"{w}.{r}", f"{r}.{w}", f"{w}_{r}", f"{w}-{r}",
                f"{w}.dev", f"{w}.pro", f"{w}.oficial", f"{w}.work",
                f"{w}.team", f"{w}.corp", f"{w}.io", f"{w}.hq",
                f"soy.{w}", f"hola.{w}", f"contact.{w}", f"staff.{w}",
                f"info.{w}", f"soporte.{w}", f"team.{w}",
                f"{w}.{a}", f"{w}_{a}", f"{w}-{a}",
                f"{w}.01", f"{w}123", f"{w}2026"
            ]
        elif len(palabras) == 2:
            w1, w2 = palabras[0], palabras[1]
            num_s = str(random.randint(1, 99))
            year = str(random.choice([24, 25, 26, 2025, 2026]))
            r = random.choice(self.ROLES_SEED)
            patrones = [
                f"{w1}.{w2}", f"{w1}_{w2}", f"{w1}-{w2}", f"{w1}{w2}",
                f"{w1[0]}{w2}", f"{w1[0]}.{w2}", f"{w1[0]}_{w2}", f"{w1[0]}-{w2}",
                f"{w1}.{w2[0]}", f"{w1}_{w2[0]}", f"{w1}{w2[0]}",
                f"{w2}.{w1}", f"{w2}_{w1}", f"{w2}-{w1}", f"{w2}{w1}",
                f"{w2[0]}{w1}", f"{w2}.{w1[0]}",
                f"{w1}.{w2}{num_s}", f"{w1}_{w2}_{num_s}", f"{w1}{w2}{num_s}",
                f"{w1[0]}{w2}{num_s}", f"{w1[0]}.{w2}.{num_s}",
                f"{w1}.{w2}.{year}", f"{w1[0]}{w2}{year}", f"{w1}.{w2}{year}",
                f"{w1}.{w2}.{r}", f"{r}.{w1}.{w2}", f"{w1}_{w2}_{r}",
                f"{w1}.{w2}-work", f"{w1}.{w2}.dev", f"{w1}.{w2}.pro",
                f"{w1}.{w2}.qa", f"{w1[0]}.{w2}.it", f"{w1}.{w2[0]}.{num_s}",
                f"{w1[0]}{w2[0]}", f"{w1[0]}.{w2[0]}", f"{w1[0]}{w2[0]}{year}",
                f"soy.{w1}.{w2}", f"contact.{w1}.{w2}", f"team.{w1}.{w2}"
            ]
        else:
            w1, w2, w3 = palabras[0], palabras[1], palabras[2]
            w4 = palabras[3] if len(palabras) >= 4 else ""
            num_s = str(random.randint(1, 99))
            year = str(random.choice([24, 25, 26, 2025, 2026]))
            r = random.choice(self.ROLES_SEED)
            patrones = [
                f"{w1}.{w3}", f"{w1[0]}{w3}", f"{w1[0]}.{w3}",
                f"{w1}.{w2}.{w3}", f"{w1}_{w2}_{w3}", f"{w1}-{w2}-{w3}",
                f"{w1}{w2}{w3}", f"{w1[0]}{w2[0]}{w3}", f"{w1[0]}.{w2[0]}.{w3}",
                f"{w1}.{w2[0]}.{w3}", f"{w1[0]}.{w2}.{w3}",
                f"{w2}.{w3}", f"{w2[0]}{w3}", f"{w2[0]}.{w3}",
                f"{w3}.{w1}", f"{w3}.{w1}.{w2}",
                f"{w1}.{w3}{num_s}", f"{w1[0]}{w3}{num_s}",
                f"{w1[0]}{w2[0]}{w3}{num_s}", f"{w1}.{w2}.{w3}{num_s}",
                f"{w1}.{w3}.{year}", f"{w1[0]}{w3}{year}",
                f"{w1}.{w3}.{r}", f"{w1[0]}{w2[0]}{w3}.{r}",
                f"{w1}.{w2[0]}{w3[0]}", f"{w1[0]}{w2[0]}{w3[0]}",
                f"{w1}.{w2}_{w3}", f"{w1}.{w2}-{w3}"
            ]
            if w4:
                patrones.extend([
                    f"{w1}.{w3}.{w4}", f"{w1[0]}{w3}{w4[0]}",
                    f"{w1}.{w3}.{w4[0]}", f"{w1[0]}{w2[0]}.{w3}.{w4[0]}",
                    f"{w1[0]}{w2[0]}{w3[0]}{w4[0]}", f"{w3}.{w4}.{w1}",
                    f"{w1}_{w3}_{w4}", f"{w1}.{w2}.{w3}.{w4}"
                ])

        limpios = []
        for p in patrones:
            cand = self._limpiar_local(p)
            if cand and cand not in limpios:
                limpios.append(cand)
        random.shuffle(limpios)
        return limpios[:cantidad]

    def _generar_dominio_aleatorio(self):
        estado = 'q2'
        dominio_str = ""
        while True:
            opciones = list(self.afd_correo[estado].keys())
            if estado == 'q6':
                tld = dominio_str.split('.')[-1]
                if len(tld) >= 2 and random.random() < 0.7: break
            if 'L' in opciones and random.random() < 0.75: eleccion = 'L'
            elif '.' in opciones and '.' not in dominio_str and len(dominio_str) >= 4: eleccion = '.'
            else: eleccion = random.choice(opciones)
            if eleccion == 'L': char = random.choice(self.alfabeto_letras).lower()
            elif eleccion == 'D': char = random.choice(self.alfabeto_digitos)
            elif eleccion == '-': char = '-'
            elif eleccion == '.': char = '.'
            else: char = eleccion
            dominio_str += char
            estado = self.afd_correo[estado][eleccion]
            if len(dominio_str) > 20 and estado == 'q6': break
        return dominio_str

    def generar_variantes_correo(self, palabras_base="", dominio="", cantidad=6):
        dominio = dominio.strip() if dominio else ""
        if dominio in ["", "(Aleatorio)"]:
            dom = self._generar_dominio_aleatorio()
        else:
            dom = self._normalizar_texto(dominio).replace(' ', '').strip('.-_')
            if '.' not in dom: dom += ".com"

        locales = self._generar_lista_locales(palabras_base, cantidad=max(cantidad * 4, 40))
        variantes = []
        for loc in locales:
            correo = f"{loc}@{dom}"
            es_valido, _ = self.validar_correo_afd(correo)
            if es_valido and correo not in variantes:
                variantes.append(correo)
            if len(variantes) == cantidad:
                break
        
        while len(variantes) < cantidad:
            loc_extra = self._generar_parte_local_aleatoria()
            correo = f"{loc_extra}@{dom}"
            if correo not in variantes:
                variantes.append(correo)

        return variantes

    def generar_correo_guiado(self, palabras_base="", dominio="", subdominio=""):
        variantes = self.generar_variantes_correo(palabras_base=palabras_base, dominio=dominio, cantidad=1)
        if variantes:
            return variantes[0]
        parte_local = self._generar_parte_local_aleatoria()
        dom = "gmail.com" if not dominio or dominio == "(Aleatorio)" else dominio
        return f"{parte_local}@{dom}"

    def generar_contrasena_guiada(self, longitud=16):
        try:
            longitud = int(longitud)
            if longitud < 8: longitud = 8
            elif longitud > 64: longitud = 64
        except (ValueError, TypeError):
            longitud = 16
        caracteres = self.alfabeto_pass_letras + self.alfabeto_digitos + self.alfabeto_simbolos
        return "".join(random.choice(caracteres) for _ in range(longitud))


# --- INTERFAZ MODERNA CON CUSTOMTKINTER (PALETA VIBRANTE CYBER-TECH) ---
class AppCredenciales(ctk.CTk):
    # Colores Vibrantes Cyber-Tech
    C_BG = "#080c16"              # Deep Obsidian
    C_CARD = "#111726"            # Dark Navy Glass Card
    C_CARD_BORDER = "#24324f"     # Borde suave iluminado
    C_INPUT_BG = "#070b14"        # Input ultra-dark
    C_INPUT_BORDER = "#2a3b5c"    # Borde de input
    
    # Acentos de color vibrantes
    C_INDIGO = "#6366f1"          # Electric Indigo (Primario)
    C_INDIGO_HOVER = "#4f46e5"
    C_CYAN = "#0ea5e9"            # Neon Cyan (Acción / Auditoría)
    C_CYAN_HOVER = "#0284c7"
    C_PURPLE = "#a855f7"          # Neon Purple (Contraseña)
    C_PURPLE_HOVER = "#9333ea"
    C_EMERALD = "#10b981"         # Emerald Green (Éxito)
    C_ROSE = "#f43f5e"            # Rose Red (Error)

    def __init__(self):
        super().__init__()
        self.validador = ValidadorLexicoAutomatas()

        # Configuración de ventana
        self.title("Sistema de Credenciales Seguras — AFD & Análisis Léxico")
        self.geometry("900x820")
        self.minsize(820, 700)
        self.configure(fg_color=self.C_BG)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.construir_encabezado()
        self.construir_cuerpo_tabs()

    def construir_encabezado(self):
        header_frame = ctk.CTkFrame(self, corner_radius=14, fg_color=self.C_CARD, 
                                    border_color=self.C_CARD_BORDER, border_width=1)
        header_frame.grid(row=0, column=0, padx=20, pady=(16, 12), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Columna Izquierda: Título e Insignias de Tecnología
        info_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_box.grid(row=0, column=0, padx=18, pady=14, sticky="w")

        lbl_titulo = ctk.CTkLabel(info_box, text="⚡ SISTEMA DE CREDENCIALES SEGURAS 🔐", 
                                  font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                                  text_color="#ffffff")
        lbl_titulo.pack(anchor="w")

        # Insignias / Tags visuales en el encabezado
        chips_frame = ctk.CTkFrame(info_box, fg_color="transparent")
        chips_frame.pack(anchor="w", pady=(6, 0))

        self.crear_chip(chips_frame, "🧠 AFD RFC 5322", "#1e1b4b", "#a5b4fc")
        self.crear_chip(chips_frame, "🛡️ NIST SP 800-63B", "#064e3b", "#6ee7b7")
        self.crear_chip(chips_frame, "⚡ Tiempo Real", "#082f49", "#7dd3fc")

        # Columna Derecha: Switch Modo Oscuro / Claro
        switch_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        switch_frame.grid(row=0, column=1, padx=18, pady=14, sticky="e")

        self.switch_tema = ctk.CTkSwitch(switch_frame, text="Modo Claro", 
                                         command=self.toggle_tema,
                                         progress_color=self.C_INDIGO,
                                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.switch_tema.pack()

    def crear_chip(self, parent, texto, bg_col, text_col):
        chip = ctk.CTkFrame(parent, fg_color=bg_col, corner_radius=6)
        chip.pack(side="left", padx=(0, 6))
        ctk.CTkLabel(chip, text=texto, font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                     text_color=text_col).pack(padx=8, pady=2)

    def toggle_tema(self):
        if self.switch_tema.get() == 1:
            ctk.set_appearance_mode("light")
            self.switch_tema.configure(text="Modo Oscuro")
        else:
            ctk.set_appearance_mode("dark")
            self.switch_tema.configure(text="Modo Claro")

    def construir_cuerpo_tabs(self):
        self.tabview = ctk.CTkTabview(self, 
                                     corner_radius=14,
                                     fg_color=self.C_CARD,
                                     segmented_button_fg_color="#090e1a",
                                     segmented_button_selected_color=self.C_INDIGO,
                                     segmented_button_selected_hover_color=self.C_INDIGO_HOVER,
                                     segmented_button_unselected_color="#151d31",
                                     segmented_button_unselected_hover_color="#1f2a47",
                                     text_color="#ffffff")
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="nsew")

        self.tab_validar = self.tabview.add("⚡ Validar en Tiempo Real")
        self.tab_gen_correo = self.tabview.add("📧 Generador de Correos (AFD)")
        self.tab_gen_pass = self.tabview.add("🔐 Generador de Contraseñas (NIST)")

        self.construir_tab_validacion(self.tab_validar)
        self.construir_tab_gen_correo(self.tab_gen_correo)
        self.construir_tab_gen_password(self.tab_gen_pass)

    def construir_tab_validacion(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        # --- TARJETA DE ENTRADAS ---
        card_entradas = ctk.CTkFrame(tab, corner_radius=12, fg_color=self.C_CARD, 
                                    border_color=self.C_CARD_BORDER, border_width=1)
        card_entradas.grid(row=0, column=0, padx=12, pady=(12, 10), sticky="ew")
        card_entradas.grid_columnconfigure(0, weight=1)

        # 1. Correo Electrónico
        lbl_correo = ctk.CTkLabel(card_entradas, text="✉️ Correo Electrónico (RFC 5322 & Dominios Compuestos):", 
                                  font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                  text_color="#38bdf8")
        lbl_correo.pack(anchor="w", padx=16, pady=(14, 4))
        
        self.entry_correo = ctk.CTkEntry(card_entradas, placeholder_text="ej. usuario@sub.empresa.com.mx", 
                                         height=40, corner_radius=8, font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                                         fg_color=self.C_INPUT_BG, border_color=self.C_INPUT_BORDER, text_color="#ffffff")
        self.entry_correo.pack(fill="x", padx=16, pady=(0, 6))
        self.entry_correo.bind("<KeyRelease>", self.analizar_credenciales)

        # Badge interactivo de estado de correo
        self.badge_correo = ctk.CTkLabel(card_entradas, 
                                         text="⚪ Ingrese un correo para analizar el recorrido del autómata", 
                                         corner_radius=6, height=30, fg_color="#151d31",
                                         text_color="#94a3b8",
                                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.badge_correo.pack(fill="x", padx=16, pady=(0, 12))

        # 2. Contraseña
        lbl_pass = ctk.CTkLabel(card_entradas, text="🔑 Contraseña Segura (NIST SP 800-63B):", 
                                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                text_color="#c084fc")
        lbl_pass.pack(anchor="w", padx=16, pady=(2, 4))
        
        self.entry_pass = ctk.CTkEntry(card_entradas, placeholder_text="Ingrese contraseña para análisis de robustez...", 
                                       show="*", height=40, corner_radius=8, font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                                       fg_color=self.C_INPUT_BG, border_color=self.C_INPUT_BORDER, text_color="#ffffff")
        self.entry_pass.pack(fill="x", padx=16, pady=(0, 8))
        self.entry_pass.bind("<KeyRelease>", self.analizar_credenciales)

        # Fila de control de contraseña: Switch + Barra de fuerza
        fila_pass = ctk.CTkFrame(card_entradas, fg_color="transparent")
        fila_pass.pack(fill="x", padx=16, pady=(2, 6))
        fila_pass.grid_columnconfigure(1, weight=1)

        self.switch_show_pass = ctk.CTkSwitch(fila_pass, text="Mostrar caracteres", 
                                              command=self.toggle_password,
                                              progress_color=self.C_PURPLE,
                                              font=ctk.CTkFont(family="Segoe UI", size=11))
        self.switch_show_pass.grid(row=0, column=0, sticky="w", padx=(0, 16))

        # Barra de robustez con altura y bordes suaves
        self.prog_pass = ctk.CTkProgressBar(fila_pass, height=12, corner_radius=6, 
                                            fg_color="#151d31", border_color=self.C_CARD_BORDER, border_width=1)
        self.prog_pass.set(0)
        self.prog_pass.grid(row=0, column=1, sticky="ew")

        self.lbl_nivel_pass = ctk.CTkLabel(card_entradas, text="⚪ Ingrese una contraseña para evaluar robustez", 
                                           text_color="#94a3b8",
                                           font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"))
        self.lbl_nivel_pass.pack(anchor="w", padx=16, pady=(0, 14))

        # --- PANEL DE DIAGNÓSTICO Y MONITOR FORMAL (AFD) ---
        panel_traza = ctk.CTkFrame(tab, corner_radius=12, fg_color=self.C_CARD, 
                                   border_color=self.C_CARD_BORDER, border_width=1)
        panel_traza.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        panel_traza.grid_columnconfigure(0, weight=1)
        panel_traza.grid_rowconfigure(1, weight=1)

        # Barra superior del Inspector (Clean DevTools / Monitor Header)
        head_traza = ctk.CTkFrame(panel_traza, height=44, corner_radius=10, fg_color="#0a0f1d",
                                  border_color="#1e293b", border_width=1)
        head_traza.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        head_traza.grid_columnconfigure(1, weight=1)

        box_left = ctk.CTkFrame(head_traza, fg_color="transparent")
        box_left.grid(row=0, column=0, padx=14, pady=8, sticky="w")

        lbl_traza_icon = ctk.CTkLabel(box_left, text="📊", font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#38bdf8")
        lbl_traza_icon.pack(side="left", padx=(0, 6))

        lbl_traza_title = ctk.CTkLabel(box_left, text="MONITOR DE TRAZABILIDAD Y ESTADOS FORMALES (AFD)", 
                                       font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                       text_color="#f8fafc")
        lbl_traza_title.pack(side="left")

        box_right = ctk.CTkFrame(head_traza, fg_color="transparent")
        box_right.grid(row=0, column=1, padx=12, pady=6, sticky="e")

        self.badge_traza_estado = ctk.CTkLabel(box_right, text="⚪ Listo para Escaneo", 
                                               corner_radius=6, height=26, fg_color="#151d31",
                                               text_color="#94a3b8", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"))
        self.badge_traza_estado.pack(side="left", padx=(0, 8))

        btn_copy = ctk.CTkButton(box_right, text="📋 Copiar Traza", width=95, height=26,
                                 corner_radius=6, fg_color="#1e293b", hover_color="#334155",
                                 text_color="#cbd5e1", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                                 command=self.copiar_traza)
        btn_copy.pack(side="left", padx=(0, 6))

        btn_clear = ctk.CTkButton(box_right, text="🧹 Limpiar", width=75, height=26,
                                  corner_radius=6, fg_color="#1e293b", hover_color="#334155",
                                  text_color="#cbd5e1", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                                  command=self.limpiar_traza)
        btn_clear.pack(side="left")

        # Visor de traza con estilo Dark Code / DevTools Inspector
        self.txt_consola = ctk.CTkTextbox(panel_traza, corner_radius=10, 
                                          font=ctk.CTkFont(family="Consolas", size=11),
                                          text_color="#cbd5e1", fg_color="#070b14",
                                          border_color="#18233c", border_width=1)
        self.txt_consola.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))

        # Barra inferior de estadísticas
        bar_stats = ctk.CTkFrame(panel_traza, height=28, fg_color="transparent")
        bar_stats.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        bar_stats.grid_columnconfigure(0, weight=1)

        self.lbl_stats_traza = ctk.CTkLabel(bar_stats, 
                                            text="Esperando entrada del usuario en los campos superiores...", 
                                            font=ctk.CTkFont(family="Segoe UI", size=10), text_color="#64748b")
        self.lbl_stats_traza.grid(row=0, column=0, sticky="w")

    def construir_tab_gen_correo(self, tab):
        scroll_correo = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_correo.pack(fill="both", expand=True, padx=4, pady=4)

        # --- TARJETA: GENERADOR DE CORREO ---
        card_correo = ctk.CTkFrame(scroll_correo, corner_radius=12, fg_color=self.C_CARD, 
                                   border_color=self.C_CARD_BORDER, border_width=1)
        card_correo.pack(fill="x", padx=12, pady=(12, 12))

        ctk.CTkLabel(card_correo, text="🎲 Generador de Correo Personalizado (Guiado por AFD)", 
                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                     text_color="#38bdf8").pack(anchor="w", padx=18, pady=(16, 4))

        # Palabras base
        ctk.CTkLabel(card_correo, text="👤 Nombres o palabras base (Opcional):", 
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color="#e2e8f0").pack(anchor="w", padx=18, pady=(4, 2))
        
        self.entry_palabras = ctk.CTkEntry(card_correo, placeholder_text="Ej. 'Juan Pérez', 'soporte', 'ventas' (o dejar vacío para aleatorio)",
                                           height=40, corner_radius=8, fg_color=self.C_INPUT_BG, border_color=self.C_INPUT_BORDER)
        self.entry_palabras.pack(fill="x", padx=18, pady=(0, 10))

        # Dominio y TLD
        ctk.CTkLabel(card_correo, text="🌐 Dominio y TLD:", 
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=18, pady=(0, 2))
        self.combo_dominio = ctk.CTkComboBox(card_correo, 
                                             values=["gmail.com", "outlook.com", "yahoo.com", "empresa.com", "universidad.edu.mx", "portal.gob.mx", "servidor.net", "(Aleatorio)"],
                                             height=40, corner_radius=8, fg_color=self.C_INPUT_BG, border_color=self.C_INPUT_BORDER,
                                             button_color=self.C_INDIGO, button_hover_color=self.C_INDIGO_HOVER)
        self.combo_dominio.set("gmail.com")
        self.combo_dominio.pack(fill="x", padx=18, pady=(0, 12))

        # Botón Generar Correo (Vibrante)
        btn_gen_mail = ctk.CTkButton(card_correo, text="🎲 Generar Correo Guiado por AFD", 
                                     height=44, corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                     fg_color=self.C_INDIGO, hover_color=self.C_INDIGO_HOVER,
                                     command=self.generar_correo)
        btn_gen_mail.pack(fill="x", padx=18, pady=(4, 10))

        # Salida del correo con tipografía monoespaciada brillante
        self.salida_correo = ctk.CTkEntry(card_correo, height=44, corner_radius=8, 
                                          font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
                                          justify="center", fg_color=self.C_INPUT_BG, 
                                          border_color="#0ea5e9", text_color="#38bdf8")
        self.salida_correo.pack(fill="x", padx=18, pady=(0, 8))

        # Botones de acción: Copiar y Probar
        fila_acc_mail = ctk.CTkFrame(card_correo, fg_color="transparent")
        fila_acc_mail.pack(fill="x", padx=18, pady=(0, 6))
        fila_acc_mail.grid_columnconfigure(0, weight=1)
        fila_acc_mail.grid_columnconfigure(1, weight=1)

        btn_copy_mail = ctk.CTkButton(fila_acc_mail, text="📋 Copiar al Portapapeles", 
                                      height=36, corner_radius=6, fg_color="#1e293b", hover_color="#334155",
                                      font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                      command=self.copiar_correo)
        btn_copy_mail.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        btn_test_mail = ctk.CTkButton(fila_acc_mail, text="🔍 Probar en Validador AFD", 
                                      height=36, corner_radius=6, fg_color=self.C_CYAN, hover_color=self.C_CYAN_HOVER,
                                      font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                      command=self.enviar_a_validador)
        btn_test_mail.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.lbl_estado_correo = ctk.CTkLabel(card_correo, text="", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_estado_correo.pack(pady=(4, 6))

        # --- PANEL DE VARIANTES Y MÁS COMBINACIONES ---
        self.frame_variantes = ctk.CTkFrame(card_correo, corner_radius=10, fg_color="#070b14", 
                                            border_color="#1e293b", border_width=1)
        self.frame_variantes.pack(fill="x", padx=18, pady=(0, 16))

        fila_head_var = ctk.CTkFrame(self.frame_variantes, fg_color="transparent")
        fila_head_var.pack(fill="x", padx=12, pady=(10, 6))
        fila_head_var.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(fila_head_var, text="💡 Más combinaciones generadas (haz clic para usar):", 
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
                     text_color="#38bdf8").grid(row=0, column=0, sticky="w")

        btn_mas_var = ctk.CTkButton(fila_head_var, text="🔄 Más Variantes", 
                                    width=110, height=28, corner_radius=6,
                                    fg_color="#1e293b", hover_color="#334155",
                                    font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                                    command=self.generar_mas_variantes)
        btn_mas_var.grid(row=0, column=1, sticky="e")

        self.box_pills = ctk.CTkFrame(self.frame_variantes, fg_color="transparent")
        self.box_pills.pack(fill="x", padx=12, pady=(0, 10))
        self.box_pills.grid_columnconfigure((0, 1), weight=1)

        self.botones_variantes = []
        for i in range(6):
            r, c = i // 2, i % 2
            btn_v = ctk.CTkButton(self.box_pills, text="", height=30, corner_radius=6,
                                  fg_color="#0f172a", hover_color="#1e293b",
                                  border_color="#334155", border_width=1,
                                  text_color="#94a3b8", font=ctk.CTkFont(family="Consolas", size=10),
                                  anchor="w")
            btn_v.grid(row=r, column=c, padx=4, pady=3, sticky="ew")
            self.botones_variantes.append(btn_v)

    def fijar_longitud_pass(self, val):
        self.slider_pass.set(val)
        self.actualizar_label_slider(val)

    def construir_tab_gen_password(self, tab):
        scroll_pass = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_pass.pack(fill="both", expand=True, padx=4, pady=4)

        # --- TARJETA: GENERADOR DE CONTRASEÑA ---
        card_pass = ctk.CTkFrame(scroll_pass, corner_radius=12, fg_color=self.C_CARD, 
                                 border_color=self.C_CARD_BORDER, border_width=1)
        card_pass.pack(fill="x", padx=12, pady=(12, 12))

        ctk.CTkLabel(card_pass, text="🔐 Generador de Contraseñas Seguras (NIST SP 800-63B)", 
                     font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                     text_color="#c084fc").pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(card_pass, text="Selecciona la longitud deseada con el slider o mediante los accesos directos:", 
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color="#94a3b8").pack(anchor="w", padx=18, pady=(0, 10))

        # Accesos rápidos de longitud (Presets NIST)
        fila_presets = ctk.CTkFrame(card_pass, fg_color="transparent")
        fila_presets.pack(fill="x", padx=18, pady=(0, 8))
        presets = [("8 (Mínimo NIST)", 8), ("12 (Media)", 12), ("16 (Recomendado)", 16), ("24 (Fuerte)", 24), ("32 (Máxima)", 32)]
        for i, (txt_p, val_p) in enumerate(presets):
            ctk.CTkButton(fila_presets, text=txt_p, height=28, corner_radius=6,
                          fg_color="#182033", hover_color="#2b3650", border_color="#334155", border_width=1,
                          font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                          command=lambda v=val_p: self.fijar_longitud_pass(v)).pack(side="left", padx=(0, 6), expand=True, fill="x")

        # Slider interactivo de longitud
        fila_slider = ctk.CTkFrame(card_pass, fg_color="transparent")
        fila_slider.pack(fill="x", padx=18, pady=(8, 12))
        fila_slider.grid_columnconfigure(1, weight=1)

        self.lbl_slider_val = ctk.CTkLabel(fila_slider, text="Longitud: 16 car. • 🟢 Fuerte (NIST Factor Único)", 
                                           font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                           text_color="#e2e8f0", width=280, anchor="w")
        self.lbl_slider_val.grid(row=0, column=0, sticky="w")

        self.slider_pass = ctk.CTkSlider(fila_slider, from_=8, to=64, number_of_steps=56, 
                                         progress_color="#8b5cf6", button_color="#c084fc", button_hover_color="#e9d5ff",
                                         command=self.actualizar_label_slider)
        self.slider_pass.set(16)
        self.slider_pass.grid(row=0, column=1, sticky="ew")

        # Botón Generar Contraseña (Púrpura Neón)
        btn_gen_pass = ctk.CTkButton(card_pass, text="🔐 Generar Contraseña Segura", 
                                     height=44, corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                     fg_color="#7c3aed", hover_color="#6d28d9",
                                     command=self.generar_pass)
        btn_gen_pass.pack(fill="x", padx=18, pady=(4, 12))

        # Salida de la contraseña
        self.salida_pass = ctk.CTkEntry(card_pass, height=46, corner_radius=8, 
                                        font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
                                        justify="center", fg_color=self.C_INPUT_BG, 
                                        border_color="#a855f7", text_color="#c084fc")
        self.salida_pass.pack(fill="x", padx=18, pady=(0, 10))

        # Badge prominente que indica explícitamente si es segura o no
        self.badge_seguridad_pass = ctk.CTkLabel(
            card_pass, 
            text="⚪ Presione 'Generar Contraseña Segura' para evaluar su nivel de seguridad", 
            corner_radius=8, height=36, fg_color="#151d31",
            text_color="#94a3b8",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        )
        self.badge_seguridad_pass.pack(fill="x", padx=18, pady=(0, 12))

        # Botón Copiar + Botón Probar en Validador
        fila_acc_pass = ctk.CTkFrame(card_pass, fg_color="transparent")
        fila_acc_pass.pack(fill="x", padx=18, pady=(0, 8))
        fila_acc_pass.grid_columnconfigure(0, weight=1)
        fila_acc_pass.grid_columnconfigure(1, weight=1)

        btn_copy_pass = ctk.CTkButton(fila_acc_pass, text="📋 Copiar Contraseña", 
                                      height=36, corner_radius=6, fg_color="#1e293b", hover_color="#334155",
                                      font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                      command=self.copiar_pass)
        btn_copy_pass.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        btn_test_pass = ctk.CTkButton(fila_acc_pass, text="🔍 Probar en Validador", 
                                      height=36, corner_radius=6, fg_color=self.C_CYAN, hover_color=self.C_CYAN_HOVER,
                                      font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                      command=self.enviar_pass_a_validador)
        btn_test_pass.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.lbl_toast_pass = ctk.CTkLabel(card_pass, text="", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        self.lbl_toast_pass.pack(pady=(2, 14))

    def actualizar_label_slider(self, val):
        val_int = int(val)
        if val_int >= 15:
            rec = " • 🟢 Fuerte (NIST Factor Único)"
        elif val_int >= 12:
            rec = " • 🟡 Media"
        else:
            rec = " • ⚠️ Baja"
        self.lbl_slider_val.configure(text=f"Longitud: {val_int} car.{rec}")

    def toggle_password(self):
        if self.switch_show_pass.get() == 1:
            self.entry_pass.configure(show="")
        else:
            self.entry_pass.configure(show="*")

    def limpiar_traza(self):
        self.txt_consola.delete("0.0", "end")
        self.badge_traza_estado.configure(text="⚪ Listo para Escaneo", fg_color="#151d31", text_color="#94a3b8")
        self.lbl_stats_traza.configure(text="Registro limpiado. Esperando entrada del usuario...")

    def copiar_traza(self):
        texto = self.txt_consola.get("0.0", "end").strip()
        if texto:
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.badge_traza_estado.configure(text="📋 Traza Copiada", fg_color="#082f49", text_color="#38bdf8")

    def analizar_credenciales(self, event=None):
        correo = self.entry_correo.get()
        password = self.entry_pass.get()

        # Limpiar consola
        self.txt_consola.delete("0.0", "end")
        stats = []

        # 1. Correo
        es_valido_correo = False
        if correo:
            es_valido_correo, rep_correo = self.validador.validar_correo_afd(correo)
            self.txt_consola.insert("end", "=== ANÁLISIS DE CORREO ELECTRÓNICO (RFC 5322 & AFD) ===\n" + rep_correo + "\n\n")

            if es_valido_correo:
                self.badge_correo.configure(text="✅ CORREO VÁLIDO — Alcanzó el estado de aceptación [q6]", 
                                            fg_color="#064e3b", text_color="#34d399")
                stats.append(f"Correo: {len(correo)} car. [q6 - VÁLIDO]")
            else:
                motivo = "Formato incompleto o carácter no permitido"
                for l in rep_correo.split('\n'):
                    if "❌" in l:
                        motivo = l.replace("❌", "").strip()
                        break
                self.badge_correo.configure(text=f"❌ {motivo}", 
                                            fg_color="#450a0a", text_color="#fda4af")
                stats.append(f"Correo: {len(correo)} car. [RECHAZADO]")
        else:
            self.badge_correo.configure(text="⚪ Ingrese un correo para analizar el recorrido del autómata", 
                                        fg_color="#151d31", text_color="#94a3b8")

        # 2. Contraseña
        es_valida_pass = False
        if password:
            es_valida_pass, rep_pass = self.validador.validar_contrasena(password)
            self.txt_consola.insert("end", "=== ANÁLISIS DE CONTRASEÑA (NIST SP 800-63B) ===\n" + rep_pass + "\n")
            self.actualizar_medidor_password(len(password), es_valida_pass)
            nivel_txt = "VÁLIDA" if es_valida_pass else "NO VÁLIDA"
            stats.append(f"Contraseña: {len(password)} car. [{nivel_txt}]")
        else:
            self.prog_pass.set(0)
            self.lbl_nivel_pass.configure(text="⚪ Ingrese una contraseña para evaluar robustez", 
                                          text_color="#94a3b8")

        # Actualizar badge del inspector y métricas inferiores
        if correo or password:
            if correo and es_valido_correo and (not password or es_valida_pass):
                self.badge_traza_estado.configure(text="✅ Cumple Formalismo", fg_color="#064e3b", text_color="#34d399")
            elif (correo and not es_valido_correo) or (password and not es_valida_pass):
                self.badge_traza_estado.configure(text="❌ Falla Detectada", fg_color="#450a0a", text_color="#fda4af")
            else:
                self.badge_traza_estado.configure(text="⚡ En Análisis", fg_color="#082f49", text_color="#38bdf8")
            self.lbl_stats_traza.configure(text="  •  ".join(stats))
        else:
            self.badge_traza_estado.configure(text="⚪ Listo para Escaneo", fg_color="#151d31", text_color="#94a3b8")
            self.lbl_stats_traza.configure(text="Esperando entrada del usuario en los campos superiores...")

    def actualizar_medidor_password(self, longitud, es_valida):
        if longitud == 0:
            self.prog_pass.set(0)
            self.lbl_nivel_pass.configure(text="⚪ Ingrese una contraseña para evaluar robustez", text_color="#94a3b8")
        elif not es_valida and longitud < 8:
            self.prog_pass.set(longitud / 64)
            self.prog_pass.configure(progress_color="#ef4444")
            self.lbl_nivel_pass.configure(text=f"❌ Muy Corta ({longitud}/8 car.) — NIST exige mínimo 8 caracteres", text_color="#f87171")
        elif not es_valida:
            self.prog_pass.set(0.15)
            self.prog_pass.configure(progress_color="#ef4444")
            self.lbl_nivel_pass.configure(text="❌ Contiene caracteres prohibidos o excede 64 caracteres", text_color="#f87171")
        elif longitud < 12:
            self.prog_pass.set(longitud / 64)
            self.prog_pass.configure(progress_color="#f97316")
            self.lbl_nivel_pass.configure(text=f"🟡 Seguridad Baja ({longitud} car.) — Mínimo NIST, vulnerable a fuerza bruta", text_color="#fb923c")
        elif longitud < 15:
            self.prog_pass.set(longitud / 64)
            self.prog_pass.configure(progress_color="#eab308")
            self.lbl_nivel_pass.configure(text=f"🟢 Seguridad Media ({longitud} car.) — Buena resistencia criptográfica", text_color="#facc15")
        else:
            self.prog_pass.set(min(longitud / 30, 1.0))
            self.prog_pass.configure(progress_color="#10b981")
            self.lbl_nivel_pass.configure(text=f"🛡️ Seguridad Fuerte ({longitud} car.) — Cumple NIST Factor Único (≥ 15 car.)", text_color="#34d399")

    def generar_correo(self):
        palabras = self.entry_palabras.get()
        dominio = self.combo_dominio.get()

        variantes = self.validador.generar_variantes_correo(palabras_base=palabras, dominio=dominio, cantidad=6)
        if variantes:
            correo_gen = variantes[0]
            self.salida_correo.delete(0, "end")
            self.salida_correo.insert(0, correo_gen)
            self._actualizar_botones_variantes(variantes)

            es_valido, _ = self.validador.validar_correo_afd(correo_gen)
            if es_valido:
                self.lbl_estado_correo.configure(text="✅ Verificado con AFD: Correo válido (Alcanzó q6)", text_color="#34d399")
            else:
                self.lbl_estado_correo.configure(text="⚠️ Verificado con AFD: El dominio personalizado requiere ajuste", text_color="#f87171")

    def generar_mas_variantes(self):
        palabras = self.entry_palabras.get()
        dominio = self.combo_dominio.get()
        variantes = self.validador.generar_variantes_correo(palabras_base=palabras, dominio=dominio, cantidad=6)
        if variantes:
            self._actualizar_botones_variantes(variantes)

    def _actualizar_botones_variantes(self, variantes):
        for idx, btn in enumerate(self.botones_variantes):
            if idx < len(variantes):
                email = variantes[idx]
                btn.configure(
                    text=f" 👉 {email}",
                    state="normal",
                    text_color="#f8fafc",
                    fg_color="#13192b",
                    hover_color="#1e293b",
                    command=lambda e=email: self.seleccionar_variante(e)
                )
            else:
                btn.configure(text="", state="disabled", fg_color="#0b1120")

    def seleccionar_variante(self, email):
        self.salida_correo.delete(0, "end")
        self.salida_correo.insert(0, email)
        es_valido, _ = self.validador.validar_correo_afd(email)
        if es_valido:
            self.lbl_estado_correo.configure(text=f"✅ Seleccionado: '{email}' es válido según el AFD (q6)", text_color="#34d399")
        else:
            self.lbl_estado_correo.configure(text="⚠️ El correo seleccionado requiere ajuste en dominio", text_color="#f87171")

    def copiar_correo(self):
        correo = self.salida_correo.get()
        if correo:
            self.clipboard_clear()
            self.clipboard_append(correo)
            self.lbl_estado_correo.configure(text="📋 ¡Correo copiado al portapapeles!", text_color="#38bdf8")

    def enviar_a_validador(self):
        correo = self.salida_correo.get()
        if correo:
            self.entry_correo.delete(0, "end")
            self.entry_correo.insert(0, correo)
            self.tabview.set("⚡ Validar en Tiempo Real")
            self.analizar_credenciales()

    def generar_pass(self):
        longitud = int(self.slider_pass.get())
        pass_gen = self.validador.generar_contrasena_guiada(longitud)
        es_valida, reporte = self.validador.validar_contrasena(pass_gen)

        self.salida_pass.delete(0, "end")
        self.salida_pass.insert(0, pass_gen)

        # Diagnóstico claro, prominente y explícito de si es segura o no
        if longitud >= 15:
            self.badge_seguridad_pass.configure(
                text="✅ CONTRASEÑA SEGURA — Nivel Fuerte (Cumple Factor Único NIST ≥ 15 car.)",
                fg_color="#064e3b", text_color="#34d399"
            )
        elif longitud >= 12:
            self.badge_seguridad_pass.configure(
                text="🟡 SEGURIDAD MEDIA — Aceptable para uso general (12 - 14 caracteres)",
                fg_color="#451a03", text_color="#fde68a"
            )
        elif longitud >= 8:
            self.badge_seguridad_pass.configure(
                text="⚠️ SEGURIDAD BAJA — Mínimo permitido (8 - 11 car., vulnerable a fuerza bruta)",
                fg_color="#451a03", text_color="#fb923c"
            )
        else:
            self.badge_seguridad_pass.configure(
                text="❌ CONTRASEÑA INSEGURA — No cumple la longitud mínima recomendada",
                fg_color="#450a0a", text_color="#fda4af"
            )

        self.lbl_toast_pass.configure(text="")

    def copiar_pass(self):
        password = self.salida_pass.get()
        if password:
            self.clipboard_clear()
            self.clipboard_append(password)
            self.lbl_toast_pass.configure(text="📋 ¡Contraseña copiada al portapapeles!", text_color="#38bdf8")

    def enviar_pass_a_validador(self):
        password = self.salida_pass.get()
        if password:
            self.entry_pass.delete(0, "end")
            self.entry_pass.insert(0, password)
            self.tabview.set("⚡ Validar en Tiempo Real")
            self.analizar_credenciales()

if __name__ == "__main__":
    app = AppCredenciales()
    app.mainloop()