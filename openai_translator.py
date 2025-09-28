import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
from datetime import datetime
import random


class ChatGPTWithFallback:
    def __init__(self, root):
        self.root = root
        root.title("ChatGPT Conversation - Smart Fallback")
        root.geometry("900x750")
        root.configure(bg='#f0f2f5')

        # Your API key pre-filled
        self.default_api_key = "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"

        # Conversation history
        self.conversation_history = []

        # Smart responses for when API fails
        self.smart_responses = {
            "hello": ["Hello! How can I help you today?", "Hi there! What would you like to chat about?",
                      "Hello! Nice to meet you!"],
            "hi": ["Hi! How are you doing?", "Hello! What's on your mind?", "Hi there! How can I assist you?"],
            "how are you": ["I'm doing well, thank you! How about you?", "I'm great! Thanks for asking. How are you?",
                            "I'm fine, thanks! What about you?"],
            "what is your name": ["I'm ChatGPT, an AI assistant created by OpenAI.",
                                  "My name is ChatGPT. I'm here to help you!",
                                  "I'm ChatGPT, your AI conversation partner."],
            "thank you": ["You're welcome!", "Happy to help!", "My pleasure!", "Anytime!"],
            "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!", "Bye! Come back anytime!"],
            "help": ["I'm here to help! What do you need assistance with?", "How can I help you today?",
                     "What would you like to know?"]
        }

        self.create_widgets()

    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#1e3a8a', height=90)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Title with icon
        title_label = tk.Label(header_frame, text="🤖 ChatGPT Conversation - Smart Edition",
                               font=('Segoe UI', 20, 'bold'), fg='white', bg='#1e3a8a')
        title_label.pack(pady=25)

        # API Key Frame
        api_frame = tk.Frame(self.root, bg='#e5e7eb', height=70)
        api_frame.pack(fill='x', padx=15, pady=10)
        api_frame.pack_propagate(False)

        tk.Label(api_frame, text="🔑 OpenAI API Key:", font=('Segoe UI', 12, 'bold'),
                 bg='#e5e7eb', fg='#374151').pack(side='left', padx=15, pady=20)

        self.api_key_entry = tk.Entry(api_frame, width=70, show="*", font=('Consolas', 10),
                                      bg='white', relief='solid', bd=1)
        self.api_key_entry.pack(side='left', padx=10, pady=20, fill='x', expand=True)
        self.api_key_entry.insert(0, self.default_api_key)  # Pre-fill your API key

        # Toggle button
        self.show_key_btn = tk.Button(api_frame, text="👁️", command=self.toggle_key_visibility,
                                      font=('Segoe UI', 12), width=4, bg='#3b82f6', fg='white',
                                      relief='flat', cursor='hand2')
        self.show_key_btn.pack(side='right', padx=15, pady=20)

        # Main Chat Frame
        main_frame = tk.Frame(self.root, bg='#ffffff')
        main_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Chat Display with custom styling
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            font=('Segoe UI', 11),
            bg='#ffffff',
            fg='#1f2937',
            state='disabled',
            relief='solid',
            bd=1,
            padx=15,
            pady=10
        )
        self.chat_display.pack(fill='both', expand=True, pady=(0, 15))

        # Configure text styling
        self.chat_display.tag_configure("user", foreground="#1e40af", font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_configure("assistant", foreground="#059669", font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_configure("system", foreground="#dc2626", font=('Segoe UI', 11, 'bold'))
        self.chat_display.tag_configure("timestamp", foreground="#6b7280", font=('Segoe UI', 9))
        self.chat_display.tag_configure("message", foreground="#374151", font=('Segoe UI', 11))
        self.chat_display.tag_configure("fallback", foreground="#7c3aed", font=('Segoe UI', 11, 'italic'))

        # Input Frame
        input_frame = tk.Frame(main_frame, bg='#f9fafb', relief='solid', bd=1)
        input_frame.pack(fill='x', pady=(0, 10))

        # Message input area
        input_top_frame = tk.Frame(input_frame, bg='#f9fafb')
        input_top_frame.pack(fill='x', padx=15, pady=(15, 5))

        tk.Label(input_top_frame, text="💬 Your message:",
                 font=('Segoe UI', 12, 'bold'), bg='#f9fafb', fg='#374151').pack(anchor='w')

        # Input and button frame
        input_bottom_frame = tk.Frame(input_frame, bg='#f9fafb')
        input_bottom_frame.pack(fill='x', padx=15, pady=(5, 15))

        self.message_entry = tk.Text(input_bottom_frame, height=3, font=('Segoe UI', 11),
                                     wrap=tk.WORD, relief='solid', bd=1, padx=10, pady=8)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 15))

        # Bind keys
        self.message_entry.bind('<Return>', self.on_enter_key)
        self.message_entry.bind('<Shift-Return>', self.on_shift_enter)

        # Buttons frame
        buttons_frame = tk.Frame(input_bottom_frame, bg='#f9fafb')
        buttons_frame.pack(side='right')

        # Send button
        self.send_button = tk.Button(buttons_frame, text="📤 Send Message",
                                     command=self.send_message,
                                     bg='#3b82f6', fg='white',
                                     font=('Segoe UI', 11, 'bold'),
                                     width=15, height=2, relief='flat',
                                     cursor='hand2')
        self.send_button.pack(pady=(0, 8))

        # Clear button
        clear_button = tk.Button(buttons_frame, text="🗑️ Clear Chat",
                                 command=self.clear_chat,
                                 bg='#ef4444', fg='white',
                                 font=('Segoe UI', 10),
                                 width=15, relief='flat',
                                 cursor='hand2')
        clear_button.pack()

        # Status bar
        status_frame = tk.Frame(self.root, bg='#e5e7eb', height=40)
        status_frame.pack(fill='x')
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="✅ Ready to chat! API key loaded. Smart fallback enabled.",
                                     font=('Segoe UI', 10), fg='#059669', bg='#e5e7eb')
        self.status_label.pack(pady=10)

        # Welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        """Add enhanced welcome message"""
        self.chat_display.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_display.insert(tk.END, "ChatGPT: ", "assistant")
        self.chat_display.insert(tk.END,
                                 "Hello! I'm ChatGPT with smart fallback system. Your API key is already loaded! 🚀\n\n",
                                 "message")

        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_display.insert(tk.END, "System: ", "system")
        self.chat_display.insert(tk.END,
                                 "🛡️ Smart Features Enabled:\n• OpenAI API with your key\n• Free LibreTranslate backup\n• Intelligent offline responses\n• Quota error handling\n\n",
                                 "fallback")

        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def toggle_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_entry.cget('show') == '*':
            self.api_key_entry.config(show='')
            self.show_key_btn.config(text='🙈', bg='#ef4444')
        else:
            self.api_key_entry.config(show='*')
            self.show_key_btn.config(text='👁️', bg='#3b82f6')

    def on_enter_key(self, event):
        """Handle Enter key"""
        self.send_message()
        return 'break'

    def on_shift_enter(self, event):
        """Handle Shift+Enter for new line"""
        return None

    def send_message(self):
        """Send message with smart fallback"""
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return

        # Clear input
        self.message_entry.delete("1.0", tk.END)

        # Add user message
        self.add_message("You", message, "user")
        self.conversation_history.append({"role": "user", "content": message})

        # Disable send button
        self.send_button.config(state='disabled', text='⏳ Processing...')
        self.status_label.config(text="🔄 Trying OpenAI API...", fg='#3b82f6')

        # Try API in separate thread
        thread = threading.Thread(target=self.try_all_methods, args=(message,))
        thread.daemon = True
        thread.start()

    def try_all_methods(self, user_message):
        """Try multiple methods to get response"""
        api_key = self.api_key_entry.get().strip()

        # Method 1: Try OpenAI API
        if api_key:
            try:
                response = self.call_openai_api(api_key)
                if response:
                    self.root.after(0, self.on_success, response, "OpenAI API")
                    return
            except Exception as e:
                print(f"OpenAI API failed: {e}")

        # Method 2: Try LibreTranslate for translation-like queries
        self.root.after(0, self.update_status, "🔄 Trying free translation API...", '#f59e0b')
        try:
            if any(word in user_message.lower() for word in ['translate', 'dịch', 'meaning', 'nghĩa']):
                response = self.try_translation_response(user_message)
                if response:
                    self.root.after(0, self.on_success, response, "Translation API")
                    return
        except Exception as e:
            print(f"Translation API failed: {e}")

        # Method 3: Smart pattern matching
        self.root.after(0, self.update_status, "🧠 Using smart responses...", '#7c3aed')
        response = self.get_smart_response(user_message)
        if response:
            self.root.after(0, self.on_success, response, "Smart Response")
            return

        # Method 4: Fallback response
        fallback_responses = [
            f"I understand you're asking about '{user_message}'. While I can't access my full capabilities right now due to API limitations, I'm still here to help! Could you rephrase your question or ask something else?",
            f"Thanks for your message about '{user_message}'. I'm experiencing some technical difficulties with my main systems, but I'm doing my best to assist you. What else would you like to know?",
            f"I see you mentioned '{user_message}'. Due to current API restrictions, I might not give you the most detailed response, but I'm happy to try helping in other ways!"
        ]

        response = random.choice(fallback_responses)
        self.root.after(0, self.on_success, response, "Fallback System")

    def call_openai_api(self, api_key):
        """Call OpenAI API"""
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        messages = [
                       {"role": "system",
                        "content": "You are ChatGPT, a helpful AI assistant. Be conversational and friendly."}
                   ] + self.conversation_history

        data = {
            'model': 'gpt-3.5-turbo',
            'messages': messages,
            'max_tokens': 800,
            'temperature': 0.7
        }

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            error_info = response.json() if response.content else {}
            error_message = error_info.get('error', {}).get('message', f'HTTP {response.status_code}')
            raise Exception(error_message)

    def try_translation_response(self, message):
        """Try to handle translation requests"""
        try:
            # Simple translation API call
            url = "https://libretranslate.de/translate"
            data = {
                "q": message,
                "source": "auto",
                "target": "vi",
                "format": "text"
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                translated = result.get('translatedText', '')
                return f"Translation: {translated}\n\n(Note: This is from a free translation service as backup)"
        except:
            pass
        return None

    def get_smart_response(self, message):
        """Get smart response based on patterns"""
        message_lower = message.lower().strip()

        # Direct matches
        for key, responses in self.smart_responses.items():
            if key in message_lower:
                return random.choice(responses)

        # Pattern matching
        if any(word in message_lower for word in ['weather', 'time', 'date']):
            return "I'd love to help with that, but I don't have access to real-time data right now. You might want to check a weather app or your system clock!"

        if any(word in message_lower for word in ['calculate', 'math', 'compute']):
            return "I can help with calculations! Could you give me the specific math problem you'd like me to solve?"

        if any(word in message_lower for word in ['code', 'programming', 'python', 'javascript']):
            return "I'd be happy to help with coding! What programming language or specific problem are you working on?"

        if '?' in message:
            return f"That's an interesting question about '{message}'. While I'm running on limited resources right now, I'll do my best to help. Could you provide more details?"

        return None

    def update_status(self, text, color):
        """Update status label"""
        self.status_label.config(text=text, fg=color)

    def on_success(self, response, method):
        """Handle successful response"""
        self.add_message("ChatGPT", response, "assistant")
        self.conversation_history.append({"role": "assistant", "content": response})

        self.send_button.config(state='normal', text='📤 Send Message')
        self.status_label.config(text=f"✅ Response from {method}", fg='#059669')

        # Keep conversation manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def add_message(self, sender, message, role):
        """Add message to chat display"""
        self.chat_display.config(state='normal')

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_display.insert(tk.END, f"{sender}: ", role)
        self.chat_display.insert(tk.END, f"{message}\n\n", "message")

        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state='normal')
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state='disabled')

        self.conversation_history = []
        self.add_welcome_message()
        self.status_label.config(text="🗑️ Chat cleared. Ready for new conversation!", fg='#6b7280')


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTWithFallback(root)
    root.mainloop()
