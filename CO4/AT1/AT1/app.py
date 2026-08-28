import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator

def translate_text():
    text = input_box.get("1.0", tk.END).strip()
    language = language_combo.get()

    if text == "":
        messagebox.showwarning("Warning", "Please enter English text")
        return

    languages = {
        "Hindi": "hi",
        "Telugu": "te",
        "Tamil": "ta"
    }

    try:
        translated = GoogleTranslator(
            source="en",
            target=languages[language]
        ).translate(text)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated)

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("Multilingual Translation Application")
root.geometry("600x450")

tk.Label(
    root,
    text="Multilingual Translation Application",
    font=("Arial", 16, "bold")
).pack(pady=10)

tk.Label(root, text="Enter English Text:").pack()

input_box = tk.Text(root, height=6, width=60)
input_box.pack(pady=5)

tk.Label(root, text="Select Target Language:").pack()

language_combo = ttk.Combobox(
    root,
    values=["Hindi", "Telugu", "Tamil"],
    state="readonly"
)
language_combo.pack(pady=5)
language_combo.set("Hindi")

tk.Button(
    root,
    text="Translate",
    command=translate_text
).pack(pady=10)

tk.Label(root, text="Translated Text:").pack()

output_box = tk.Text(root, height=6, width=60)
output_box.pack(pady=5)

root.mainloop()