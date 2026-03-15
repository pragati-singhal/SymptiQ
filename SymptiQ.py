import customtkinter as ctk
from PIL import Image
import webbrowser
import os
import sqlite3 # Imported for future database integration

# ==========================================
# SETUP & THEME CONFIGURATION
# ==========================================
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Custom colors inspired by the SymptiQ Logo (Blue to Green gradient vibe)
SYMPTIQ_BLUE = "#1F6AA5"
SYMPTIQ_GREEN = "#159c7b"
BG_COLOR = "#f4f5f7" # For light mode
DARK_BG = "#1a1a1a"  # For dark mode

class SymptiQApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SymptiQ: AI-Powered Healthcare Clarity")
        self.geometry("1000x650")
        self.minsize(800, 500)
        
        # Load Logo Image
        self.load_logo()

        # Configure main grid (1 row, 1 column for full screen frame swapping)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize Frames
        self.login_frame = LoginFrame(self, self.login_success)
        self.dashboard_frame = DashboardFrame(self, self.logout)

        # Show Login Screen Initially
        self.show_frame(self.login_frame)

    def load_logo(self):
        """Loads the logo image to be used across the app."""
        logo_path = os.path.join(os.path.dirname(__file__), "Logo.jpeg")
        try:
            # We create a CTkImage. It handles scaling automatically.
            image = Image.open(logo_path)
            self.logo_image_large = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 100))
            self.logo_image_small = ctk.CTkImage(light_image=image, dark_image=image, size=(120, 60))
        except FileNotFoundError:
            print("Warning: Logo.jpeg not found. Please ensure it is in the same directory.")
            self.logo_image_large = None
            self.logo_image_small = None

    def show_frame(self, frame):
        """Hides all frames and shows the requested one."""
        self.login_frame.grid_forget()
        self.dashboard_frame.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    def login_success(self, email):
        """Callback for successful login."""
        # TODO: Backend - Here you would normally set the active user session details
        self.dashboard_frame.set_user(email)
        self.show_frame(self.dashboard_frame)

    def logout(self):
        """Callback for logging out."""
        # TODO: Backend - Clear user session variables here
        self.show_frame(self.login_frame)


# ==========================================
# LOGIN SCREEN
# ==========================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback):
        super().__init__(master, corner_radius=0)
        self.login_callback = login_callback

        # Center configure
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Login Box container
        self.box = ctk.CTkFrame(self, width=400, height=450, corner_radius=15)
        self.box.grid(row=1, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)
        self.box.grid_rowconfigure(8, weight=1)

        # Logo
        if master.logo_image_large:
            self.logo_label = ctk.CTkLabel(self.box, text="", image=master.logo_image_large)
            self.logo_label.grid(row=0, column=0, pady=(30, 10))
        else:
            self.logo_label = ctk.CTkLabel(self.box, text="SymptiQ", font=ctk.CTkFont(size=30, weight="bold"))
            self.logo_label.grid(row=0, column=0, pady=(30, 10))

        self.welcome_label = ctk.CTkLabel(self.box, text="Welcome to SymptiQ\nUSER LOGIN", font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=1, column=0, pady=(0, 20))

        # Email Input
        self.email_entry = ctk.CTkEntry(self.box, width=250, placeholder_text="Email Id")
        self.email_entry.grid(row=2, column=0, pady=10)

        # Password Input
        self.password_entry = ctk.CTkEntry(self.box, width=250, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, pady=10)

        # Login Button
        self.login_btn = ctk.CTkButton(self.box, text="Login / Register", fg_color=SYMPTIQ_BLUE, hover_color=SYMPTIQ_GREEN, command=self.attempt_login)
        self.login_btn.grid(row=4, column=0, pady=20)

        # Forgot Password
        self.forgot_btn = ctk.CTkButton(self.box, text="Forgot password?", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.forgot_btn.grid(row=5, column=0, pady=(0, 20))

        self.error_label = ctk.CTkLabel(self.box, text="", text_color="red")
        self.error_label.grid(row=6, column=0)

    def attempt_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        # TODO: Backend - Database Authentication
        
        if email == "" or password == "":
            self.error_label.configure(text="Please enter both Email and Password.")
        else:
            self.error_label.configure(text="")
            self.email_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.login_callback(email)


# ==========================================
# DASHBOARD (MAIN APPLICATION)
# ==========================================
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, logout_callback):
        super().__init__(master, corner_radius=0)
        self.logout_callback = logout_callback

        # Grid Layout: Sidebar (col 0) and Main Content (col 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # Pushes logout to bottom

        if master.logo_image_small:
            self.side_logo = ctk.CTkLabel(self.sidebar_frame, text="", image=master.logo_image_small)
            self.side_logo.grid(row=0, column=0, padx=20, pady=(20, 20))
        else:
            self.side_logo = ctk.CTkLabel(self.sidebar_frame, text="SymptiQ", font=ctk.CTkFont(size=20, weight="bold"))
            self.side_logo.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.menu_label = ctk.CTkLabel(self.sidebar_frame, text="Menu:", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.menu_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Sidebar Navigation Buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color=SYMPTIQ_BLUE, anchor="w", command=self.show_input_view)
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_profile = ctk.CTkButton(self.sidebar_frame, text="Profile & History", fg_color="transparent", text_color=("gray10", "gray90"), anchor="w", hover_color=("gray70", "gray30"))
        self.btn_profile.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_prefs = ctk.CTkButton(self.sidebar_frame, text="Preferences", fg_color="transparent", text_color=("gray10", "gray90"), anchor="w", hover_color=("gray70", "gray30"))
        self.btn_prefs.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_help = ctk.CTkButton(self.sidebar_frame, text="Help & T&C", fg_color="transparent", text_color=("gray10", "gray90"), anchor="w", hover_color=("gray70", "gray30"))
        self.btn_help.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="Logout [→", fg_color="#d9534f", hover_color="#c9302c", anchor="w", command=self.logout_callback)
        self.btn_logout.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")

        # --- Main Content Area ---
        # We will use this frame to swap between Input, Results, and Details views
        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Inner Views (Instantiate them once and swap them using tkraise or grid)
        self.input_view = InputView(self.main_content, self.process_symptoms)
        self.results_view = ResultsView(self.main_content, self.show_disease_details)
        self.details_view = DetailsView(self.main_content, self.show_results_view)

        # Show initial view
        self.show_input_view()

    def set_user(self, email):
        user_name = email.split('@')[0].capitalize()
        self.input_view.welcome_label.configure(text=f"Hello, {user_name}!")

    def hide_all_views(self):
        self.input_view.grid_forget()
        self.results_view.grid_forget()
        self.details_view.grid_forget()

    def show_input_view(self):
        self.hide_all_views()
        self.input_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Highlight Dashboard button
        self.btn_dashboard.configure(fg_color=SYMPTIQ_BLUE)

    def show_results_view(self):
        self.hide_all_views()
        self.results_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def show_disease_details(self, disease_data):
        self.hide_all_views()
        self.details_view.populate_data(disease_data)
        self.details_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def process_symptoms(self, symptom_text):
        """Called when user clicks 'Analyze'."""
        if not symptom_text.strip():
            return

        # TODO: Backend - AI and NLP Integration
        # 1. Clean `symptom_text` using NLTK/spaCy
        # 2. Extract keywords.
        # 3. Pass keywords to scikit-learn model OR Google Gemini API.
        # 4. Fetch matching conditions from SQLite database.
        
        # --- MOCK DATA FOR DEMONSTRATION ---
        mock_results = [
            {
                "name": "Migraine",
                "match": "Matching Symptoms: Headache, Sensitivity to light, Nausea",
                "overview": "A migraine is a headache that can cause severe throbbing pain or a pulsing sensation, usually on one side of the head. It's often accompanied by nausea, vomiting, and extreme sensitivity to light and sound.",
                "causes": "Hormonal changes, certain foods/drinks, stress, sensory stimuli, changes in sleep.",
                "remedies": "1. Rest in a quiet, dark room.\n2. Apply a cold compress to your forehead.\n3. Stay hydrated.\n4. Consume a small amount of caffeine.",
                "specialist": "Neurologist"
            },
            {
                "name": "Tension Headache",
                "match": "Matching Symptoms: Dull head pain, tightness across forehead",
                "overview": "A tension headache is generally a diffuse, mild to moderate pain in your head that's often described as feeling like a tight band around your head.",
                "causes": "Stress, inadequate sleep, poor posture, eye strain.",
                "remedies": "1. Practice relaxation techniques.\n2. Apply a heating pad to your neck.\n3. Gently massage your scalp.\n4. Rest in a well-ventilated room.",
                "specialist": "General Physician"
            }
        ]
        
        # Populate the results view with the AI/DB results
        self.results_view.populate_results(mock_results, symptom_text)
        self.show_results_view()


# ==========================================
# INTERNAL VIEWS (Inside Dashboard)
# ==========================================

class InputView(ctk.CTkFrame):
    """View 1: Where the user types their symptoms."""
    def __init__(self, master, analyze_callback):
        super().__init__(master, fg_color="transparent")
        self.analyze_callback = analyze_callback

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.welcome_label = ctk.CTkLabel(self, text="Hello, User!", font=ctk.CTkFont(size=24, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w", pady=(10, 5))

        self.instruction_label = ctk.CTkLabel(self, text="Please describe how you are feeling in detail. What are your symptoms?", font=ctk.CTkFont(size=14))
        self.instruction_label.grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.symptom_textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=14))
        self.symptom_textbox.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.symptom_textbox.insert("0.0", "E.g., I have had a severe headache on the left side of my head since yesterday, and I feel nauseous when I look at bright lights...")

        self.analyze_btn = ctk.CTkButton(self, text="Analyze Symptoms with AI", font=ctk.CTkFont(weight="bold"), fg_color=SYMPTIQ_GREEN, hover_color="#117a60", height=40, command=self.on_analyze)
        self.analyze_btn.grid(row=3, column=0, pady=(0, 10))

    def on_analyze(self):
        text = self.symptom_textbox.get("0.0", "end")
        self.analyze_callback(text)


class ResultsView(ctk.CTkFrame):
    """View 2: Displays the list of probable diseases."""
    def __init__(self, master, details_callback):
        super().__init__(master, fg_color="transparent")
        self.details_callback = details_callback

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self, text="Analysis Results", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="w", pady=(10, 5))

        self.user_symptoms = ctk.CTkLabel(self, text="Based on your input...", text_color="gray", font=ctk.CTkFont(slant="italic"))
        self.user_symptoms.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Scrollable frame for results
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def populate_results(self, results, original_text):
        # Clear previous results
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Trim original text for display
        short_text = (original_text[:60] + '...') if len(original_text) > 60 else original_text
        self.user_symptoms.configure(text=f'Analyzed for: "{short_text.strip()}"')

        # Generate result cards
        for i, disease in enumerate(results):
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
            card.grid(row=i, column=0, sticky="ew", pady=10, padx=10)
            card.grid_columnconfigure(0, weight=1)

            title = ctk.CTkLabel(card, text=disease["name"], font=ctk.CTkFont(size=18, weight="bold"), text_color=SYMPTIQ_BLUE)
            title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

            match = ctk.CTkLabel(card, text=disease["match"], font=ctk.CTkFont(size=12))
            match.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))

            # Important: we use a default argument `d=disease` in the lambda to capture the current iteration's data
            view_btn = ctk.CTkButton(card, text="View Details", fg_color=SYMPTIQ_BLUE, command=lambda d=disease: self.details_callback(d))
            view_btn.grid(row=0, column=1, rowspan=2, padx=15, pady=15)


class DetailsView(ctk.CTkFrame):
    """View 3: Shows detailed information about a specific disease."""
    def __init__(self, master, back_callback):
        super().__init__(master, fg_color="transparent")
        self.back_callback = back_callback
        self.current_specialist = ""

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top Bar
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.back_btn = ctk.CTkButton(self.top_bar, text="← Back to Results", width=120, fg_color="transparent", text_color=SYMPTIQ_BLUE, border_width=1, border_color=SYMPTIQ_BLUE, hover_color=SYMPTIQ_BLUE, command=self.back_callback)
        self.back_btn.grid(row=0, column=0, sticky="w")

        # Scrollable Content Area
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(self.content, text="DISEASE NAME", font=ctk.CTkFont(size=28, weight="bold"), text_color=SYMPTIQ_BLUE)
        self.title_lbl.grid(row=0, column=0, sticky="w", pady=(10, 20))

        # Disease Overview
        self._create_section(self.content, 1, "Disease Overview", "overview_lbl")
        # Causes
        self._create_section(self.content, 3, "Causes", "causes_lbl")
        # Home Remedies
        self._create_section(self.content, 5, "Home Remedies", "remedies_lbl")

        # Specialist Section
        spec_frame = ctk.CTkFrame(self.content, corner_radius=10, fg_color=SYMPTIQ_GREEN)
        spec_frame.grid(row=7, column=0, sticky="ew", pady=(30, 10), ipady=10)
        spec_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(spec_frame, text="Specialist to Contact", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").grid(row=0, column=0, pady=(10, 5))
        self.spec_desc = ctk.CTkLabel(spec_frame, text="For accurate diagnosis, we recommend consulting a specialist.", text_color="white")
        self.spec_desc.grid(row=1, column=0, pady=(0, 10))

        self.route_btn = ctk.CTkButton(spec_frame, text="Find Specialist Near Me", fg_color="white", text_color=SYMPTIQ_GREEN, hover_color="#f0f0f0", font=ctk.CTkFont(weight="bold"), command=self.route_to_specialist)
        self.route_btn.grid(row=2, column=0, pady=(0, 15))

    def _create_section(self, parent, row, title, attr_name):
        lbl_title = ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        lbl_title.grid(row=row, column=0, sticky="w", pady=(10, 5))
        
        lbl_content = ctk.CTkLabel(parent, text="", justify="left", wraplength=700, font=ctk.CTkFont(size=14))
        lbl_content.grid(row=row+1, column=0, sticky="w", pady=(0, 15))
        
        setattr(self, attr_name, lbl_content)

    def populate_data(self, data):
        self.title_lbl.configure(text=data["name"].upper())
        self.overview_lbl.configure(text=data["overview"])
        self.causes_lbl.configure(text=data["causes"])
        self.remedies_lbl.configure(text=data["remedies"])
        
        self.current_specialist = data["specialist"]
        self.spec_desc.configure(text=f"For accurate diagnosis, we recommend consulting a {self.current_specialist} as soon as possible!")
        self.route_btn.configure(text=f"Find {self.current_specialist} Near Me")

    def route_to_specialist(self):
        """Python Web Routing Logic (Milestone Requirement)"""
        if self.current_specialist:
            query = f"{self.current_specialist} near me"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    app = SymptiQApp()
    app.mainloop()