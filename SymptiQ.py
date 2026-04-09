import customtkinter as ctk
from PIL import Image
import webbrowser
import os
import pandas as pd
import joblib
import numpy as np

# ==========================================
# ENTERPRISE THEME CONFIGURATION
# ==========================================
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

BRAND_PRIMARY = "#0B2447"      # Deep Navy for Sidebar
BRAND_ACCENT = "#19A7CE"       # Bright Teal/Blue for CTA Buttons
BRAND_SUCCESS = "#10B981"      # Emerald Green for Routing/Success
SIDEBAR_HOVER = "#1e3a63"
BG_MAIN = ("#F4F6F8", "#121212")
CARD_BG = ("#FFFFFF", "#1E1E1E")
TEXT_MAIN = ("#111827", "#F9FAFB")
TEXT_SUB = ("#6B7280", "#9CA3AF")

class FadeLabel(ctk.CTkLabel):
    """Custom label for smooth text fade-in animations."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.final_text_color = self.cget("text_color")
        if isinstance(self.final_text_color, (list, tuple)):
            mode = ctk.get_appearance_mode()
            self.final_text_color = self.final_text_color[0] if mode == "Light" else self.final_text_color[1]

    def fade_in(self, text, step=0):
        if step == 0:
            self.configure(text=text, text_color=self._get_fade_color())
            self.after(15, self.fade_in, text, 1)
        elif step <= 10:
            self.configure(text_color=self._get_fade_color())
            self.after(15, self.fade_in, text, step + 1)
        else:
            self.configure(text_color=self.final_text_color)

    def _get_fade_color(self):
        return self.final_text_color


class SymptiQApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SymptiQ: AI Diagnostic Assistant")
        self.geometry("1280x850")
        self.minsize(1100, 750)
        self.configure(fg_color=BG_MAIN)

        self.load_assets()
        
        self.model = None
        self.vectorizer = None
        self.disease_data = None
        self.load_ai_engine()

        self.pages = {}
        self.responsive_labels = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.build_login_screen()
        self.build_main_application()

        self.bind("<Configure>", self.on_window_resize)

        self.app_container.grid_remove()
        self.login_container.grid(row=0, column=0, sticky="nsew")

    def load_assets(self):
        self.logo_large = None
        self.logo_small = None
        
        target_logo = "Only Logo.jpeg"
        if not os.path.exists(target_logo):
            target_logo = "Logo.jpeg"
            
        if os.path.exists(target_logo):
            try:
                img_data = Image.open(target_logo)
                self.logo_large = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(130, 130))
                self.logo_small = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(45, 45))
            except Exception as e:
                print(f"Asset warning: {e}")

    def load_ai_engine(self):
        try:
            self.model = joblib.load('model.pkl')
            self.vectorizer = joblib.load('vectorizer.pkl')
            self.disease_data = pd.read_csv('Dataset_SymptiQ.csv')
            self.disease_data.columns = self.disease_data.columns.str.strip()
        except Exception as e:
            print(f"System Error (AI Engine): {e}")

    def on_window_resize(self, event):
        if event.widget == self:
            if hasattr(self, '_resize_timer'):
                self.after_cancel(self._resize_timer)
            self._resize_timer = self.after(50, self.update_all_wraplengths)

    def update_all_wraplengths(self):
        try:
            scale = ctk.ScalingTracker.get_widget_scaling(self)
        except Exception:
            scale = 1.0
            
        logical_width = self.winfo_width() / scale
        
        alive_labels = []
        for lbl, offset in self.responsive_labels:
            if lbl.winfo_exists():
                safe_wrap = max(200, logical_width - offset)
                
                lbl.configure(wraplength=safe_wrap, justify="left", anchor="w")
                alive_labels.append((lbl, offset))
                
        self.responsive_labels = alive_labels

    def register_responsive_label(self, label_widget, offset=480):
        self.responsive_labels.append((label_widget, offset))
        
        if hasattr(self, '_init_wrap_timer'):
            self.after_cancel(self._init_wrap_timer)
        self._init_wrap_timer = self.after(100, self.update_all_wraplengths)

    # ==========================================
    # SCREEN 1: THE LOGIN PORTAL
    # ==========================================
    def build_login_screen(self):
        self.login_container = ctk.CTkFrame(self, fg_color="transparent")
        self.login_container.grid_rowconfigure(0, weight=1)
        self.login_container.grid_rowconfigure(2, weight=1)
        self.login_container.grid_columnconfigure(0, weight=1)
        self.login_container.grid_columnconfigure(2, weight=1)

        card = ctk.CTkFrame(self.login_container, corner_radius=20, fg_color=CARD_BG, width=450, height=550)
        card.grid(row=1, column=1, padx=20, pady=20)
        card.grid_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        if self.logo_large:
            logo_lbl = ctk.CTkLabel(content, image=self.logo_large, text="")
            logo_lbl.pack(pady=(0, 20))

        title = ctk.CTkLabel(content, text="Sign in to SymptiQ", font=ctk.CTkFont(size=26, weight="bold"), text_color=TEXT_MAIN)
        title.pack(pady=(0, 5))
        
        sub = ctk.CTkLabel(content, text="Secure AI Healthcare Platform", font=ctk.CTkFont(size=14), text_color=TEXT_SUB)
        sub.pack(pady=(0, 35))

        self.user_entry = ctk.CTkEntry(content, placeholder_text="Email or Username", width=300, height=45, corner_radius=8, border_width=1)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(content, placeholder_text="Password", show="*", width=300, height=45, corner_radius=8, border_width=1)
        self.pass_entry.pack(pady=10)

        login_btn = ctk.CTkButton(content, text="Access Platform", font=ctk.CTkFont(size=15, weight="bold"),
                                  width=300, height=50, corner_radius=8, 
                                  fg_color=BRAND_ACCENT, hover_color=BRAND_PRIMARY,
                                  command=self.login)
        login_btn.pack(pady=(30, 0))

    def login(self):
        self.login_container.grid_remove()
        self.app_container.grid(row=0, column=0, sticky="nsew")
        self.navigate_to("dashboard")
        self.after(100, self.update_all_wraplengths)

    # ==========================================
    # SCREEN 2: MAIN DASHBOARD & ROUTING
    # ==========================================
    def build_main_application(self):
        self.app_container = ctk.CTkFrame(self, fg_color="transparent")
        self.app_container.grid_rowconfigure(0, weight=1)
        self.app_container.grid_columnconfigure(1, weight=1)

        # 1. SIDEBAR
        sidebar = ctk.CTkFrame(self.app_container, width=260, corner_radius=0, fg_color=BRAND_PRIMARY)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1) 

        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, pady=(40, 40), padx=20, sticky="w")
        
        if self.logo_small:
            s_logo = ctk.CTkLabel(brand_frame, image=self.logo_small, text="")
            s_logo.pack(side="left", padx=(0, 10))
        
        brand_lbl = ctk.CTkLabel(brand_frame, text="SymptiQ", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        brand_lbl.pack(side="left")

        self.nav_buttons = {}
        self.create_nav_button(sidebar, "Dashboard", 1, "dashboard")
        self.create_nav_button(sidebar, "Medical Records", 2, "records")
        self.create_nav_button(sidebar, "Settings", 3, "settings")
        
        ctk.CTkFrame(sidebar, height=1, fg_color="#1f3a63").grid(row=4, column=0, sticky="ew", padx=20, pady=20) 
        
        self.create_nav_button(sidebar, "Help & Support", 5, "help", is_sub=True)
        self.create_nav_button(sidebar, "Terms of Service", 6, "tos", is_sub=True)

        logout_btn = ctk.CTkButton(sidebar, text="Sign Out", font=ctk.CTkFont(size=14, weight="bold"),
                                   fg_color="transparent", text_color="#9CA3AF", hover_color="#dc2626",
                                   anchor="w", width=220, height=45, command=self.logout)
        logout_btn.grid(row=8, column=0, pady=(0, 30), padx=20)

        # 2. MAIN CONTENT AREA
        self.content_area = ctk.CTkFrame(self.app_container, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Build All Pages
        self.build_dashboard_page()
        self.build_placeholder_page()
        self.build_medical_records_page()
        self.build_settings_page()
        self.build_help_page()
        self.build_tos_page()
        
        self.pages['results'] = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.pages['details'] = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")

    def create_nav_button(self, parent, text, row, target_page, is_sub=False):
        t_color = "#D1D5DB" if not is_sub else "#9CA3AF"
        font_weight = "bold" if not is_sub else "normal"
        
        btn = ctk.CTkButton(parent, text=f"  {text}", anchor="w", font=ctk.CTkFont(size=15, weight=font_weight),
                            fg_color="transparent", text_color=t_color, hover_color=SIDEBAR_HOVER,
                            width=220, height=45, corner_radius=8,
                            command=lambda: self.navigate_to(target_page))
        btn.grid(row=row, column=0, pady=5, padx=20)
        self.nav_buttons[target_page] = btn

    def navigate_to(self, page_name):
        for frame in self.pages.values():
            frame.grid_remove()
            
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color="transparent", text_color="#D1D5DB")
            
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].configure(fg_color=BRAND_ACCENT, text_color="white")
            
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")

        self.update_all_wraplengths()
        self.after(50, self.update_all_wraplengths)

    def logout(self):
        self.app_container.grid_remove()
        self.login_container.grid(row=0, column=0, sticky="nsew")
        self.symptom_input.delete("1.0", "end")

    # ==========================================
    # PAGE REPOSITORY 
    # ==========================================

    def build_dashboard_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages['dashboard'] = page
        
        greet = ctk.CTkLabel(page, text="Welcome, User", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        greet.pack(anchor="w", pady=(0, 5))
        
        sub_greet = ctk.CTkLabel(page, text="Here is your health overview for today.", font=ctk.CTkFont(size=16), text_color=TEXT_SUB, wraplength=100)
        sub_greet.pack(anchor="w", pady=(0, 30))
        self.register_responsive_label(sub_greet, offset=380)

        input_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        input_card.pack(fill="x", pady=(0, 30))
        
        inner = ctk.CTkFrame(input_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=30)
        
        lbl_instruct = ctk.CTkLabel(inner, text="What brings you here today?", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_MAIN)
        lbl_instruct.pack(anchor="w", pady=(0, 5))
        
        lbl_sub = ctk.CTkLabel(inner, text="Detail your symptoms below for a comprehensive AI diagnostic evaluation.", text_color=TEXT_SUB, font=ctk.CTkFont(size=15), wraplength=100)
        lbl_sub.pack(anchor="w", pady=(0, 15))
        self.register_responsive_label(lbl_sub, offset=450)

        self.symptom_input = ctk.CTkTextbox(inner, height=120, font=ctk.CTkFont(size=16), corner_radius=12, 
                                            fg_color=BG_MAIN, border_width=2, border_color="#E5E7EB", wrap="word")
        self.symptom_input.pack(fill="x", pady=(0, 20))

        analyze_btn = ctk.CTkButton(inner, text="Generate Health Report", font=ctk.CTkFont(size=18, weight="bold"),
                                    fg_color=BRAND_ACCENT, hover_color=BRAND_PRIMARY, height=55, corner_radius=12,
                                    command=self.run_diagnostic_engine)
        analyze_btn.pack(fill="x")

        actions_frame = ctk.CTkFrame(page, fg_color="transparent")
        actions_frame.pack(fill="x")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_action_card(actions_frame, 0, "Recent Reports", "View past analyses", "placeholder")
        self._create_action_card(actions_frame, 1, "Connected Devices", "Apple Watch synced", "placeholder")
        self._create_action_card(actions_frame, 2, "Find a Doctor", "Search network", "placeholder")

    def _create_action_card(self, parent, col, title, subtitle, target_page):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=15, height=110, cursor="hand2", border_width=1, border_color="gray80")
        card.grid(row=0, column=col, sticky="ew", padx=10)
        card.grid_propagate(False) 
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        t_lbl = ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_MAIN)
        t_lbl.pack(anchor="w", pady=(5, 0))
        s_lbl = ctk.CTkLabel(inner, text=subtitle, font=ctk.CTkFont(size=14), text_color=TEXT_SUB)
        s_lbl.pack(anchor="w")

        def on_click(event):
            self.navigate_to(target_page)
            
        card.bind("<Button-1>", on_click)
        inner.bind("<Button-1>", on_click)
        t_lbl.bind("<Button-1>", on_click)
        s_lbl.bind("<Button-1>", on_click)

    def build_medical_records_page(self):
        page = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.pages['records'] = page
        
        title = ctk.CTkLabel(page, text="Comprehensive Medical Profile", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 5))
        
        sub = ctk.CTkLabel(page, text="Manage your foundational health parameters for highly accurate AI predictions.", font=ctk.CTkFont(size=16), text_color=TEXT_SUB, wraplength=100)
        sub.pack(anchor="w", pady=(0, 25))
        self.register_responsive_label(sub, offset=380)

        form_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        form_card.pack(fill="x", pady=(0, 20))
        
        inner = ctk.CTkFrame(form_card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(inner, text="Personal Details", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        p_frame = ctk.CTkFrame(inner, fg_color="transparent")
        p_frame.pack(fill="x", pady=(0, 20))
        p_frame.grid_columnconfigure(1, weight=1)

        personal_fields = [("Full Legal Name", "Enter your full name"), ("Date of Birth", "DD/MM/YYYY"), 
                           ("Biological Sex", "Male / Female / Other"), ("Blood Group", "A+, O-, etc.")]
        for i, (label, placeholder) in enumerate(personal_fields):
            ctk.CTkLabel(p_frame, text=label, font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_MAIN).grid(row=i, column=0, sticky="w", pady=10, padx=(0, 30))
            ctk.CTkEntry(p_frame, placeholder_text=placeholder, fg_color=BG_MAIN, height=45).grid(row=i, column=1, sticky="ew", pady=10)

        ctk.CTkFrame(inner, height=1, fg_color="gray80").pack(fill="x", pady=20)

        ctk.CTkLabel(inner, text="Vitals & Metrics", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        v_frame = ctk.CTkFrame(inner, fg_color="transparent")
        v_frame.pack(fill="x", pady=(0, 20))
        v_frame.grid_columnconfigure(1, weight=1)

        vitals_fields = [("Height (cm)", "e.g., 175"), ("Weight (kg)", "e.g., 70")]
        for i, (label, placeholder) in enumerate(vitals_fields):
            ctk.CTkLabel(v_frame, text=label, font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_MAIN).grid(row=i, column=0, sticky="w", pady=10, padx=(0, 30))
            ctk.CTkEntry(v_frame, placeholder_text=placeholder, fg_color=BG_MAIN, height=45).grid(row=i, column=1, sticky="ew", pady=10)

        ctk.CTkFrame(inner, height=1, fg_color="gray80").pack(fill="x", pady=20)

        ctk.CTkLabel(inner, text="Lifestyle & Habits", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        l_frame = ctk.CTkFrame(inner, fg_color="transparent")
        l_frame.pack(fill="x", pady=(0, 20))
        l_frame.grid_columnconfigure(1, weight=1)

        lifestyle_fields = [("Smoking Status", "Never / Former / Current"), ("Alcohol Consumption", "None / Occasional / Frequent"),
                            ("Physical Activity", "Sedentary / Moderate / Active")]
        for i, (label, placeholder) in enumerate(lifestyle_fields):
            ctk.CTkLabel(l_frame, text=label, font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_MAIN).grid(row=i, column=0, sticky="w", pady=10, padx=(0, 30))
            ctk.CTkEntry(l_frame, placeholder_text=placeholder, fg_color=BG_MAIN, height=45).grid(row=i, column=1, sticky="ew", pady=10)

        ctk.CTkFrame(inner, height=1, fg_color="gray80").pack(fill="x", pady=20)

        ctk.CTkLabel(inner, text="Clinical History", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        c_frame = ctk.CTkFrame(inner, fg_color="transparent")
        c_frame.pack(fill="x", pady=(0, 20))
        c_frame.grid_columnconfigure(1, weight=1)

        clinical_fields = [
            ("Known Allergies", "List any food or medication allergies..."), 
            ("Current Medications", "List active medications and dosages..."), 
            ("Pre-existing Conditions", "E.g., Asthma, Diabetes, Hypertension..."), 
            ("Past Surgeries", "Year and type of procedure...")]
        
        for i, (label, placeholder) in enumerate(clinical_fields):
            ctk.CTkLabel(c_frame, text=label, font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_MAIN).grid(row=i, column=0, sticky="nw", pady=15, padx=(0, 30))
            box = ctk.CTkTextbox(c_frame, height=75, fg_color=BG_MAIN, border_width=1, border_color="gray80", wrap="word")
            box.insert("1.0", placeholder)
            box.grid(row=i, column=1, sticky="ew", pady=10)

        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        ctk.CTkButton(btn_frame, text="Save & Update Profile Securely", fg_color=BRAND_SUCCESS, hover_color="#059669",
                      height=55, font=ctk.CTkFont(size=16, weight="bold")).pack(side="right")

    def build_settings_page(self):
        page = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.pages['settings'] = page
        
        title = ctk.CTkLabel(page, text="Platform Settings", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 25))

        # 1. Account Section
        acc_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        acc_card.pack(fill="x", pady=(0, 25))
        inner_acc = ctk.CTkFrame(acc_card, fg_color="transparent")
        inner_acc.pack(fill="both", expand=True, padx=30, pady=25)
        
        ctk.CTkLabel(inner_acc, text="Account Preferences", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        
        r1 = ctk.CTkFrame(inner_acc, fg_color="transparent")
        r1.pack(fill="x", pady=10)
        ctk.CTkLabel(r1, text="Email Address", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkEntry(r1, placeholder_text="user@example.com", fg_color=BG_MAIN, width=300, height=40).pack(side="right")

        r2 = ctk.CTkFrame(inner_acc, fg_color="transparent")
        r2.pack(fill="x", pady=10)
        ctk.CTkLabel(r2, text="Update Password", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkEntry(r2, placeholder_text="New password...", show="*", fg_color=BG_MAIN, width=300, height=40).pack(side="right")

        # 2. Appearance Section
        app_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        app_card.pack(fill="x", pady=(0, 25))
        inner_app = ctk.CTkFrame(app_card, fg_color="transparent")
        inner_app.pack(fill="both", expand=True, padx=30, pady=25)
        
        ctk.CTkLabel(inner_app, text="Appearance & Display", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        
        row1 = ctk.CTkFrame(inner_app, fg_color="transparent")
        row1.pack(fill="x", pady=10)
        ctk.CTkLabel(row1, text="Theme Preference", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkOptionMenu(row1, values=["System", "Light", "Dark"], fg_color=BG_MAIN, text_color=TEXT_MAIN, height=40,
                          command=lambda v: ctk.set_appearance_mode(v)).pack(side="right")
        
        row2 = ctk.CTkFrame(inner_app, fg_color="transparent")
        row2.pack(fill="x", pady=10)
        ctk.CTkLabel(row2, text="Interface Language", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkOptionMenu(row2, values=["English (US)", "English (UK)", "Spanish", "French"], fg_color=BG_MAIN, text_color=TEXT_MAIN, height=40).pack(side="right")

        # 3. Notification Section
        notif_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        notif_card.pack(fill="x", pady=(0, 25))
        inner_notif = ctk.CTkFrame(notif_card, fg_color="transparent")
        inner_notif.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(inner_notif, text="Notifications", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        ctk.CTkSwitch(inner_notif, text="Enable Desktop Push Notifications", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, progress_color=BRAND_ACCENT).pack(anchor="w", pady=10)
        ctk.CTkSwitch(inner_notif, text="Receive Email Health Summaries", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, progress_color=BRAND_ACCENT).pack(anchor="w", pady=10)

        # 4. Privacy Section
        priv_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        priv_card.pack(fill="x", pady=(0, 25))
        inner_priv = ctk.CTkFrame(priv_card, fg_color="transparent")
        inner_priv.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(inner_priv, text="Privacy & Security", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        ctk.CTkSwitch(inner_priv, text="Enable Secure Biometric Login (If Available)", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, progress_color=BRAND_ACCENT).pack(anchor="w", pady=10)
        ctk.CTkSwitch(inner_priv, text="Enhanced Data Anonymization for ML processing", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, progress_color=BRAND_ACCENT).pack(anchor="w", pady=10)
        ctk.CTkSwitch(inner_priv, text="Allow crash reports to improve SymptiQ", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, progress_color=BRAND_ACCENT).pack(anchor="w", pady=10)

        # 5. Data Management
        data_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        data_card.pack(fill="x", pady=(0, 25))
        inner_data = ctk.CTkFrame(data_card, fg_color="transparent")
        inner_data.pack(fill="both", expand=True, padx=30, pady=25)

        ctk.CTkLabel(inner_data, text="Data Management", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_ACCENT).pack(anchor="w", pady=(0, 15))
        
        btn_row = ctk.CTkFrame(inner_data, fg_color="transparent")
        btn_row.pack(fill="x", pady=10)
        ctk.CTkButton(btn_row, text="Export Medical History", font=ctk.CTkFont(weight="bold", size=15), height=45, fg_color=BRAND_ACCENT).pack(side="left", padx=(0, 15))
        ctk.CTkButton(btn_row, text="Clear Local Cache", font=ctk.CTkFont(weight="bold", size=15), height=45, fg_color="transparent", border_width=1, text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkButton(btn_row, text="Delete Account Data", font=ctk.CTkFont(weight="bold", size=15), height=45, fg_color="#dc2626", hover_color="#991b1b").pack(side="right")

    def build_help_page(self):
        page = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.pages['help'] = page
        
        title = ctk.CTkLabel(page, text="Help & Support", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 20))

        faq_card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        faq_card.pack(fill="x", pady=(0, 25))
        
        inner_faq = ctk.CTkFrame(faq_card, fg_color="transparent")
        inner_faq.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(inner_faq, text="Frequently Asked Questions", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 20))
        
        faqs = [
            ("How accurate is the AI diagnostic tool?", "Our AI is trained on rigorous medical datasets and utilizes natural language processing to identify patterns. However, it is a preliminary tool and not a substitute for a professional doctor."),
            ("Is my personal health data secure?", "Absolutely. SymptiQ operates primarily locally. Any data routed for prediction is fully anonymized before leaving your device to ensure maximum privacy."),
            ("Can I save or export my diagnostic results?", "Yes. Your recent reports are saved locally to your device and are not accessible by third parties. You can view them in the 'Recent Reports' section or export them via the Settings tab."),
            ("What should I do in a severe medical emergency?", "SymptiQ is NOT an emergency response tool. If you are experiencing a life-threatening emergency, please immediately call your local emergency services (e.g., 911, 112) or go to the nearest hospital."),
            ("How do I update my medical records?", "Navigate to the 'Medical Records' tab in the sidebar. Updating your baseline health profile helps the AI contextualize your symptoms better and provide more accurate insights."),
            ("Does the application require an internet connection?", "The core symptom analysis runs entirely offline. However, advanced features like routing to a local medical specialist via Google require an active internet connection.")
        ]
        
        for q, a in faqs:
            q_lbl = ctk.CTkLabel(inner_faq, text=f"Q: {q}", font=ctk.CTkFont(size=18, weight="bold"), text_color=BRAND_ACCENT)
            q_lbl.pack(anchor="w", pady=(20, 5))
            self.register_responsive_label(q_lbl, offset=440)
            
            a_lbl = ctk.CTkLabel(inner_faq, text=f"A: {a}", text_color=TEXT_SUB, justify="left", font=ctk.CTkFont(size=16), wraplength=100)
            a_lbl.pack(anchor="w") 
            self.register_responsive_label(a_lbl, offset=440) 

        # Contact Creators
        contact_card = ctk.CTkFrame(page, fg_color=BRAND_PRIMARY, corner_radius=15)
        contact_card.pack(fill="x", pady=(0, 20))
        
        inner_contact = ctk.CTkFrame(contact_card, fg_color="transparent")
        inner_contact.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(inner_contact, text="Contact the Engineering Team", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(anchor="w", pady=(0, 15))
        ctk.CTkLabel(inner_contact, text="Pragati Singhal | s24cseu1650@bennett.edu.in", font=ctk.CTkFont(size=16), text_color="#E5E7EB").pack(anchor="w", pady=4)
        ctk.CTkLabel(inner_contact, text="Aastha Sucheta | s24cseu0192@bennett.edu.in", font=ctk.CTkFont(size=16), text_color="#E5E7EB").pack(anchor="w", pady=4)

    def build_tos_page(self):
        page = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.pages['tos'] = page
        
        title = ctk.CTkLabel(page, text="Terms & Conditions", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(page, fg_color=CARD_BG, corner_radius=15, border_width=1, border_color="gray80")
        card.pack(fill="x", pady=(0, 20))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=40)
        
        intro = ctk.CTkLabel(inner, text="Terms and Conditions and Privacy Agreement for SymptiQ", font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_MAIN, wraplength=100)
        intro.pack(anchor="w", pady=(0, 20))
        self.register_responsive_label(intro, offset=460)

        tos_sections = [
            ("1. Acceptance of Terms", "By using the SymptiQ desktop application, you are accepting to be bound by the terms and conditions stated herein. Hence, if you do not accept the terms and conditions stated herein, you should immediately stop the utilization of the application."),
            ("2. Strict Medical Disclaimer", "The SymptiQ application is a basic information system designed and developed by a student technology project. IT IS NOT A SUBSTITUTE FOR PROFESSIONAL MEDICAL ADVICE, DIAGNOSIS, OR TREATMENT. ALWAYS CONSULT YOUR PHYSICIAN OR OTHER QUALIFIED HEALTH CARE PROVIDERS WITH ANY QUESTIONS YOU MAY HAVE REGARDING A MEDICAL CONDITION. NEVER DISREGARD PROFESSIONAL MEDICAL ADVICE OR DELAY SEEKING IT BECAUSE OF ANYTHING YOU READ ON THIS APPLICATION. IF YOU THINK YOU MAY HAVE A MEDICAL EMERGENCY, CALL YOUR DOCTOR OR EMERGENCY SERVICES AT ONCE. THE HOME REMEDIES OFFERED ARE FOR GENERAL RELIEF PURPOSES ONLY AND NOT GUARANTEED TO CURE ANY ILLNESS."),
            ("3. Privacy and Data Handling", "We respect your privacy. Being a local desktop app, we don’t ask you to create any cloud-based user account. We don’t store, transmit, or make any money off any personally identifiable health-related data or symptomology that you share with us. However, if any AI engine is used through any API, then the text that you type in as symptoms will be anonymized before it is sent off to the API to ensure that no personally identifiable information leaks out."),
            ("4. Third-Party Services and Routing", "The app will also have the capability to automatically determine the type of medical specialist that you might need and route you off to a local Google Search. However, if you do that, you agree that you are leaving us and using the services of a third-party search engine. We don’t have any control over their privacy policies or the quality of medical specialists that you might find using these external links."),
            ("5. Limitation of Liability", "To the maximum extent permitted by law, the creators of SymptiQ shall not be liable for any direct, indirect, incidental, or consequential damages arising from the use or inability to use the application. This includes, but is not limited to, damages arising from medical decisions made based on the information provided by the application."),
            ("6. AI Bias and Accuracy", "Though we have made a concerted effort to provide accurate predictions about the disease through the Natural Language Processing model, there are chances that the AI model might not always produce accurate results. The database used by the application is a manually created database of symptoms, and we do not guarantee the accuracy of the data provided.")
        ]

        for heading, para in tos_sections:
            h_lbl = ctk.CTkLabel(inner, text=heading, font=ctk.CTkFont(size=18, weight="bold"), text_color=BRAND_ACCENT)
            h_lbl.pack(anchor="w", pady=(20, 5))
            self.register_responsive_label(h_lbl, offset=460)

            p_lbl = ctk.CTkLabel(inner, text=para, justify="left", font=ctk.CTkFont(size=16), text_color=TEXT_SUB, wraplength=100)
            p_lbl.pack(anchor="w") 
            self.register_responsive_label(p_lbl, offset=460) 

    def build_placeholder_page(self):
        page = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.pages['placeholder'] = page
        
        lbl = ctk.CTkLabel(page, text="Feature in Development", font=ctk.CTkFont(size=30, weight="bold"), text_color=TEXT_SUB)
        lbl.place(relx=0.5, rely=0.5, anchor="center")

    # ==========================================
    # ML LOGIC & DYNAMIC PAGE GENERATION
    # ==========================================
    def run_diagnostic_engine(self):
        user_input = self.symptom_input.get("1.0", "end-1c").strip()
        if not user_input:
            return

        if self.model is None or self.vectorizer is None or self.disease_data is None:
            print("System Error: ML Models missing.")
            return

        input_vector = self.vectorizer.transform([user_input])
        probabilities = self.model.predict_proba(input_vector)[0]
        
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_diseases = self.model.classes_[top_3_indices]

        self.build_results_page(top_3_diseases)
        self.navigate_to("results")

    # ==========================================
    # PAGE: RESULTS (Top 3 Predictions)
    # ==========================================
    def build_results_page(self, diseases):
        page = self.pages['results']
        for widget in page.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        back_btn = ctk.CTkButton(header_frame, text="← Return to Dashboard", width=150, fg_color="transparent", 
                                 text_color=TEXT_SUB, hover_color=CARD_BG, font=ctk.CTkFont(size=14, weight="bold"),
                                 command=lambda: self.navigate_to("dashboard"))
        back_btn.pack(side="left")

        title = ctk.CTkLabel(page, text="Diagnostic Analysis Complete", font=ctk.CTkFont(size=32, weight="bold"), text_color=TEXT_MAIN)
        title.pack(anchor="w", pady=(0, 5))
        
        sub = ctk.CTkLabel(page, text="Based on clinical parameters, please select the condition that best matches your symptoms:", font=ctk.CTkFont(size=16), text_color=TEXT_SUB, wraplength=100)
        sub.pack(anchor="w", pady=(0, 25))
        self.register_responsive_label(sub, offset=380)

        for i, disease in enumerate(diseases):
            self.after(150 * (i + 1), self._create_prediction_button, page, disease)

    def _create_prediction_button(self, parent, disease):
        btn = ctk.CTkButton(
            parent, 
            text=f"  {disease}", 
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=CARD_BG,
            text_color=TEXT_MAIN,
            hover_color=BRAND_ACCENT,
            height=70,
            corner_radius=12,
            anchor="w",
            border_width=1,
            border_color="gray80",
            command=lambda d=disease: self.build_details_page(d) 
        )
        btn.pack(fill="x", pady=8, padx=5)

    # ==========================================
    # PAGE: DEEP DIVE DETAILS
    # ==========================================
    def build_details_page(self, selected_disease):
        page = self.pages['details']
        for widget in page.winfo_children():
            widget.destroy()

        matching_row = self.disease_data[self.disease_data['Disease Name'] == selected_disease]
        if matching_row.empty:
            return
        row_data = matching_row.iloc[0]

        header_frame = ctk.CTkFrame(page, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        back_btn = ctk.CTkButton(header_frame, text="← Back to Predictions", width=150, fg_color="transparent", 
                                 text_color=TEXT_SUB, hover_color=CARD_BG, font=ctk.CTkFont(size=14, weight="bold"),
                                 command=lambda: self.navigate_to("results"))
        back_btn.pack(side="left")

        title_lbl = FadeLabel(page, text="", font=ctk.CTkFont(size=34, weight="bold"), text_color=BRAND_PRIMARY)
        title_lbl.pack(anchor="w", pady=(0, 10))
        self.register_responsive_label(title_lbl, offset=380)
        title_lbl.fade_in(str(row_data['Disease Name']).upper())

        badge_frame = ctk.CTkFrame(page, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 30))
        self._create_badge(badge_frame, f"Classification: {row_data['Type']}", "#DBEAFE", "#1E3A8A")   
        self._create_badge(badge_frame, f"Category: {row_data['Category']}", "#FEF3C7", "#92400E")   

        self._create_info_card(page, "Clinical Overview", str(row_data['Overview']))
        self._create_info_card(page, "Primary Causes & Triggers", str(row_data['Causes']))
        self._create_info_card(page, "Medical Treatment & Home Care", str(row_data['Treatment/ Home Remedies']))

        self._create_routing_card(page, str(row_data['Specialist']))
        self.navigate_to("details")

    def _create_badge(self, parent, text, bg_color, text_color):
        badge = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=15)
        badge.pack(side="left", padx=(0, 12))
        lbl = ctk.CTkLabel(badge, text=text, text_color=text_color, font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(padx=15, pady=6)

    def _create_info_card(self, parent, title, content):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color="gray80")
        card.pack(fill="x", pady=10)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=25)
        
        lbl_title = FadeLabel(inner, text="", font=ctk.CTkFont(size=19, weight="bold"), text_color=BRAND_ACCENT)
        lbl_title.pack(anchor="w", pady=(0, 5))
        self.register_responsive_label(lbl_title, offset=430)
        lbl_title.fade_in(title)
        
        lbl_content = FadeLabel(inner, text="", justify="left", font=ctk.CTkFont(size=16), text_color=TEXT_MAIN, wraplength=100)
        lbl_content.pack(anchor="w") 
        self.register_responsive_label(lbl_content, offset=430)
        lbl_content.fade_in(content)

    def _create_routing_card(self, parent, specialist):
        card = ctk.CTkFrame(parent, fg_color=BRAND_SUCCESS, corner_radius=12)
        card.pack(fill="x", pady=25)
        
        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(fill="x", padx=30, pady=25)
        
        text_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        text_frame.pack(side="left")
        
        title = ctk.CTkLabel(text_frame, text="Recommended Specialist Action", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        title.pack(anchor="w")
        
        desc = ctk.CTkLabel(text_frame, text=f"Consult a {specialist} for professional diagnosis and clinical care.", font=ctk.CTkFont(size=16), text_color="#D1FAE5", wraplength=100)
        desc.pack(anchor="w", pady=(2,0))
        self.register_responsive_label(desc, offset=600)
        
        route_btn = ctk.CTkButton(inner_frame, text="Locate Specialist", font=ctk.CTkFont(size=16, weight="bold"),
                                  fg_color="white", text_color=BRAND_SUCCESS, hover_color="#F3F4F6",
                                  height=50, corner_radius=8,
                                  command=lambda s=specialist: self.execute_web_routing(s))
        route_btn.pack(side="right")

    def execute_web_routing(self, specialist):
        search_term = f"{specialist} near me".replace(" ", "+")
        url = f"https://www.google.com/search?q={search_term}"
        webbrowser.open(url)

if __name__ == "__main__":
    app = SymptiQApp()
    app.mainloop()