from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
import pygame
import json
import time
import threading
from datetime import datetime

pygame.mixer.init()

ALARM_FILE = "alarms.json"
alarms = []

def load_alarms():
    try:
        with open(ALARM_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  
    except json.JSONDecodeError:
        return []

def save_alarms():
    with open(ALARM_FILE, "w") as file:
        json.dump(alarms, file, indent=4)

def play_alarm_sound():
    pygame.mixer.music.load("alarm_sound.mp3")
    pygame.mixer.music.play(-1)  

def stop_alarm_sound(instance):  
    pygame.mixer.music.stop()  

def show_alarm_message():
    
    Clock.schedule_once(lambda dt: open_popup("Time to Take Your Medicine!", "⏰ Reminder: Take your medicine now!"))

def open_popup(title, message):
    
    content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

   
    content_layout.add_widget(Label(text=message))

    
    stop_button = Button(
        text="✔ Stop", 
        size_hint=(None, None), 
        size=(150, 50), 
        background_normal='', 
        background_color=(0, 1, 0, 1)  
    )
    stop_button.bind(on_press=lambda instance: stop_alarm_sound(instance))  
    content_layout.add_widget(stop_button)

    
    popup = Popup(
        title=title,
        content=content_layout,
        size_hint=(None, None),
        size=(400, 200)  
    )
    popup.open()


def delete_alarm(alarm_to_delete):
    alarms.remove(alarm_to_delete)
    save_alarms()

def check_alarms():
    while True:
        now = datetime.now().strftime("%H:%M")
        for alarm in alarms:
            if alarm["time"] == now:
                sound_thread = threading.Thread(target=play_alarm_sound, daemon=True)
                sound_thread.start()

               
                show_alarm_message()
                alarms.remove(alarm)
                save_alarms()
        time.sleep(60)

class MedicineAlarmApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        
        self.entry_medicine = TextInput(hint_text="Medicine Name", size_hint_y=None, height=40)
        self.entry_dose = TextInput(hint_text="Dose", size_hint_y=None, height=40)
        self.entry_time = TextInput(hint_text="Alarm Time (HH:MM)", size_hint_y=None, height=40)

        layout.add_widget(self.entry_medicine)
        layout.add_widget(self.entry_dose)
        layout.add_widget(self.entry_time)

        
        button_add = Button(text="Add Alarm", on_press=self.add_alarm, size_hint_y=None, height=50)
        layout.add_widget(button_add)

       
        button_view = Button(text="View Alarms", on_press=self.show_alarm_list, size_hint_y=None, height=50)
        layout.add_widget(button_view)

        return layout

    def add_alarm(self, instance):
        medicine_name = self.entry_medicine.text
        dose = self.entry_dose.text
        alarm_time = self.entry_time.text

        try:
            datetime.strptime(alarm_time, "%H:%M")
            alarms.append({"name": medicine_name, "dose": dose, "time": alarm_time})
            save_alarms()
            self.show_popup(f"Alarm Set for {medicine_name} at {alarm_time}")

            self.entry_medicine.text = ""
            self.entry_dose.text = ""
            self.entry_time.text = ""

        except ValueError:
            self.show_popup("Invalid Time. Please enter a valid time in HH:MM format.")

    def show_alarm_list(self, instance):
        Clock.schedule_once(lambda dt: self.open_alarm_list())

    def open_alarm_list(self):
        
        alarm_list_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        
        for alarm in alarms:
            alarm_item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            alarm_label = Label(text=f"{alarm['name']} - {alarm['dose']} at {alarm['time']}", size_hint_x=0.8)
            delete_button = Button(text="Delete", size_hint_x=0.2)
            delete_button.bind(on_press=lambda instance, alarm=alarm: self.delete_alarm_popup(alarm))  
            alarm_item_layout.add_widget(alarm_label)
            alarm_item_layout.add_widget(delete_button)
            alarm_list_layout.add_widget(alarm_item_layout)

       
        popup = Popup(title="Active Alarms",
                      content=alarm_list_layout,
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def delete_alarm_popup(self, alarm):
        
        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        
        content_layout.add_widget(Label(text=f"Are you sure you want to delete the alarm for {alarm['name']}?"))

       
        yes_button = Button(
            text="Yes", 
            size_hint=(None, None),
            size=(150, 50),  
            background_normal='', 
            background_color=(0, 1, 0, 1) 
        )
        yes_button.bind(on_press=lambda instance: self.delete_alarm_confirm(alarm, content_popup))  
        content_layout.add_widget(yes_button)

      
        no_button = Button(
            text="No", 
            size_hint=(None, None),
            size=(150, 50),  
            background_normal='', 
            background_color=(1, 0, 0, 1) 
        )
        no_button.bind(on_press=lambda instance: content_popup.dismiss())  
        content_layout.add_widget(no_button)

        
        content_popup = Popup(
            title="Delete Alarm?",
            content=content_layout,
            size_hint=(None, None),
            size=(400, 200)  
        )
        content_popup.open()


    def delete_alarm_confirm(self, alarm, delete_popup):
        try:
            
            alarms.remove(alarm)  
            self.update_alarm_list() 
            self.show_popup(f"Deleted alarm for {alarm['name']}")
        except ValueError:
            
            self.show_popup(f"Error: Alarm already deleted")
        
        
        delete_popup.dismiss()

        
        for popup in App.get_running_app().root_window.children:
            if isinstance(popup, Popup) and popup.title == "Active Alarms":
                popup.dismiss()

    def update_alarm_list(self):

        self.show_alarm_list(None) 

    def close_current_popup(self):
       
        for popup in App.get_running_app().root_window.children:
            if isinstance(popup, Popup):
                popup.dismiss()

    def show_popup(self, message):
        popup = Popup(title="Alert", content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
   
    alarms = load_alarms()

    
    threading.Thread(target=check_alarms, daemon=True).start()

    
    MedicineAlarmApp().run()
