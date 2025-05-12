import tkinter as tk
import _tkinter
import customtkinter as ctk


hdr_1_font = ("Arial", 15 ) 
hdr_2_font = ("Courier", 13 ) 

def build_main_app(app):
    
    ctk.set_appearance_mode('system')
    ctk.set_default_color_theme('blue')
    
    app.geometry("720x480")
    
    # inputs
    text_var = ctk.StringVar()
    text_var.set("Application Directory")
    label = build_label(app, {'textvariable' : text_var, 'anchor' : "w", 'justify' : "left", 'font': hdr_2_font})
    label.pack(pady=10, padx=10, anchor="w") 
    
    app_dir_txt_input = tk.Entry(app, width=40)
    app_dir_txt_input.pack(pady=4, padx=10, anchor="w")
    
    text_var = ctk.StringVar()
    text_var.set("Acoustic Data Directory")
    label = build_label(app, {'textvariable' : text_var, 'anchor' : ctk.W,'font': hdr_2_font})
    label.pack(pady=20, padx=10, anchor="w") 
    
    acoustic_dir_txt_input = tk.Entry(app, width=40)
    acoustic_dir_txt_input.pack(pady=2, padx=10, anchor="w")
    
    text_var = ctk.StringVar()
    text_var.set("Working Directory")
    label = build_label(app, {'textvariable' : text_var, 'anchor' : ctk.W,'font': hdr_2_font})
    label.pack(pady=20, padx=10, anchor="w") 
    
    working_dir_txt_input =tk.Entry(app, width=40)
    working_dir_txt_input.pack(pady=2, padx=10, anchor="w")
    
    text_var = ctk.StringVar()
    text_var.set("Features Directory")
    label = build_label(app, {'textvariable' : text_var, 'anchor' : ctk.W,'font': hdr_2_font})
    label.pack(pady=20, padx=10, anchor="w") 
    
    features_dir_txt_input = tk.Entry(app, width=40)
    features_dir_txt_input.pack(pady=2, padx=10, anchor="w")
    
    text_var = ctk.StringVar()
    text_var.set("Output Directory")
    label = build_label(app, {'textvariable' : text_var, 'anchor' : ctk.W,'font': hdr_2_font})
    label.pack(pady=20, padx=10, anchor="w") 
    
    output_dir_txt_input = tk.Entry(app, width=40)
    output_dir_txt_input.pack(pady=2, padx=10, anchor="w")


    # Button to print input
    btn = tk.Button(app, text="Run IDent", command=main_run)
    btn.pack(pady=20, padx=10, anchor="w")
    
    
def build_label(app, options={}):
    # Create the label widget with all options
    label = tk.Label(app,options) 
    
    return label
        
def run_app(app):
    app.mainloop()
    


