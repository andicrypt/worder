import tkinter as tk
import random
import argparse
import re
import pandas as pd
import openai
from dotenv import load_dotenv
import os
import epitran


load_dotenv()


# Flashcard App
class FlashcardApp:
    def __init__(self, root, flashcards):
        self.root = root
        self.flashcards = flashcards
        self.original_flashcards = list(flashcards)  # Store the original order
        self.index = 0
        self.showing_back = False
        self.is_shuffled = False  # Track shuffle state

        # CHATGPT
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Initialize the UI
        self.setup_ui()

        # Bind all necessary keys
        self.bind_keys()

        # Display the first card
        self.show_front()

    def setup_ui(self):
        self.root.title("Flashcard App")
        self.root.geometry("600x400")

        # Flashcard display
        self.card_frame = tk.Frame(root, bg="white", bd=2, relief="ridge")
        self.card_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.word_label = tk.Label(self.card_frame, text="", font=("Helvetica", 32, "bold"), fg="blue", bg="white")
        self.word_label.pack(pady=(5,0))

        self.pos_label = tk.Label(self.card_frame, text="", font=("Helvetica", 18), bg="white")
        self.pos_label.pack(pady=(0, 2))  # Slightly reduce the padding for part of speech

        self.example_label = tk.Label(self.card_frame, text="", font=("Helvetica", 14), wraplength=500, bg="white")
        self.example_label.pack(pady=20)

        # Card number display (bottom-right corner)
        self.card_number_label = tk.Label(root, text="", font=("Helvetica", 10, "italic"))
        self.card_number_label.place(relx=0.95, rely=0.95, anchor="se")
        # self.card_number_label.pack()

        # Shuffle Button
        self.shuffle_button = tk.Button(root, text="Shuffle", command=self.toggle_shuffle, font=("Helvetica", 14))
        self.shuffle_button.pack(pady=10)

        self.update_card_number()  # Initial display of card number

        # Example text display using a Text widget for highlighting
        # self.example_text = tk.Text(self.card_frame, font=("Helvetica", 14), wrap="word", height=4, width=60, bg="white", bd=0)
        self.example_text = tk.Text(
            self.card_frame, 
            font=("Helvetica", 14), 
            wrap="word", 
            height=4, 
            width=60, 
            bg="white", 
            bd=0,              # Remove border
            highlightthickness=0  # Remove the highlight border
        )
        self.example_text.config(state="disabled")  # Disable editing
        self.example_text.tag_configure("highlight", font=("Helvetica", 14, "bold"), foreground="blue")
        self.example_text.pack(expand=True, fill="both", pady=(5,5))
        
        # Pronunciation
        self.pronunciation_label = tk.Label(self.card_frame, text="", font=("Helvetica", 16, "italic"), bg="white")
        self.pronunciation_label.pack(pady=(2, 5))  # Position right below the part of speech

        # Add a search entry and button
        self.search_label = tk.Label(root, text="Search:", font=("Helvetica", 11))
        self.search_label.place(relx=0.01, rely=0.95, anchor="sw")

        self.search_entry = tk.Entry(root, font=("Helvetica", 12), width=15)
        self.search_entry.place(relx=0.1, rely=0.95, anchor="sw")


    def bind_keys(self):
        # Key bindings for left and right arrows
        self.root.bind("<Left>", self.prev_card_key)
        self.root.bind("<Right>", self.next_card_key)

        # Key binding for Spacebar to flip the card
        self.root.bind("<space>", self.flip_card_key)

        # GPT generated question
        self.root.bind("<Control-g>", self.generate_gre_question_key)

        # History of generated question
        self.root.bind("<Control-z>", self.show_stored_gre_question)
        
        # GPT generated word example
        self.root.bind("<Control-e>", lambda event: self.generate_gre_example())
        self.root.bind("<Control-q>", self.show_stored_gre_examples)

        # Search word
        self.root.bind("<Control-f>", lambda event: self.focus_search())
        self.root.bind("<Return>", lambda event: self.search_flashcard())
        self.search_entry.bind("<Control-a>", self.select_all_search_text)

        # GPT word root
        self.root.bind("<Control-space>", self.show_word_root)

    def show_front(self):
        self.showing_back = False
        card = self.flashcards[self.index]

        # Update the word and part of speech
        self.word_label.config(text=card["word"])
        self.pos_label.config(text=f"({card['part_of_speech']})")

        # Fetch and display the pronunciation
        pronunciation = self.fetch_pronunciation(card["word"])
        self.pronunciation_label.config(text=pronunciation)

        # Clear and enable the text widget for the example
        self.example_text.config(state="normal")
        self.example_text.delete("1.0", "end")

        # Highlight the word in the example
        word_to_highlight = card["word"]
        example = card["example"]
        pattern = r"\b" + re.escape(word_to_highlight) + r"[a-zA-Z]*\b"

        start_idx = 0
        for match in re.finditer(pattern, example, re.IGNORECASE):
            self.example_text.insert("end", example[start_idx:match.start()])
            self.example_text.insert("end", example[match.start():match.end()], "highlight")
            start_idx = match.end()
        self.example_text.insert("end", example[start_idx:])

        # Center align the content
        self.example_text.tag_configure("center", justify="center")
        self.example_text.tag_add("center", "1.0", "end")

        # Disable the text widget
        self.example_text.config(state="disabled")
        self.update_card_number()

    def show_back(self):
        self.showing_back = True
        card = self.flashcards[self.index]

        # Update the word and part of speech
        self.word_label.config(text=card["word"])
        self.pos_label.config(text=f"({card['part_of_speech']})")

        # Fetch and display the pronunciation
        pronunciation = self.fetch_pronunciation(card["word"])
        self.pronunciation_label.config(text=pronunciation)

        # Safely retrieve synonyms and definition
        synonyms = card.get("synonyms", "No synonyms available").strip()
        definition = card.get("definition", "No definition available").strip()

        # Clear and enable Text widget
        self.example_text.config(state="normal")
        self.example_text.delete("1.0", "end")

        # Insert Synonyms and Definition with proper line breaks
        self.example_text.insert("end", f"{synonyms}\n\n", "bold")
        self.example_text.insert("end", definition, "normal")

        # Apply text alignment
        self.example_text.tag_configure("center", justify="center")
        self.example_text.tag_configure("bold", font=("Helvetica", 14, "bold"))
        self.example_text.tag_configure("normal", font=("Helvetica", 14))
        self.example_text.tag_add("center", "1.0", "end")

        # Disable editing
        self.example_text.config(state="disabled")

    def flip_card(self):
        if self.showing_back:
            self.show_front()
        else:
            self.show_back()


    def update_card_number(self):
        current = self.index + 1
        total = len(self.flashcards)
        self.card_number_label.config(text=f"{current}/{total}")

    def prev_card_key(self, event):
        self.index = (self.index - 1) % len(self.flashcards)
        self.show_front()
        self.update_card_number()

    def next_card_key(self, event):
        self.index = (self.index + 1) % len(self.flashcards)
        self.show_front()
        self.update_card_number()

    def flip_card_key(self, event):
        if self.showing_back:
            self.show_front()
        else:
            self.show_back()

    def toggle_shuffle(self):
        if self.is_shuffled:
            # Restore to the original order
            self.flashcards = list(self.original_flashcards)
            self.shuffle_button.config(text="Shuffle")
            self.is_shuffled = False
        else:
            # Shuffle the flashcards
            random.shuffle(self.flashcards)
            self.shuffle_button.config(text="Restore Order")
            self.is_shuffled = True

        # Reset index and display the first card in the new order
        self.index = 0
        self.show_front()

    def generate_gre_question(self):
        card = self.flashcards[self.index]
        word = card["word"]

        # Generate the question
        part_of_speech = card["part_of_speech"]
        definition = card.get("definition", "No definition available")

        # Prepare the GPT prompt
        prompt = f"""Generate a GRE-style vocabulary question for the word "{word}" (Part of speech: {part_of_speech}, Definition: {definition}). 
        Provide a multiple-choice question with four options, where one is the correct answer. Clearly mark the correct answer."""

        try:
            # Use the latest openai.ChatCompletion.create method
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Adjust model to gpt-4 if you have access
                messages=[
                    {"role": "system", "content": "You are an assistant that creates GRE-style vocabulary questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )

            # Extract the response text
            gre_question = response['choices'][0]['message']['content']

            # Save the question to the file
            self.save_gre_question_to_file(word, gre_question)

            # Display the question
            self.show_gre_question_popup(gre_question)

        except Exception as e:
            print(f"Error: {e}")
            self.show_gre_question_popup("Failed to generate GRE question. Please check your API key or internet connection.")

            
    def show_gre_question_popup(self, question_text):
        popup = tk.Toplevel(self.root)
        popup.title("GRE Question")
        popup.geometry("500x300")

        question_label = tk.Label(popup, text=question_text, font=("Helvetica", 12), wraplength=450, justify="left")
        question_label.pack(pady=20, padx=20)

        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

        # Bind the Esc key to close the popup
        popup.bind("<Escape>", lambda event: popup.destroy())

    def generate_gre_question_key(self, event):
        self.generate_gre_question()

    def fetch_pronunciation(self, word):
        try:
            # Use Epitran for English IPA transcription
            epi = epitran.Epitran('eng-Latn')  # eng-Latn is for English
            ipa_transcription = epi.transliterate(word)
            return f"{ipa_transcription}"
        except Exception as e:
            print(f"Error fetching pronunciation: {e}")
            return "Pronunciation not available"

    def save_gre_question_to_file(self, word, question):
        # Define the directory to save questions (adjust path as needed)
        directory = os.path.join("questions")  # Adjust the directory as needed
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the file path
        file_path = os.path.join(directory, f"{word}.txt")

        # Write the question to the file
        with open(file_path, "a") as file:  # Append mode to avoid overwriting
            file.write(question + "\n\n")  # Separate each question with a newline

    def show_stored_gre_question(self, event=None):
        card = self.flashcards[self.index]
        word = card["word"]

        # Define the file path
        directory = os.path.join("questions")  # Adjust the directory as needed
        file_path = os.path.join(directory, f"{word}.txt")

        # Read the file content or handle missing file
        try:
            with open(file_path, "r") as file:
                gre_questions = file.read()
        except FileNotFoundError:
            gre_questions = "No questions found."

        # Create the popup
        popup = tk.Toplevel(self.root)
        popup.title(f"GRE Questions for {word}")
        popup.geometry("500x400")

        # Add a scrollbar
        scroll_bar = tk.Scrollbar(popup)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a Text widget with a scrollbar
        text_widget = tk.Text(popup, wrap="word", font=("Helvetica", 12), yscrollcommand=scroll_bar.set)
        text_widget.insert("1.0", gre_questions)
        text_widget.config(state="disabled")  # Disable editing
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Configure the scrollbar
        scroll_bar.config(command=text_widget.yview)

        # Close button (optional)
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

        # Bind Esc key to close the popup
        popup.bind("<Escape>", lambda event: popup.destroy())

    def generate_gre_example(self):
        card = self.flashcards[self.index]
        word = card["word"]

        # Prepare the GPT prompt
        prompt = f"""Generate a GRE-style example sentence for the word "{word}"."""
        
        try:
            # Use the latest OpenAI ChatCompletion.create method
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Adjust model to gpt-4 if needed
                messages=[
                    {"role": "system", "content": "You are an assistant that generates GRE-style example sentences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            # Extract the response text
            gre_example = response['choices'][0]['message']['content']

            # Save the example to the file
            self.save_gre_example_to_file(word, gre_example)

            # Display the example
            self.show_gre_example_popup(gre_example)

        except Exception as e:
            print(f"Error: {e}")
            self.show_gre_example_popup("Failed to generate GRE example. Please check your API key or internet connection.")

    def save_gre_example_to_file(self, word, example):
        # Define the directory to save examples
        directory = os.path.join("examples")  # Adjust the directory as needed
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

        # Define the file path
        file_path = os.path.join(directory, f"{word}.txt")

        # Write the example to the file
        with open(file_path, "a") as file:  # Append mode to avoid overwriting
            file.write(example + "\n\n")  # Separate each example with a newline

    def show_stored_gre_examples(self, event=None):
        card = self.flashcards[self.index]
        word = card["word"]

        # Define the file path
        directory = os.path.join("examples")  # Adjust the directory as needed
        file_path = os.path.join(directory, f"{word}.txt")

        # Read the file content or handle missing file
        try:
            with open(file_path, "r") as file:
                gre_examples = file.read()
        except FileNotFoundError:
            gre_examples = "No examples found."

        # Create the popup
        popup = tk.Toplevel(self.root)
        popup.title(f"GRE Examples for {word}")
        popup.geometry("500x400")

        # Add a scrollbar
        scroll_bar = tk.Scrollbar(popup)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a Text widget with a scrollbar
        text_widget = tk.Text(popup, wrap="word", font=("Helvetica", 12), yscrollcommand=scroll_bar.set)
        text_widget.insert("1.0", gre_examples)
        text_widget.config(state="disabled")  # Disable editing
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)

        # Configure the scrollbar
        scroll_bar.config(command=text_widget.yview)

        # Close button (optional)
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

        # Bind the Esc key to close the popup
        popup.bind("<Escape>", lambda event: popup.destroy())

    def show_gre_example_popup(self, example_text):
        # Create the popup window
        popup = tk.Toplevel(self.root)
        popup.title("Generated GRE Example")
        popup.geometry("500x300")

        # Display the GRE example
        example_label = tk.Label(popup, text=example_text, font=("Helvetica", 12), wraplength=450, justify="left")
        example_label.pack(pady=20, padx=20)

        # Add a close button
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

        # Bind the Esc key to close the popup
        popup.bind("<Escape>", lambda event: popup.destroy())

    def search_flashcard(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            print("Please enter a search term.")
            return

        # Find the first flashcard that matches the search term
        for i, card in enumerate(self.flashcards):
            if search_term in card["word"].lower() or search_term in card["example"].lower() or search_term in card["definition"].lower():
                self.index = i  # Go to the matching card
                self.show_front()
                self.update_card_number()
                return

        # If no match is found
        print(f"No flashcard found for search term: {search_term}")


    def focus_search(self):
        self.search_entry.focus_set()

    def select_all_search_text(self, event):
        # Select all text in the search entry box
        self.search_entry.select_range(0, tk.END)
        self.search_entry.icursor(tk.END)  # Place the cursor at the end of the text
        return "break"  # Prevent default behavior

    def show_word_root(self, event=None):
        card = self.flashcards[self.index]
        word = card["word"]

        # Prepare the GPT prompt
        prompt = f"""Provide the etymology and root word analysis of the word "{word}". Include the language of origin and its original meaning if possible."""

        try:
            # Use OpenAI API to get the root word information
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are an assistant that provides detailed etymology and root word analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )

            # Extract the response text
            root_info = response['choices'][0]['message']['content']

            # Display the root word information in a popup
            self.show_root_popup(root_info)

        except Exception as e:
            print(f"Error: {e}")
            self.show_root_popup("Failed to fetch root word information. Please check your API key or internet connection.")

    def show_root_popup(self, root_info):
        popup = tk.Toplevel(self.root)
        popup.title("Word Root Information")
        popup.geometry("500x300")

        # Create a frame to hold the Text widget and scrollbar
        frame = tk.Frame(popup)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Add a Text widget to display the root information
        text_widget = tk.Text(frame, wrap="word", font=("Helvetica", 12), state="normal")
        text_widget.insert("1.0", root_info)
        text_widget.config(state="disabled")  # Disable editing
        text_widget.pack(side="left", expand=True, fill="both")

        # Add a scrollbar
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Text widget to work with the scrollbar
        text_widget.config(yscrollcommand=scrollbar.set)

        # Add a Close button
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=10)

        # Bind the Esc key to close the popup
        popup.bind("<Escape>", lambda event: popup.destroy())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine multiple ODS files and load flashcards.")
    parser.add_argument("--path", nargs="+", required=True, help="Paths to the input ODS files (space-separated).")
    args = parser.parse_args()

    # Combine data from all provided ODS files
    combined_data = pd.DataFrame()
    for path in args.path:
        data = pd.read_excel(path, engine="odf")
        combined_data = pd.concat([combined_data, data], ignore_index=True)

    # Remove duplicates, prioritizing words from the first file (learnt.ods)
    combined_data = combined_data.drop_duplicates(subset=["Words"], keep="first")

    # Convert the combined data to flashcards
    flashcards = []
    for _, row in combined_data.iterrows():
        flashcard = {
            "word": row["Words"],
            "part_of_speech": row["Part of Speech"],
            "example": row["Examples"],
            "definition": row["Meanings"],
            "synonyms": row["Synonyms"]
        }
        flashcards.append(flashcard)

    root = tk.Tk()
    app = FlashcardApp(root, flashcards)
    root.mainloop()
