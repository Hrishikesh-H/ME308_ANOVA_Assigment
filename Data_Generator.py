import numpy as np
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ANOVADataGenerator:
    def __init__(self, d1, d2, m1, m2, y1, y2, replications=25, tol_mean=0.05, tol_std=0.05, num_decimals=2):
        """
        Initialize the generator with birthdate parameters and experimental settings.
        
        Parameters:
            d1, d2 : int
                The first and second digits of the day.
            m1, m2 : int
                The first and second digits of the month.
            y1, y2 : int
                The two digits of the year (provided as the last two digits).
            replications : int
                The number of observations per treatment.
            tol_mean : float
                Allowed tolerance for deviation of the sample mean from the target mean.
            tol_std : float
                Allowed tolerance for deviation of the sample standard deviation from the target std.
            num_decimals : int
                The number of decimal places to round the generated observations.
        """
        self.d1 = d1
        self.d2 = d2
        self.m1 = m1
        self.m2 = m2
        self.y1 = y1
        self.y2 = y2
        self.replications = replications
        self.tol_mean = tol_mean
        self.tol_std = tol_std
        self.num_decimals = num_decimals
        
        # Determine number of treatments = max(4, d1 + d2)
        self.num_treatments = max(4, self.d1 + self.d2)
        # Calculate target standard deviation: (m2 * d2) / y2
        self.target_std = (self.m2 * self.d2) / self.y2

    def generate_observations(self, target_mean, target_std):
        """
        Generate a set of observations from a normal distribution with given target mean and std.
        Adjust if sample stats deviate beyond tolerances.
        """
        observations = np.random.normal(loc=target_mean, scale=target_std, size=self.replications)
        sample_mean = np.mean(observations)
        sample_std = np.std(observations, ddof=1)
        if (abs(sample_mean - target_mean) > self.tol_mean) or (abs(sample_std - target_std) > self.tol_std):
            observations = ((observations - sample_mean) / sample_std) * target_std + target_mean
        observations = np.round(observations, self.num_decimals)
        return observations

    def generate_data(self):
        """
        Generate a DataFrame where each column corresponds to a treatment.
        For treatment i, target mean = (m2 * d2) + (i * y2).
        """
        data = {}
        for i in range(1, self.num_treatments + 1):
            target_mean = (self.m2 * self.d2) + (i * self.y2)
            observations = self.generate_observations(target_mean, self.target_std)
            data[f"Treatment_{i}"] = observations
        return pd.DataFrame(data)

class DataGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ANOVA Data Generator")
        self.geometry("450x600")
        self.create_widgets()
    
    def create_widgets(self):
        # --- DOB Section using Drop-downs ---
        dob_frame = ttk.LabelFrame(self, text="Date of Birth (DOB)")
        dob_frame.pack(padx=10, pady=10, fill="x")
        
        # Day drop-down (two-digit options "01" to "31")
        ttk.Label(dob_frame, text="Day:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.day_var = tk.StringVar(value="10")
        day_options = [f"{i:02d}" for i in range(1, 32)]
        day_menu = ttk.OptionMenu(dob_frame, self.day_var, self.day_var.get(), *day_options)
        day_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Month drop-down (two-digit "01" to "12")
        ttk.Label(dob_frame, text="Month:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.month_var = tk.StringVar(value="03")
        month_options = [f"{i:02d}" for i in range(1, 13)]
        month_menu = ttk.OptionMenu(dob_frame, self.month_var, self.month_var.get(), *month_options)
        month_menu.grid(row=1, column=1, padx=5, pady=5)
        
        # Year drop-down (last two digits, e.g., "24")
        ttk.Label(dob_frame, text="Year:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.year_var = tk.StringVar(value="24")
        year_options = [f"{i:02d}" for i in range(0, 100)]
        year_menu = ttk.OptionMenu(dob_frame, self.year_var, self.year_var.get(), *year_options)
        year_menu.grid(row=2, column=1, padx=5, pady=5)
        
        # --- Parameter Section with Slider and Type Option ---
        param_frame = ttk.LabelFrame(self, text="Other Parameters")
        param_frame.pack(padx=10, pady=10, fill="x")
        
        # Function to create a parameter row with a slider and an entry widget.
        def create_param_row(frame, label_text, var, slider_from, slider_to, resolution, row):
            ttk.Label(frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            scale = tk.Scale(frame, variable=var, from_=slider_from, to=slider_to,
                             orient=tk.HORIZONTAL, resolution=resolution, length=200,
                             command=lambda val, v=var, e=entry: e.delete(0, tk.END) or e.insert(0, f"{float(val):.2f}" if isinstance(var.get(), float) else f"{int(float(val))}"))
            scale.grid(row=row, column=1, padx=5, pady=5)
            entry = ttk.Entry(frame, textvariable=var, width=10)
            entry.grid(row=row, column=2, padx=5, pady=5)
            return scale, entry
        
        # Replications: integer, default 25, range 1 to 100
        self.replications_var = tk.IntVar(value=25)
        ttk.Label(param_frame, text="Replications:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.replications_scale = tk.Scale(param_frame, variable=self.replications_var, from_=1, to=100,
                                           orient=tk.HORIZONTAL, length=200,
                                           command=lambda val: self.replications_entry.delete(0, tk.END) or self.replications_entry.insert(0, str(int(float(val)))))
        self.replications_scale.grid(row=0, column=1, padx=5, pady=5)
        self.replications_entry = ttk.Entry(param_frame, textvariable=self.replications_var, width=10)
        self.replications_entry.grid(row=0, column=2, padx=5, pady=5)
        
        # Tolerance for mean difference: float, default 0.05, range 0 to 1, resolution 0.01
        self.tol_mean_var = tk.DoubleVar(value=0.05)
        ttk.Label(param_frame, text="Tol. Mean Diff:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.tol_mean_scale = tk.Scale(param_frame, variable=self.tol_mean_var, from_=0, to=1,
                                       orient=tk.HORIZONTAL, resolution=0.01, length=200,
                                       command=lambda val: self.tol_mean_entry.delete(0, tk.END) or self.tol_mean_entry.insert(0, f"{float(val):.2f}"))
        self.tol_mean_scale.grid(row=1, column=1, padx=5, pady=5)
        self.tol_mean_entry = ttk.Entry(param_frame, textvariable=self.tol_mean_var, width=10)
        self.tol_mean_entry.grid(row=1, column=2, padx=5, pady=5)
        
        # Tolerance for std deviation: float, default 0.05, range 0 to 1, resolution 0.01
        self.tol_std_var = tk.DoubleVar(value=0.05)
        ttk.Label(param_frame, text="Tol. Std Diff:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.tol_std_scale = tk.Scale(param_frame, variable=self.tol_std_var, from_=0, to=1,
                                      orient=tk.HORIZONTAL, resolution=0.01, length=200,
                                      command=lambda val: self.tol_std_entry.delete(0, tk.END) or self.tol_std_entry.insert(0, f"{float(val):.2f}"))
        self.tol_std_scale.grid(row=2, column=1, padx=5, pady=5)
        self.tol_std_entry = ttk.Entry(param_frame, textvariable=self.tol_std_var, width=10)
        self.tol_std_entry.grid(row=2, column=2, padx=5, pady=5)
        
        # Number of decimals: integer, default 2, range 0 to 5.
        self.decimals_var = tk.IntVar(value=2)
        ttk.Label(param_frame, text="Decimals:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.decimals_scale = tk.Scale(param_frame, variable=self.decimals_var, from_=0, to=5,
                                       orient=tk.HORIZONTAL, length=200,
                                       command=lambda val: self.decimals_entry.delete(0, tk.END) or self.decimals_entry.insert(0, str(int(float(val)))))
        self.decimals_scale.grid(row=3, column=1, padx=5, pady=5)
        self.decimals_entry = ttk.Entry(param_frame, textvariable=self.decimals_var, width=10)
        self.decimals_entry.grid(row=3, column=2, padx=5, pady=5)
        
        # File prefix entry (text only)
        prefix_frame = ttk.LabelFrame(self, text="CSV File Settings")
        prefix_frame.pack(padx=10, pady=10, fill="x")
        ttk.Label(prefix_frame, text="File Prefix:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.prefix_var = tk.StringVar(value="220003037")
        self.prefix_entry = ttk.Entry(prefix_frame, textvariable=self.prefix_var)
        self.prefix_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Generate Data button
        self.generate_button = ttk.Button(self, text="Generate Data", command=self.generate_data)
        self.generate_button.pack(pady=20)
    
    def generate_data(self):
        try:
            # Extract DOB values from the drop-downs.
            day_str = self.day_var.get()  # already two-digit
            month_str = self.month_var.get()  # two-digit
            year_str = self.year_var.get()  # two-digit
            
            # Convert the strings into individual digits.
            d1, d2 = int(day_str[0]), int(day_str[1])
            m1, m2 = int(month_str[0]), int(month_str[1])
            y1, y2 = int(year_str[0]), int(year_str[1])
            
            # Retrieve other parameters from the corresponding variables.
            replications = self.replications_var.get()
            tol_mean = self.tol_mean_var.get()
            tol_std = self.tol_std_var.get()
            num_decimals = self.decimals_var.get()
            file_prefix = self.prefix_var.get().strip() or "220003037"
            
            # Create the data generator instance with the provided parameters.
            generator = ANOVADataGenerator(d1, d2, m1, m2, y1, y2, replications, tol_mean, tol_std, num_decimals)
            df = generator.generate_data()
            
            # Save the data to a CSV file with a timestamp.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{file_prefix}_anova_data_{timestamp}.csv"
            df.to_csv(filename, index=False)
            
            # Show success message with a summary of the data.
            messagebox.showinfo("Success", f"Data generated and saved to {filename}.\n\nFirst 5 rows:\n{df.head().to_string()}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    np.random.seed(42)
    app = DataGeneratorGUI()
    app.mainloop()
