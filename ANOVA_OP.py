import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import scipy.stats as stats
import time
from datetime import datetime
import threading

class AnovaApp:
    anova_steps = [
        "Step 1: C = (ΣX)² / n  (Correction Factor)",
        "Step 2: SST = Σ(X²) - C  (Total SS)",
        "Step 3: SSTR = Σ((ΣXᵢ)² / nᵢ) - C  (Treatment SS)",
        "Step 4: SSE = SST - SSTR  (Error SS)",
        "Step 5: F = [SSTR/(p−1)] / [SSE/(n−p)]"
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("ANOVA Analysis")
        self.center_window(1200, 800)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("MainFrame.TFrame", background="#f0f0f0")
        style.configure("TitleLabel.TLabel", font=("Helvetica", 18, "bold"), background="#f0f0f0")
        style.configure("SubTitleLabel.TLabel", font=("Helvetica", 12, "bold"), background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 11))
        style.configure("TButton", background="#007acc", foreground="white", font=("Helvetica", 11, "bold"))
        style.configure("TEntry", font=("Helvetica", 11))
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), background="#007acc", foreground="white")
        style.configure("TProgressbar", troughcolor="#e6e6e6", background="#007acc")

        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(self.main_frame, text="One-Way ANOVA", style="TitleLabel.TLabel")
        self.title_label.pack(pady=10)

        self.param_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.param_frame.pack(pady=5)

        self.header_label = ttk.Label(self.param_frame, text="Does your CSV have a header row?", style="TLabel")
        self.header_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.header_var = tk.StringVar(value="yes")
        self.header_yes = ttk.Radiobutton(self.param_frame, text="Yes", variable=self.header_var, value="yes")
        self.header_no = ttk.Radiobutton(self.param_frame, text="No", variable=self.header_var, value="no")
        self.header_yes.grid(row=0, column=1, padx=5)
        self.header_no.grid(row=0, column=2, padx=5)

        self.index_label = ttk.Label(self.param_frame, text="Does your CSV have an index column?", style="TLabel")
        self.index_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.index_var = tk.StringVar(value="no")
        self.index_yes = ttk.Radiobutton(self.param_frame, text="Yes", variable=self.index_var, value="yes")
        self.index_no = ttk.Radiobutton(self.param_frame, text="No", variable=self.index_var, value="no")
        self.index_yes.grid(row=1, column=1, padx=5)
        self.index_no.grid(row=1, column=2, padx=5)

        self.alpha_label = ttk.Label(self.param_frame, text="Significance Level (α):", style="TLabel")
        self.alpha_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.alpha_entry = ttk.Entry(self.param_frame, width=10, style="TEntry")
        self.alpha_entry.insert(0, "0.05")
        self.alpha_entry.grid(row=2, column=1, padx=5)

        self.load_button = ttk.Button(self.param_frame, text="Load CSV", command=self.load_csv, style="TButton")
        self.load_button.grid(row=3, column=0, padx=5, pady=10)

        self.anova_button = ttk.Button(self.param_frame, text="Perform ANOVA", command=self.run_anova, style="TButton")
        self.anova_button.grid(row=3, column=1, padx=5, pady=10)

        self.csv_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.csv_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.progress = ttk.Progressbar(self.main_frame, orient="horizontal", length=600, mode="indeterminate", style="TProgressbar")
        self.progress.pack(pady=5)

        self.step_label = ttk.Label(self.main_frame, text="", style="TLabel", wraplength=1100, justify="left")
        self.step_label.pack(pady=5)

        self.output_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.save_button = ttk.Button(self.main_frame, text="Save to Excel", command=self.save_to_excel, state=tk.DISABLED, style="TButton")
        self.save_button.pack(pady=10)

        self.df = None
        self.group_info_df = None
        self.anova_result = None
        self.current_step = 0

    def center_window(self, width, height):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            has_header = self.header_var.get()
            has_index = self.index_var.get()

            if has_index == "yes":
                if has_header == "yes":
                    self.df = pd.read_csv(file_path, header=0, index_col=0)
                else:
                    self.df = pd.read_csv(file_path, header=None, index_col=0)
                    col_count = self.df.shape[1]
                    self.df.reset_index(inplace=True)
                    self.df.columns = [f"Group{i}" for i in range(col_count+1)]
            else:
                if has_header == "yes":
                    self.df = pd.read_csv(file_path, header=0)
                else:
                    self.df = pd.read_csv(file_path, header=None)
                    col_count = self.df.shape[1]
                    self.df.columns = [f"Group{i}" for i in range(col_count)]
        except Exception as e:
            messagebox.showerror("Error", f"Unable to read CSV:\n{e}")
            return

        for widget in self.csv_frame.winfo_children():
            widget.destroy()

        tree_scroll = ttk.Scrollbar(self.csv_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.csv_tree = ttk.Treeview(self.csv_frame, yscrollcommand=tree_scroll.set, style="Treeview")
        self.csv_tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.csv_tree.yview)

        self.csv_tree["columns"] = list(self.df.columns)
        self.csv_tree["show"] = "headings"
        for col in self.df.columns:
            self.csv_tree.heading(col, text=col)
            self.csv_tree.column(col, width=100, anchor="center")

        for _, row in self.df.iterrows():
            self.csv_tree.insert("", "end", values=list(row))

    def show_steps(self):
        if self.current_step < len(self.anova_steps):
            self.step_label.config(text=self.anova_steps[self.current_step])
            self.current_step += 1
            self.root.after(2000, self.show_steps)

    def run_anova(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No CSV loaded.")
            return

        self.progress.start()
        self.current_step = 0
        self.step_label.config(text="")
        self.show_steps()

        threading.Thread(target=self.perform_anova, daemon=True).start()

    def perform_anova(self):
        try:
            time.sleep(1)
            alpha_str = self.alpha_entry.get().strip()
            try:
                alpha = float(alpha_str)
            except ValueError:
                alpha = 0.05

            numeric_only = self.df.apply(pd.to_numeric, errors='coerce')
            valid_cols = [col for col in numeric_only.columns if not numeric_only[col].dropna().empty]

            if len(valid_cols) < 2:
                raise ValueError("At least two columns must contain numeric data.")

            group_list = []
            group_names = []
            for col in valid_cols:
                vals = numeric_only[col].dropna().values
                if len(vals) > 0:
                    group_list.append(vals)
                    group_names.append(col)

            if len(group_list) < 2:
                raise ValueError("At least two groups are required for ANOVA.")

            group_info_data = {
                "Group": [],
                "Size": [],
                "Sum": [],
                "Mean": []
            }
            for gname, gvals in zip(group_names, group_list):
                group_info_data["Group"].append(gname)
                group_info_data["Size"].append(len(gvals))
                group_info_data["Sum"].append(gvals.sum())
                group_info_data["Mean"].append(gvals.mean())
            self.group_info_df = pd.DataFrame(group_info_data)

            f_stat, p_value = stats.f_oneway(*group_list)

            group_sums = [g.sum() for g in group_list]
            group_sq_sums = [(g**2).sum() for g in group_list]
            group_sizes = [len(g) for g in group_list]

            p = len(group_list)
            n = sum(group_sizes)

            # (1) C = ( (ΣX)² ) / n
            total_sum = sum(group_sums)
            C = (total_sum**2) / n

            # (2) SST = Σ(X²) - C
            total_sq_sum = sum(group_sq_sums)
            SST = total_sq_sum - C

            # (3) SSTR = Σ( (ΣXᵢ)² / nᵢ ) - C
            SSTR = sum((s**2)/sz for s, sz in zip(group_sums, group_sizes)) - C

            # (4) SSE = SST - SSTR
            SSE = SST - SSTR

            # (5) df
            df_treat = p - 1
            df_error = n - p
            df_total = n - 1

            MSTR = SSTR / df_treat
            MSE = SSE / df_error
            F_calculated = MSTR / MSE

            result_data = {
                "Source of Variation": ["Treatments", "Error", "Total"],
                "Degrees of Freedom": [df_treat, df_error, df_total],
                "Sum of Squares": [SSTR, SSE, SST],
                "Mean Square": [MSTR, MSE, ""],
                "F-Statistic": [F_calculated, "", ""],
                "P-value": [p_value, "", ""],
                "Significance (α)": [alpha, "", ""],
                "Reject H0?": [("Yes" if p_value < alpha else "No"), "", ""]
            }

            self.anova_result = pd.DataFrame(result_data)
            self.progress.stop()
            self.display_extracted_info()
            self.display_results()
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Error", f"{str(e)}")

    def display_extracted_info(self):
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        info_label = ttk.Label(self.output_frame, text="Group Info (Extracted):", style="SubTitleLabel.TLabel")
        info_label.pack(pady=5)

        group_table = ttk.Treeview(self.output_frame, columns=list(self.group_info_df.columns), show="headings", style="Treeview")
        for col in self.group_info_df.columns:
            group_table.heading(col, text=col)
            group_table.column(col, width=100, anchor="center")

        group_table.pack(pady=5, fill="x")

        for _, row in self.group_info_df.iterrows():
            group_table.insert("", "end", values=list(row))

    def display_results(self):
        anova_label = ttk.Label(self.output_frame, text="ANOVA Table:", style="SubTitleLabel.TLabel")
        anova_label.pack(pady=5)

        anova_table = ttk.Treeview(self.output_frame, columns=list(self.anova_result.columns), show="headings", style="Treeview")
        for col in self.anova_result.columns:
            anova_table.heading(col, text=col)
            anova_table.column(col, width=110, anchor="center")

        anova_table.pack(pady=5, fill="x")

        for _, row in self.anova_result.iterrows():
            anova_table.insert("", "end", values=list(row))

        self.save_button.config(state=tk.NORMAL)

    def save_to_excel(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"ANOVA_{timestamp}.xlsx"
        )
        if file_path:
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                if self.group_info_df is not None:
                    self.group_info_df.to_excel(writer, index=False, sheet_name="Group Info")
                self.anova_result.to_excel(writer, index=False, sheet_name="ANOVA Results")

                workbook = writer.book
                if self.group_info_df is not None:
                    ws_info = writer.sheets["Group Info"]
                    header_format = workbook.add_format({"bold": True, "align": "center", "border": 1})
                    cell_format = workbook.add_format({"align": "center", "border": 1})
                    for col_num, value in enumerate(self.group_info_df.columns.values):
                        ws_info.write(0, col_num, value, header_format)
                    for row_num, row_data in enumerate(self.group_info_df.values, start=1):
                        for col_num, cell_value in enumerate(row_data):
                            ws_info.write(row_num, col_num, cell_value, cell_format)

                ws_anova = writer.sheets["ANOVA Results"]
                header_format = workbook.add_format({"bold": True, "align": "center", "border": 1})
                cell_format = workbook.add_format({"align": "center", "border": 1})
                for col_num, value in enumerate(self.anova_result.columns.values):
                    ws_anova.write(0, col_num, value, header_format)
                for row_num, row_data in enumerate(self.anova_result.values, start=1):
                    for col_num, cell_value in enumerate(row_data):
                        ws_anova.write(row_num, col_num, cell_value, cell_format)

            messagebox.showinfo("Success", "ANOVA results saved successfully!")

def main():
    root = tk.Tk()
    app = AnovaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
