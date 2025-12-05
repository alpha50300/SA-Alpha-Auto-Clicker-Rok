import pyautogui
import time
import json
import os
from datetime import datetime
import keyboard
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sys

class AutoClickerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🖱️ SA Alpha | Auto Clicker  - لوحة التحكم الاحترافية")
        self.window.geometry("1200x800")
        self.window.configure(bg="#0f172a")
        
        self.points = []
        self.is_running = False
        self.cycles = 1
        self.current_cycle = 0
        self.data_file = "clicker_data.json"
        self.is_picking_location = False
        self.edit_index = None
        self.cycle_delays = []  # قائمة التأخيرات بين الدورات
        
        self.load_data()
        self.setup_ui()
        self.update_stats()
        
        # مراقبة مفتاح ESC للإيقاف
        keyboard.on_press_key('esc', lambda _: self.stop_clicker() if self.is_running else None)
        
    def load_data(self):
        """تحميل البيانات المحفوظة"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.points = data.get('points', [])
                    self.cycles = data.get('cycles', 1)
                    self.cycle_delays = data.get('cycle_delays', [])
            except:
                pass
    
    def save_data(self):
        """حفظ البيانات"""
        data = {
            'points': self.points, 
            'cycles': self.cycles,
            'cycle_delays': self.cycle_delays
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def setup_ui(self):
        """إنشاء واجهة المستخدم"""
        
        # الإطار العلوي - العنوان
        header_frame = tk.Frame(self.window, bg="#1e293b", height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🖱️ SA Alpha | Auto Clicker  - لوحة التحكم الاحترافي",
            font=("Arial", 24, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        )
        title_label.pack(pady=20)
        
        # الإطار الرئيسي
        main_frame = tk.Frame(self.window, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # الجانب الأيمن - الإحصائيات والتحكم
        right_frame = tk.Frame(main_frame, bg="#0f172a", width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # بطاقة الإحصائيات
        stats_frame = tk.LabelFrame(
            right_frame,
            text="📊 الإحصائيات المباشرة",
            font=("Arial", 14, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            bd=2,
            relief=tk.RAISED
        )
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # إحصائيات
        self.total_points_label = self.create_stat_label(stats_frame, "إجمالي النقاط:", "0", "#22c55e")
        self.active_points_label = self.create_stat_label(stats_frame, "النقاط النشطة:", "0", "#f59e0b")
        self.current_cycle_label = self.create_stat_label(stats_frame, "الدورة الحالية:", "0/0", "#3b82f6")
        self.total_time_label = self.create_stat_label(stats_frame, "الوقت الإجمالي:", "00:00:00", "#a855f7")
        self.next_click_label = self.create_stat_label(stats_frame, "النقر التالي:", "00:00:00", "#ec4899")
        
        # بطاقة التحكم
        control_frame = tk.LabelFrame(
            right_frame,
            text="🎮 لوحة التحكم",
            font=("Arial", 14, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            bd=2,
            relief=tk.RAISED
        )
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # زر إدارة تأخيرات الدورات
        tk.Button(
            control_frame,
            text="⏳ إدارة الدورات والتأخيرات",
            font=("Arial", 12, "bold"),
            bg="#6366f1",
            fg="white",
            activebackground="#4f46e5",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            command=self.manage_cycle_delays,
            height=2
        ).pack(fill=tk.X, padx=15, pady=10)
        
        # أزرار التحكم
        self.start_button = tk.Button(
            control_frame,
            text="▶️ تشغيل",
            font=("Arial", 14, "bold"),
            bg="#22c55e",
            fg="white",
            activebackground="#16a34a",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            command=self.start_clicker,
            height=2
        )
        self.start_button.pack(fill=tk.X, padx=15, pady=5)
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏸️ إيقاف",
            font=("Arial", 14, "bold"),
            bg="#ef4444",
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            command=self.stop_clicker,
            height=2,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, padx=15, pady=5)
        
        # بطاقة الإجراءات
        actions_frame = tk.LabelFrame(
            right_frame,
            text="⚡ الإجراءات السريعة",
            font=("Arial", 14, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            bd=2,
            relief=tk.RAISED
        )
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_action_button(actions_frame, "➕ إضافة نقطة", self.add_point, "#3b82f6")
        self.create_action_button(actions_frame, "🗑️ حذف الكل", self.clear_all_points, "#ef4444")
        self.create_action_button(actions_frame, "💾 حفظ", self.save_data, "#8b5cf6")
        self.create_action_button(actions_frame, "📥 تحميل", self.load_and_refresh, "#f59e0b")
        
        # معلومات
        info_frame = tk.Frame(right_frame, bg="#1e293b", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = """
💡 نصائح الاستخدام:

✨ إضافة نقطة:
  اضغط "إضافة نقطة" ثم انقر
  على الموقع المطلوب

✏️ تعديل نقطة:
  اضغط مرتين على النقطة

🗑️ حذف نقطة:
  اختر النقطة واضغط حذف

⏸️ إيقاف سريع:
  اضغط ESC في أي وقت

🔄 الدورات:
  حدد عدد مرات التكرار
        """
        
        tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            bg="#1e293b",
            fg="#94a3b8",
            justify=tk.RIGHT,
            anchor="e"
        ).pack(padx=15, pady=15)
        
        # الجانب الأيسر - قائمة النقاط
        left_frame = tk.Frame(main_frame, bg="#0f172a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # عنوان القائمة
        list_header = tk.Frame(left_frame, bg="#1e293b", height=50)
        list_header.pack(fill=tk.X, pady=(0, 10))
        list_header.pack_propagate(False)
        
        tk.Label(
            list_header,
            text="📋 قائمة النقاط",
            font=("Arial", 16, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        ).pack(pady=10)
        
        # جدول النقاط
        table_frame = tk.Frame(left_frame, bg="#1e293b")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Custom.Treeview",
            background="#334155",
            foreground="white",
            fieldbackground="#334155",
            borderwidth=0,
            font=("Arial", 11),
            rowheight=35
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1e293b",
            foreground="#38bdf8",
            borderwidth=0,
            font=("Arial", 12, "bold"),
            relief=tk.FLAT
        )
        style.map('Custom.Treeview', background=[('selected', '#3b82f6')])
        
        columns = ("#", "الموقع", "التأخير", "الحالة")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            selectmode='browse'
        )
        
        # تحديد عرض الأعمدة
        self.tree.column("#", width=50, anchor=tk.CENTER)
        self.tree.column("الموقع", width=200, anchor=tk.CENTER)
        self.tree.column("التأخير", width=200, anchor=tk.CENTER)
        self.tree.column("الحالة", width=150, anchor=tk.CENTER)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # أحداث الجدول
        self.tree.bind('<Double-1>', self.edit_point)
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # تحديث القائمة
        self.refresh_tree()
        
    def create_stat_label(self, parent, title, value, color):
        """إنشاء تسمية إحصائية"""
        container = tk.Frame(parent, bg="#1e293b")
        container.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            container,
            text=title,
            font=("Arial", 11),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack(side=tk.RIGHT, padx=5)
        
        value_label = tk.Label(
            container,
            text=value,
            font=("Arial", 12, "bold"),
            bg="#1e293b",
            fg=color
        )
        value_label.pack(side=tk.RIGHT, padx=5)
        
        return value_label
    
    def create_action_button(self, parent, text, command, color):
        """إنشاء زر إجراء"""
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            cursor="hand2",
            relief=tk.FLAT,
            command=command,
            height=2
        )
        btn.pack(fill=tk.X, padx=15, pady=5)
        
    def refresh_tree(self):
        """تحديث جدول النقاط"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, point in enumerate(self.points, 1):
            location = f"({point['x']}, {point['y']})"
            delay = point['delay']
            delay_str = f"{delay['hours']}س {delay['minutes']}د {delay['seconds']}ث"
            status = "✅ مُفعّلة" if point['enabled'] else "❌ معطّلة"
            
            self.tree.insert('', tk.END, values=(i, location, delay_str, status))
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        if not hasattr(self, 'total_points_label'):
            return
            
        active = sum(1 for p in self.points if p['enabled'])
        self.total_points_label.config(text=str(len(self.points)))
        self.active_points_label.config(text=str(active))
        self.current_cycle_label.config(text=f"{self.current_cycle}/{self.cycles}")
        
        total_seconds = 0
        for point in self.points:
            if point['enabled']:
                delay = point['delay']
                total_seconds += delay['hours'] * 3600 + delay['minutes'] * 60 + delay['seconds']
        
        total_time = total_seconds * self.cycles
        self.total_time_label.config(text=self.format_time(total_time))
    
    def format_time(self, seconds):
        """تنسيق الوقت"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def add_point(self):
        """إضافة نقطة جديدة"""
        self.is_picking_location = True
        self.window.attributes('-alpha', 0.3)
        messagebox.showinfo("إضافة نقطة", "انقر على الموقع المطلوب على الشاشة")
        
        def on_click(x, y, button, pressed):
            if pressed and self.is_picking_location:
                self.is_picking_location = False
                self.window.attributes('-alpha', 1.0)
                
                # نافذة إدخال التأخير
                delay_window = tk.Toplevel(self.window)
                delay_window.title("تحديد التأخير")
                delay_window.geometry("400x300")
                delay_window.configure(bg="#1e293b")
                delay_window.transient(self.window)
                delay_window.grab_set()
                
                tk.Label(
                    delay_window,
                    text=f"📍 الموقع: ({x}, {y})",
                    font=("Arial", 14, "bold"),
                    bg="#1e293b",
                    fg="#38bdf8"
                ).pack(pady=20)
                
                tk.Label(
                    delay_window,
                    text="⏱️ حدد التأخير بعد هذه النقطة:",
                    font=("Arial", 12),
                    bg="#1e293b",
                    fg="#cbd5e1"
                ).pack(pady=10)
                
                inputs_frame = tk.Frame(delay_window, bg="#1e293b")
                inputs_frame.pack(pady=10)
                
                tk.Label(inputs_frame, text="ساعات:", bg="#1e293b", fg="white").grid(row=0, column=0, padx=5, pady=5)
                hours_var = tk.StringVar(value="0")
                tk.Spinbox(inputs_frame, from_=0, to=23, textvariable=hours_var, width=10).grid(row=0, column=1, padx=5, pady=5)
                
                tk.Label(inputs_frame, text="دقائق:", bg="#1e293b", fg="white").grid(row=1, column=0, padx=5, pady=5)
                minutes_var = tk.StringVar(value="0")
                tk.Spinbox(inputs_frame, from_=0, to=59, textvariable=minutes_var, width=10).grid(row=1, column=1, padx=5, pady=5)
                
                tk.Label(inputs_frame, text="ثواني:", bg="#1e293b", fg="white").grid(row=2, column=0, padx=5, pady=5)
                seconds_var = tk.StringVar(value="1")
                tk.Spinbox(inputs_frame, from_=0, to=59, textvariable=seconds_var, width=10).grid(row=2, column=1, padx=5, pady=5)
                
                def save_point():
                    point = {
                        'x': x,
                        'y': y,
                        'delay': {
                            'hours': int(hours_var.get()),
                            'minutes': int(minutes_var.get()),
                            'seconds': int(seconds_var.get())
                        },
                        'enabled': True
                    }
                    self.points.append(point)
                    self.save_data()
                    self.refresh_tree()
                    self.update_stats()
                    delay_window.destroy()
                
                tk.Button(
                    delay_window,
                    text="✅ حفظ",
                    font=("Arial", 12, "bold"),
                    bg="#22c55e",
                    fg="white",
                    command=save_point,
                    cursor="hand2"
                ).pack(pady=20)
                
                return False
        
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def edit_point(self, event=None):
        """تعديل نقطة"""
        selection = self.tree.selection()
        if not selection:
            return
        
        index = self.tree.index(selection[0])
        point = self.points[index]
        
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"تعديل النقطة #{index + 1}")
        edit_window.geometry("450x400")
        edit_window.configure(bg="#1e293b")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        tk.Label(
            edit_window,
            text=f"✏️ تعديل النقطة #{index + 1}",
            font=("Arial", 16, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        ).pack(pady=20)
        
        # الموقع
        location_frame = tk.Frame(edit_window, bg="#1e293b")
        location_frame.pack(pady=10)
        
        tk.Label(
            location_frame,
            text=f"📍 الموقع الحالي: ({point['x']}, {point['y']})",
            font=("Arial", 12),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack()
        
        tk.Button(
            location_frame,
            text="📌 تغيير الموقع",
            font=("Arial", 11),
            bg="#3b82f6",
            fg="white",
            command=lambda: self.change_location(index, edit_window),
            cursor="hand2"
        ).pack(pady=5)
        
        # التأخير
        tk.Label(
            edit_window,
            text="⏱️ التأخير:",
            font=("Arial", 12),
            bg="#1e293b",
            fg="#cbd5e1"
        ).pack(pady=10)
        
        delay_frame = tk.Frame(edit_window, bg="#1e293b")
        delay_frame.pack()
        
        tk.Label(delay_frame, text="ساعات:", bg="#1e293b", fg="white").grid(row=0, column=0, padx=5, pady=5)
        hours_var = tk.StringVar(value=str(point['delay']['hours']))
        tk.Spinbox(delay_frame, from_=0, to=23, textvariable=hours_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(delay_frame, text="دقائق:", bg="#1e293b", fg="white").grid(row=1, column=0, padx=5, pady=5)
        minutes_var = tk.StringVar(value=str(point['delay']['minutes']))
        tk.Spinbox(delay_frame, from_=0, to=59, textvariable=minutes_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(delay_frame, text="ثواني:", bg="#1e293b", fg="white").grid(row=2, column=0, padx=5, pady=5)
        seconds_var = tk.StringVar(value=str(point['delay']['seconds']))
        tk.Spinbox(delay_frame, from_=0, to=59, textvariable=seconds_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # الحالة
        enabled_var = tk.BooleanVar(value=point['enabled'])
        tk.Checkbutton(
            edit_window,
            text="✅ نقطة مُفعّلة",
            variable=enabled_var,
            font=("Arial", 11),
            bg="#1e293b",
            fg="white",
            selectcolor="#334155",
            activebackground="#1e293b",
            activeforeground="white"
        ).pack(pady=10)
        
        # أزرار
        buttons_frame = tk.Frame(edit_window, bg="#1e293b")
        buttons_frame.pack(pady=20)
        
        def save_changes():
            self.points[index]['delay'] = {
                'hours': int(hours_var.get()),
                'minutes': int(minutes_var.get()),
                'seconds': int(seconds_var.get())
            }
            self.points[index]['enabled'] = enabled_var.get()
            self.save_data()
            self.refresh_tree()
            self.update_stats()
            edit_window.destroy()
        
        tk.Button(
            buttons_frame,
            text="💾 حفظ",
            font=("Arial", 11, "bold"),
            bg="#22c55e",
            fg="white",
            command=save_changes,
            cursor="hand2",
            width=12
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="❌ إلغاء",
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            command=edit_window.destroy,
            cursor="hand2",
            width=12
        ).pack(side=tk.RIGHT, padx=5)

    def change_location(self, index, edit_window):
        """تغيير موقع النقطة عند التعديل"""
        self.is_picking_location = True
        self.window.attributes('-alpha', 0.3)
        messagebox.showinfo("تغيير الموقع", "انقر على الموقع الجديد على الشاشة")

        def on_click(x, y, button, pressed):
            if pressed and self.is_picking_location:
                self.is_picking_location = False
                self.window.attributes('-alpha', 1.0)

                self.points[index]['x'] = x
                self.points[index]['y'] = y
                self.save_data()
                self.refresh_tree()
                messagebox.showinfo("تم", f"تم تغيير الموقع إلى ({x}, {y})")
                return False

        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def show_context_menu(self, event):
        """قائمة يمين لحذف نقطة"""
        try:
            row = self.tree.identify_row(event.y)
            if not row:
                return
            self.tree.selection_set(row)
            index = self.tree.index(row)

            menu = tk.Menu(self.window, tearoff=0, bg="#1e293b", fg="white")
            menu.add_command(label="🗑️ حذف", command=lambda: self.delete_point(index))
            menu.post(event.x_root, event.y_root)

        except:
            pass

    def delete_point(self, index):
        """حذف نقطة معينة"""
        confirm = messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذه النقطة؟")
        if confirm:
            del self.points[index]
            self.save_data()
            self.refresh_tree()
            self.update_stats()

    def clear_all_points(self):
        """حذف كل النقاط"""
        confirm = messagebox.askyesno("تحذير", "هل تريد حذف جميع النقاط؟")
        if confirm:
            self.points = []
            self.save_data()
            self.refresh_tree()
            self.update_stats()

    def load_and_refresh(self):
        """تحميل البيانات وتحديث الواجهة"""
        self.load_data()
        self.refresh_tree()
        self.update_stats()

    def update_cycles(self):
        """تحديث عدد الدورات"""
        try:
            new_cycles = int(self.cycles_var.get()) if hasattr(self, 'cycles_var') else self.cycles
            old_cycles = self.cycles
            self.cycles = new_cycles
            
            # تحديث قائمة التأخيرات حسب عدد الدورات الجديد
            if new_cycles > old_cycles:
                # إضافة تأخيرات افتراضية للدورات الجديدة
                for i in range(old_cycles, new_cycles):
                    self.cycle_delays.append({'hours': 0, 'minutes': 0, 'seconds': 0})
            elif new_cycles < old_cycles:
                # حذف التأخيرات الزائدة
                self.cycle_delays = self.cycle_delays[:new_cycles]
            
            self.save_data()
            self.update_stats()
        except:
            messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح")

    def manage_cycle_delays(self):
        """نافذة إدارة تأخيرات الدورات"""
        # التأكد من وجود تأخيرات لكل الدورات
        while len(self.cycle_delays) < self.cycles:
            self.cycle_delays.append({'hours': 0, 'minutes': 0, 'seconds': 0})
        
        delays_window = tk.Toplevel(self.window)
        delays_window.title("⏳ إدارة الدورات والتأخيرات")
        delays_window.geometry("700x600")
        delays_window.configure(bg="#0f172a")
        delays_window.transient(self.window)
        delays_window.grab_set()
        
        # العنوان
        header_frame = tk.Frame(delays_window, bg="#1e293b", height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="⏳ إدارة الدورات والتأخيرات",
            font=("Arial", 18, "bold"),
            bg="#1e293b",
            fg="#38bdf8"
        ).pack(pady=25)
        
        # أزرار الإضافة والحذف
        controls_frame = tk.Frame(delays_window, bg="#0f172a")
        controls_frame.pack(pady=10)
        
        def add_cycle():
            self.cycles += 1
            self.cycle_delays.append({'hours': 0, 'minutes': 0, 'seconds': 0})
            refresh_cycles_list()
        
        def remove_cycle():
            if self.cycles > 1:
                self.cycles -= 1
                if len(self.cycle_delays) > 0:
                    self.cycle_delays.pop()
                refresh_cycles_list()
            else:
                messagebox.showwarning("تحذير", "يجب أن يكون هناك دورة واحدة على الأقل!")
        
        tk.Button(
            controls_frame,
            text="➕ إضافة دورة",
            font=("Arial", 11, "bold"),
            bg="#22c55e",
            fg="white",
            command=add_cycle,
            cursor="hand2",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            controls_frame,
            text="➖ حذف دورة",
            font=("Arial", 11, "bold"),
            bg="#ef4444",
            fg="white",
            command=remove_cycle,
            cursor="hand2",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        cycles_count_label = tk.Label(
            controls_frame,
            text=f"🔄 عدد الدورات: {self.cycles}",
            font=("Arial", 12, "bold"),
            bg="#0f172a",
            fg="#38bdf8"
        )
        cycles_count_label.pack(side=tk.LEFT, padx=15)
        
        # إطار القائمة مع سكرول
        canvas_frame = tk.Frame(delays_window, bg="#0f172a")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0f172a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # متغيرات لحفظ القيم
        delay_vars = []
        
        def refresh_cycles_list():
            # مسح القائمة الحالية
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            delay_vars.clear()
            
            # تحديث عداد الدورات
            cycles_count_label.config(text=f"🔄 عدد الدورات: {self.cycles}")
            
            # التأكد من وجود تأخيرات كافية
            while len(self.cycle_delays) < self.cycles:
                self.cycle_delays.append({'hours': 0, 'minutes': 0, 'seconds': 0})
            
            # إنشاء حقول لكل دورة
            for i in range(self.cycles):
                cycle_frame = tk.LabelFrame(
                    scrollable_frame,
                    text=f"🔄 الدورة {i + 1}" + (f" → التأخير قبل الدورة {i + 2}" if i < self.cycles - 1 else " (آخر دورة - لا يوجد تأخير)"),
                    font=("Arial", 11, "bold"),
                    bg="#1e293b",
                    fg="#38bdf8" if i < self.cycles - 1 else "#94a3b8",
                    bd=2,
                    relief=tk.RAISED
                )
                cycle_frame.pack(fill=tk.X, padx=10, pady=8)
                
                # إذا كانت آخر دورة، لا نضيف حقول التأخير
                if i == self.cycles - 1:
                    tk.Label(
                        cycle_frame,
                        text="✅ هذه آخر دورة - لا يحتاج تأخير بعدها",
                        font=("Arial", 10, "italic"),
                        bg="#1e293b",
                        fg="#94a3b8"
                    ).pack(pady=10)
                    continue
                
                inputs_frame = tk.Frame(cycle_frame, bg="#1e293b")
                inputs_frame.pack(pady=10, padx=15)
                
                # الحصول على القيم الحالية
                current_delay = self.cycle_delays[i] if i < len(self.cycle_delays) else {'hours': 0, 'minutes': 0, 'seconds': 0}
                
                # ساعات
                tk.Label(inputs_frame, text="⏰ ساعات:", bg="#1e293b", fg="white", font=("Arial", 10)).grid(row=0, column=0, padx=8, pady=5)
                hours_var = tk.StringVar(value=str(current_delay['hours']))
                tk.Spinbox(inputs_frame, from_=0, to=23, textvariable=hours_var, width=8,
                          bg="#334155", fg="white", buttonbackground="#475569", font=("Arial", 10)).grid(row=0, column=1, padx=8, pady=5)
                
                # دقائق
                tk.Label(inputs_frame, text="⏱️ دقائق:", bg="#1e293b", fg="white", font=("Arial", 10)).grid(row=0, column=2, padx=8, pady=5)
                minutes_var = tk.StringVar(value=str(current_delay['minutes']))
                tk.Spinbox(inputs_frame, from_=0, to=59, textvariable=minutes_var, width=8,
                          bg="#334155", fg="white", buttonbackground="#475569", font=("Arial", 10)).grid(row=0, column=3, padx=8, pady=5)
                
                # ثواني
                tk.Label(inputs_frame, text="⏲️ ثواني:", bg="#1e293b", fg="white", font=("Arial", 10)).grid(row=0, column=4, padx=8, pady=5)
                seconds_var = tk.StringVar(value=str(current_delay['seconds']))
                tk.Spinbox(inputs_frame, from_=0, to=59, textvariable=seconds_var, width=8,
                          bg="#334155", fg="white", buttonbackground="#475569", font=("Arial", 10)).grid(row=0, column=5, padx=8, pady=5)
                
                delay_vars.append({
                    'hours': hours_var,
                    'minutes': minutes_var,
                    'seconds': seconds_var
                })
            
            # تحديث منطقة السكرول
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # عرض القائمة الأولية
        refresh_cycles_list()
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # زر الحفظ
        def save_delays():
            self.cycle_delays = []
            for var_set in delay_vars:
                self.cycle_delays.append({
                    'hours': int(var_set['hours'].get()),
                    'minutes': int(var_set['minutes'].get()),
                    'seconds': int(var_set['seconds'].get())
                })
            self.save_data()
            self.update_stats()
            messagebox.showinfo("نجح", f"تم حفظ {self.cycles} دورة بتأخيراتها")
            delays_window.destroy()
        
        buttons_frame = tk.Frame(delays_window, bg="#0f172a")
        buttons_frame.pack(pady=15)
        
        tk.Button(
            buttons_frame,
            text="💾 حفظ جميع التعديلات",
            font=("Arial", 12, "bold"),
            bg="#22c55e",
            fg="white",
            command=save_delays,
            cursor="hand2",
            width=22,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            buttons_frame,
            text="❌ إلغاء",
            font=("Arial", 12, "bold"),
            bg="#ef4444",
            fg="white",
            command=delays_window.destroy,
            cursor="hand2",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)

    def start_clicker(self):
        """تشغيل النقر التلقائي"""
        if self.is_running:
            return

        if not any(p['enabled'] for p in self.points):
            messagebox.showerror("خطأ", "لا توجد نقاط مفعلة!")
            return

        self.is_running = True
        self.current_cycle = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        threading.Thread(target=self.run_clicker, daemon=True).start()

    def stop_clicker(self):
        """إيقاف النقر"""
        if self.is_running:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def run_clicker(self):
        """التنفيذ الرئيسي للنقر"""
        while self.is_running and self.current_cycle < self.cycles:
            self.current_cycle += 1
            self.update_stats()

            for point in self.points:
                if not self.is_running:
                    break

                if point['enabled']:
                    delay = point['delay']
                    delay_seconds = delay['hours'] * 3600 + delay['minutes'] * 60 + delay['seconds']

                    # تحديث الوقت التالي
                    target_time = datetime.now().timestamp() + delay_seconds
                    self.next_click_label.config(text=self.format_time(delay_seconds))

                    time.sleep(delay_seconds)
                    pyautogui.click(point['x'], point['y'])

            # تأخير بين الدورات (إلا في الدورة الأخيرة)
            if self.is_running and self.current_cycle < self.cycles:
                # استخدام التأخير المخصص لهذه الدورة
                cycle_index = self.current_cycle - 1  # الدورة الحالية - 1
                
                if cycle_index < len(self.cycle_delays):
                    cycle_delay = self.cycle_delays[cycle_index]
                    cycle_delay_seconds = (cycle_delay['hours'] * 3600 + 
                                         cycle_delay['minutes'] * 60 + 
                                         cycle_delay['seconds'])
                    
                    if cycle_delay_seconds > 0:
                        self.next_click_label.config(text=f"⏳ انتظار الدورة {self.current_cycle + 1}")
                        time.sleep(cycle_delay_seconds)

        self.stop_clicker()

    def run(self):
        """تشغيل الواجهة"""
        self.window.mainloop()


if __name__ == "__main__":
    AutoClickerGUI().run()
