"""Tkinter UI for the WMM declination calculator."""

from __future__ import annotations

import calendar as cal
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from wmm_calculator.calculation import calculate_declination, utm2lonlat

MIN_DATE = date(2019, 12, 31)
MAX_DATE = date(2029, 12, 31)
MONTH_NAMES = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


class DeclinationCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WMM Declination Calculator")
        self.resizable(False, False)
        self.fig = None
        self.canvas = None
        self._build_ui()

    def _build_ui(self):
        default_easting = 675461
        default_northing = 5405048
        default_zone = 18
        default_hemisphere = False
        default_lon, default_lat = utm2lonlat(
            default_easting,
            default_northing,
            utm_zone=default_zone,
            northern_hemisphere=default_hemisphere,
        )
        default_lon = round(default_lon, 4)
        default_lat = round(default_lat, 4)

        self.coordinate_mode_var = tk.StringVar(value="utm")
        self.coordinate_mode_label = tk.Label(
            self, width=15, text="Coordinates: ", font=("Calibri", 10, "bold"),
        )
        self.coordinate_mode_label.grid(sticky="W", row=0, column=0, pady=3, padx=3)
        coordinate_mode_frame = tk.Frame(self)
        coordinate_mode_frame.grid(sticky="W", row=0, column=1, pady=3, padx=3)
        self.utm_mode_radio = tk.Radiobutton(
            coordinate_mode_frame,
            text="UTM",
            variable=self.coordinate_mode_var,
            value="utm",
            command=self._toggle_coordinate_mode,
            font=("Calibri", 10),
        )
        self.latlon_mode_radio = tk.Radiobutton(
            coordinate_mode_frame,
            text="Lat/Lon",
            variable=self.coordinate_mode_var,
            value="latlon",
            command=self._toggle_coordinate_mode,
            font=("Calibri", 10),
        )
        self.utm_mode_radio.grid(row=0, column=0, padx=(0, 8))
        self.latlon_mode_radio.grid(row=0, column=1)

        east = tk.DoubleVar(value=default_easting)
        north = tk.DoubleVar(value=default_northing)
        z = tk.DoubleVar(value=default_zone)
        self.easting_label = tk.Label(
            self, width=15, text="Easting: ", font=("Calibri", 10, "bold"),
        )
        self.easting_label.grid(sticky="W", row=1, column=0, pady=3, padx=3)
        self.easting_entry = tk.Entry(self, width=15, textvariable=east)
        self.easting_entry.grid(sticky="W", row=1, column=1, pady=3, padx=3)
        self.northing_label = tk.Label(
            self, width=15, text="Northing: ", font=("Calibri", 10, "bold"),
        )
        self.northing_label.grid(sticky="W", row=2, column=0, pady=3, padx=3)
        self.northing_entry = tk.Entry(self, width=15, textvariable=north)
        self.northing_entry.grid(sticky="W", row=2, column=1, pady=3, padx=3)
        self.zone_label = tk.Label(
            self, width=15, text="UTM Zone: ", font=("Calibri", 10, "bold"),
        )
        self.zone_label.grid(sticky="W", row=3, column=0, pady=3, padx=3)
        self.zone_entry = tk.Entry(self, width=15, textvariable=z)
        self.zone_entry.grid(sticky="W", row=3, column=1, pady=3, padx=3)
        self.bool_var2 = tk.BooleanVar(value=default_hemisphere)

        self.hemisphere_label = tk.Label(
            self, width=15, text="Hemisphere: ", font=("Calibri", 10, "bold"),
        )
        self.hemisphere_label.grid(sticky="W", row=4, column=0, pady=3, padx=3)
        self.radiobutton_north = tk.Radiobutton(
            self, text="North", variable=self.bool_var2, value=True, font=("Calibri", 10),
        )
        self.radiobutton_south = tk.Radiobutton(
            self, text="South", variable=self.bool_var2, value=False, font=("Calibri", 10),
        )
        self.radiobutton_north.grid(row=5, column=0, pady=1, padx=1)
        self.radiobutton_south.grid(row=6, column=0, pady=1, padx=1)

        lat = tk.DoubleVar(value=default_lat)
        lon = tk.DoubleVar(value=default_lon)
        self.latitude_label = tk.Label(
            self, width=15, text="Latitude: ", font=("Calibri", 10, "bold"),
        )
        self.latitude_label.grid(sticky="W", row=1, column=0, pady=3, padx=3)
        self.latitude_entry = tk.Entry(self, width=15, textvariable=lat)
        self.latitude_entry.grid(sticky="W", row=1, column=1, pady=3, padx=3)
        self.longitude_label = tk.Label(
            self, width=15, text="Longitude: ", font=("Calibri", 10, "bold"),
        )
        self.longitude_label.grid(sticky="W", row=2, column=0, pady=3, padx=3)
        self.longitude_entry = tk.Entry(self, width=15, textvariable=lon)
        self.longitude_entry.grid(sticky="W", row=2, column=1, pady=3, padx=3)
        self._toggle_coordinate_mode()

        today = date.today()
        if today < MIN_DATE:
            default_date = MIN_DATE
        elif today > MAX_DATE:
            default_date = MAX_DATE
        else:
            default_date = today

        self.date_label = tk.Label(
            self, width=15, text="Date: ", font=("Calibri", 10, "bold"),
        )
        self.date_label.grid(sticky="W", row=7, column=0, pady=3, padx=3)

        date_frame = tk.Frame(self)
        date_frame.grid(sticky="W", row=7, column=1, pady=3, padx=3)

        self.year_var = tk.StringVar(value=str(default_date.year))
        self.month_var = tk.StringVar(value=MONTH_NAMES[default_date.month - 1])
        self.day_var = tk.StringVar(value=str(default_date.day))

        self.year_combo = ttk.Combobox(
            date_frame,
            textvariable=self.year_var,
            values=[str(y) for y in range(MIN_DATE.year, MAX_DATE.year + 1)],
            width=5,
            state="readonly",
            font=("Calibri", 10),
        )
        self.year_combo.grid(row=0, column=0, padx=(0, 4))
        self.year_combo.bind("<<ComboboxSelected>>", self._on_date_part_changed)

        self.month_combo = ttk.Combobox(
            date_frame,
            textvariable=self.month_var,
            width=4,
            state="readonly",
            font=("Calibri", 10),
        )
        self.month_combo.grid(row=0, column=1, padx=(0, 4))
        self.month_combo.bind("<<ComboboxSelected>>", self._on_date_part_changed)

        self.day_combo = ttk.Combobox(
            date_frame,
            textvariable=self.day_var,
            width=3,
            state="readonly",
            font=("Calibri", 10),
        )
        self.day_combo.grid(row=0, column=2)

        self._refresh_month_day_options(preserve_day=default_date.day)

        self.date_hint = tk.Label(
            self,
            text="WMM models: 2019-12-31 to 2029-12-31",
            font=("Calibri", 8),
            fg="gray",
        )
        self.date_hint.grid(sticky="W", row=8, column=0, columnspan=2, padx=3)

        button_frame = tk.Frame(self)
        button_frame.grid(sticky="E", row=9, column=0, columnspan=2, pady=3, padx=3)
        self.calculate_button = ttk.Button(
            button_frame, text="Calculate", width=10, command=self.calculate_pressed,
        )
        self.calculate_button.grid(row=0, column=0)

        self.declination_frame = tk.Frame(self, bg="whitesmoke", width=300, height=400)
        self.declination_frame.grid(
            sticky="W", row=0, column=2, rowspan=10, columnspan=1, pady=0.5, padx=0.5,
        )

    def _toggle_coordinate_mode(self):
        use_utm = self.coordinate_mode_var.get() == "utm"
        utm_widgets = (
            self.easting_label,
            self.easting_entry,
            self.northing_label,
            self.northing_entry,
            self.zone_label,
            self.zone_entry,
            self.hemisphere_label,
            self.radiobutton_north,
            self.radiobutton_south,
        )
        latlon_widgets = (
            self.latitude_label,
            self.latitude_entry,
            self.longitude_label,
            self.longitude_entry,
        )
        for widget in utm_widgets:
            if use_utm:
                widget.grid()
            else:
                widget.grid_remove()
        for widget in latlon_widgets:
            if use_utm:
                widget.grid_remove()
            else:
                widget.grid()

    def _parse_coordinates(self):
        if self.coordinate_mode_var.get() == "utm":
            try:
                easting = float(self.easting_entry.get())
                northing = float(self.northing_entry.get())
                utm_zone = int(self.zone_entry.get())
                hemisphere = self.bool_var2.get()
            except ValueError as exc:
                raise ValueError(
                    "Easting, Northing, and UTM zone must be valid numbers."
                ) from exc
            return {
                "Easting": easting,
                "Northing": northing,
                "utm_zone": utm_zone,
                "northern_hemisphere": hemisphere,
            }

        try:
            latitude = float(self.latitude_entry.get())
            longitude = float(self.longitude_entry.get())
        except ValueError as exc:
            raise ValueError(
                "Latitude and longitude must be valid numbers."
            ) from exc
        return {"lat": latitude, "lon": longitude}

    def _selected_year(self) -> int:
        return int(self.year_var.get())

    def _selected_month(self) -> int:
        return MONTH_NAMES.index(self.month_var.get()) + 1

    def _valid_months(self, year: int) -> list[int]:
        months = []
        for month in range(1, 13):
            last_day = cal.monthrange(year, month)[1]
            if date(year, month, 1) <= MAX_DATE and date(year, month, last_day) >= MIN_DATE:
                months.append(month)
        return months

    def _valid_days(self, year: int, month: int) -> list[int]:
        last_day = cal.monthrange(year, month)[1]
        return [
            day for day in range(1, last_day + 1)
            if MIN_DATE <= date(year, month, day) <= MAX_DATE
        ]

    def _refresh_month_day_options(self, preserve_day: int | None = None):
        year = self._selected_year()
        months = self._valid_months(year)
        month_labels = [MONTH_NAMES[m - 1] for m in months]
        self.month_combo.configure(values=month_labels)

        if self.month_var.get() not in month_labels:
            self.month_var.set(month_labels[0])

        month = self._selected_month()
        days = self._valid_days(year, month)
        day_labels = [str(d) for d in days]
        self.day_combo.configure(values=day_labels)

        if preserve_day is not None and str(preserve_day) in day_labels:
            self.day_var.set(str(preserve_day))
        elif self.day_var.get() not in day_labels:
            self.day_var.set(day_labels[0])

    def _on_date_part_changed(self, _event=None):
        try:
            preserve_day = int(self.day_var.get())
        except ValueError:
            preserve_day = None
        self._refresh_month_day_options(preserve_day=preserve_day)

    def _parse_date(self):
        try:
            selected = date(
                self._selected_year(),
                self._selected_month(),
                int(self.day_var.get()),
            )
        except (ValueError, IndexError) as exc:
            raise ValueError("Select a valid year, month, and day.") from exc
        if selected < MIN_DATE or selected > MAX_DATE:
            raise ValueError(
                "Date must be between 2019-12-31 and 2029-12-31."
            )
        return datetime.combine(selected, datetime.min.time())

    def _show_figure(self, fig):
        for widget in self.declination_frame.winfo_children():
            widget.destroy()
        old_fig = self.fig
        if old_fig is not None and old_fig is not fig:
            import matplotlib.pyplot as plt
            plt.close(old_fig)
        self.fig = fig
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.declination_frame)
        toolbar = NavigationToolbar2Tk(self.canvas, self.declination_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=0, column=0, columnspan=1)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, pady=1, padx=1)

    def calculate_pressed(self):
        try:
            location_kwargs = self._parse_coordinates()
            timestamp = self._parse_date()
        except ValueError as exc:
            messagebox.showerror("WMM Declination", str(exc))
            return

        try:
            lon, lat, declination, error, fig = calculate_declination(
                timestamp,
                **location_kwargs,
            )
        except Exception as exc:
            messagebox.showerror(
                "WMM Declination", f"Could not calculate declination:\n{exc}",
            )
            return

        self.declination = declination
        self.error = error
        self.lat = lat
        self.lon = lon
        self._show_figure(fig)


def run():
    app = DeclinationCalculatorApp()
    app.mainloop()
