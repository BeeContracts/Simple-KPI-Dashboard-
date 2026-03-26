#!/usr/bin/env python3
"""Business KPI Dashboard desktop app."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_BG = '#0f172a'
PANEL_BG = '#111827'
TEXT = '#e5e7eb'
MUTED = '#94a3b8'
ACCENT = '#38bdf8'
BUTTON = '#1f2937'
GOOD = '#14532d'
CARD_1 = '#1d4ed8'
CARD_2 = '#0f766e'
CARD_3 = '#7c3aed'
CARD_4 = '#b45309'


class DashboardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Business KPI Dashboard')
        self.root.geometry('1240x820')
        self.root.configure(bg=APP_BG)
        self.rows: list[dict[str, str]] = []
        self.headers: list[str] = []
        self.current_file: Path | None = None
        self._set_icon_if_available()
        self._build_ui()

    def _set_icon_if_available(self) -> None:
        icon = Path(__file__).with_name('app_icon.png')
        if icon.exists():
            try:
                photo = tk.PhotoImage(file=str(icon))
                self.root.iconphoto(True, photo)
                self._icon_ref = photo
            except Exception:
                pass

    def _button(self, parent, text, command, bold=False):
        return tk.Button(parent, text=text, command=command, bg=BUTTON, fg=TEXT, activebackground=ACCENT, activeforeground='black', relief='flat', padx=10, pady=6, font=('Segoe UI', 10, 'bold' if bold else 'normal'))

    def _card(self, parent, title, var, bg):
        frame = tk.Frame(parent, bg=bg, padx=12, pady=10)
        tk.Label(frame, text=title, bg=bg, fg=TEXT, font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        tk.Label(frame, textvariable=var, bg=bg, fg='white', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(4, 0))
        return frame

    def _build_ui(self):
        tk.Label(self.root, text='Business KPI Dashboard', font=('Segoe UI', 18, 'bold'), bg=APP_BG, fg=TEXT).pack(pady=(12, 4))
        tk.Label(self.root, text='Load a CSV, choose key columns, and generate recruiter-friendly business metrics.', font=('Segoe UI', 10), bg=APP_BG, fg=MUTED).pack(pady=(0, 10))

        cards = tk.Frame(self.root, bg=APP_BG)
        cards.pack(fill='x', padx=12, pady=(0, 10))
        self.total_records_var = tk.StringVar(value='0')
        self.total_value_var = tk.StringVar(value='$0')
        self.avg_value_var = tk.StringVar(value='$0')
        self.top_category_var = tk.StringVar(value='-')
        self._card(cards, 'Total Records', self.total_records_var, CARD_1).pack(side='left', fill='x', expand=True, padx=(0, 6))
        self._card(cards, 'Total Value', self.total_value_var, CARD_2).pack(side='left', fill='x', expand=True, padx=6)
        self._card(cards, 'Average Value', self.avg_value_var, CARD_3).pack(side='left', fill='x', expand=True, padx=6)
        self._card(cards, 'Top Category/Stage', self.top_category_var, CARD_4).pack(side='left', fill='x', expand=True, padx=(6, 0))

        controls = tk.Frame(self.root, bg=APP_BG)
        controls.pack(fill='x', padx=12, pady=(0, 10))
        self._button(controls, 'Load CSV', self.load_csv, bold=True).pack(side='left')
        self._button(controls, 'Analyze', self.run_analysis).pack(side='left', padx=8)
        self._button(controls, 'Export JSON', self.export_json).pack(side='left')
        self._button(controls, 'Export CSV Summary', self.export_csv_summary).pack(side='left', padx=8)

        selectors = tk.Frame(self.root, bg=PANEL_BG, padx=12, pady=12)
        selectors.pack(fill='x', padx=12, pady=(0, 10))

        self.value_var = tk.StringVar(value='')
        self.category_var = tk.StringVar(value='')
        self.date_var = tk.StringVar(value='')

        for idx, (label, var) in enumerate([
            ('Value / Revenue Column', self.value_var),
            ('Category / Stage Column', self.category_var),
            ('Date Column (optional)', self.date_var),
        ]):
            tk.Label(selectors, text=label, bg=PANEL_BG, fg=TEXT).grid(row=0, column=idx*2, sticky='w', padx=(0, 6), pady=4)
            combo = ttk.Combobox(selectors, textvariable=var, values=[], state='readonly', width=24)
            combo.grid(row=0, column=idx*2+1, sticky='ew', padx=(0, 14), pady=4)
            if var is self.value_var:
                self.value_combo = combo
            elif var is self.category_var:
                self.category_combo = combo
            else:
                self.date_combo = combo
        selectors.grid_columnconfigure(1, weight=1)
        selectors.grid_columnconfigure(3, weight=1)
        selectors.grid_columnconfigure(5, weight=1)

        lower = tk.Frame(self.root, bg=APP_BG)
        lower.pack(fill='both', expand=True, padx=12, pady=(0, 10))

        table_panel = tk.Frame(lower, bg=APP_BG)
        table_panel.pack(side='left', fill='both', expand=True, padx=(0, 8))
        report_panel = tk.Frame(lower, bg=APP_BG)
        report_panel.pack(side='left', fill='both', expand=True)

        tk.Label(table_panel, text='Loaded Data Preview', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.tree = ttk.Treeview(table_panel, show='headings', height=22)
        self.tree.pack(fill='both', expand=True, pady=(6, 0))

        tk.Label(report_panel, text='Summary Report', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.report = tk.Text(report_panel, bg=PANEL_BG, fg=TEXT, insertbackground=TEXT, relief='flat', wrap='word')
        self.report.pack(fill='both', expand=True, pady=(6, 0))

        style = ttk.Style()
        try:
            style.theme_use('default')
        except Exception:
            pass
        style.configure('Treeview', background=PANEL_BG, fieldbackground=PANEL_BG, foreground=TEXT, rowheight=26)
        style.configure('Treeview.Heading', background=BUTTON, foreground=TEXT)
        style.map('Treeview', background=[('selected', ACCENT)], foreground=[('selected', 'black')])

        self.status_var = tk.StringVar(value='Load a CSV to begin')
        tk.Label(self.root, textvariable=self.status_var, anchor='w', bg=APP_BG, fg=MUTED).pack(fill='x', padx=12, pady=(0, 10))

    def set_status(self, text: str):
        self.status_var.set(text)

    def detect_value_columns(self):
        value_candidates = []
        for header in self.headers:
            nums = [self.to_number(row.get(header, '')) for row in self.rows]
            valid = [n for n in nums if n is not None]
            if valid and len(valid) >= max(2, len(self.rows) // 3):
                value_candidates.append(header)
        return value_candidates or self.headers

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.rows = list(reader)
                self.headers = reader.fieldnames or []
            self.current_file = Path(path)
            self.populate_selectors()
            self.populate_table_preview()
            self.report.delete('1.0', tk.END)
            self.set_status(f'Loaded {len(self.rows)} row(s) from {path}')
        except Exception as e:
            messagebox.showerror('CSV Error', f'Failed to load CSV: {e}')

    def populate_selectors(self):
        headers_with_none = [''] + self.headers
        self.value_combo['values'] = self.detect_value_columns()
        self.category_combo['values'] = headers_with_none
        self.date_combo['values'] = headers_with_none
        if self.value_combo['values']:
            self.value_var.set(self.value_combo['values'][0])
        if self.headers:
            self.category_var.set(self.headers[0])

    def populate_table_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = self.headers
        for h in self.headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=130, anchor='w')
        for row in self.rows[:100]:
            self.tree.insert('', tk.END, values=[row.get(h, '') for h in self.headers])

    def to_number(self, value):
        if value is None:
            return None
        cleaned = ''.join(ch for ch in str(value) if ch.isdigit() or ch in '.-')
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def compute_summary(self):
        if not self.rows:
            return None
        value_col = self.value_var.get().strip()
        category_col = self.category_var.get().strip()
        date_col = self.date_var.get().strip()

        values = [self.to_number(row.get(value_col, '')) for row in self.rows] if value_col else []
        numeric_values = [v for v in values if v is not None]
        categories = [row.get(category_col, '').strip() for row in self.rows if category_col and row.get(category_col, '').strip()]
        category_counts = Counter(categories)
        top_category = category_counts.most_common(1)[0][0] if category_counts else '-'

        summary = {
            'file': str(self.current_file) if self.current_file else '',
            'total_records': len(self.rows),
            'value_column': value_col,
            'category_column': category_col,
            'date_column': date_col,
            'total_value': round(sum(numeric_values), 2) if numeric_values else 0,
            'average_value': round(mean(numeric_values), 2) if numeric_values else 0,
            'top_category': top_category,
            'category_breakdown': dict(category_counts.most_common()),
        }
        return summary

    def render_summary(self, summary):
        self.total_records_var.set(str(summary['total_records']))
        self.total_value_var.set(f"${summary['total_value']:,.2f}")
        self.avg_value_var.set(f"${summary['average_value']:,.2f}")
        self.top_category_var.set(summary['top_category'])

        lines = []
        lines.append('=== Business KPI Summary ===')
        if summary['file']:
            lines.append(f"Source File: {summary['file']}")
        lines.append(f"Total Records: {summary['total_records']}")
        lines.append(f"Value Column: {summary['value_column'] or 'Not selected'}")
        lines.append(f"Category Column: {summary['category_column'] or 'Not selected'}")
        lines.append(f"Date Column: {summary['date_column'] or 'Not selected'}")
        lines.append(f"Total Value: ${summary['total_value']:,.2f}")
        lines.append(f"Average Value: ${summary['average_value']:,.2f}")
        lines.append(f"Top Category/Stage: {summary['top_category']}")
        lines.append('')
        lines.append('Category Breakdown:')
        if summary['category_breakdown']:
            for key, value in summary['category_breakdown'].items():
                lines.append(f'- {key}: {value}')
        else:
            lines.append('- No category column selected or no category values found')
        self.report.delete('1.0', tk.END)
        self.report.insert(tk.END, '\n'.join(lines))

    def run_analysis(self):
        if not self.rows:
            messagebox.showinfo('No Data', 'Load a CSV file first.')
            return
        summary = self.compute_summary()
        if not summary:
            return
        self.last_summary = summary
        self.render_summary(summary)
        self.set_status('Analysis complete')

    def export_json(self):
        if not getattr(self, 'last_summary', None):
            messagebox.showinfo('No Summary', 'Run Analyze first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')], initialfile='kpi_summary.json')
        if not path:
            return
        Path(path).write_text(json.dumps(self.last_summary, indent=2), encoding='utf-8')
        self.set_status(f'Exported JSON summary: {path}')

    def export_csv_summary(self):
        if not getattr(self, 'last_summary', None):
            messagebox.showinfo('No Summary', 'Run Analyze first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], initialfile='kpi_summary.csv')
        if not path:
            return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['total_records', self.last_summary['total_records']])
            writer.writerow(['value_column', self.last_summary['value_column']])
            writer.writerow(['category_column', self.last_summary['category_column']])
            writer.writerow(['date_column', self.last_summary['date_column']])
            writer.writerow(['total_value', self.last_summary['total_value']])
            writer.writerow(['average_value', self.last_summary['average_value']])
            writer.writerow(['top_category', self.last_summary['top_category']])
            for key, value in self.last_summary['category_breakdown'].items():
                writer.writerow([f'category::{key}', value])
        self.set_status(f'Exported CSV summary: {path}')


def main():
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
