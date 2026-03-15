#!/usr/bin/env python3
"""GUI-first launcher for exif_editor.py fake command."""

from __future__ import annotations

import sys
import threading
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path

from camera_presets import CAMERA_PRESETS


class _LineWriter:
    """File-like writer that emits complete lines to a callback."""

    def __init__(self, emit):
        self._emit = emit
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._emit(line)
        return len(text)

    def flush(self):
        if self._buffer:
            self._emit(self._buffer)
            self._buffer = ""


def run_exif_editor_args(args: list[str], emit_line=None) -> int:
    """Run exif_editor.main() in-process so one-file packaging works."""
    import exif_editor

    if emit_line is None:
        emit_line = print

    old_argv = sys.argv[:]
    writer = _LineWriter(emit_line)
    try:
        with redirect_stdout(writer), redirect_stderr(writer):
            sys.argv = ["exif_editor.py", *args]
            exif_editor.main()
        writer.flush()
        return 0
    except SystemExit as exc:
        writer.flush()
        code = exc.code
        if isinstance(code, int):
            return code
        return 0 if code in (None, "") else 1
    except Exception as exc:
        writer.flush()
        emit_line(f"Error: {exc}")
        return 1
    finally:
        sys.argv = old_argv


def get_default_batch_output_dir(input_path: str) -> str:
    """Return sibling output folder next to the selected input directory."""
    return str(Path(input_path).resolve().parent / "output")


def ask_input(prompt: str, required: bool = False, default: str | None = None) -> str:
    """Simple prompt helper used by CLI fallback mode."""
    display_prompt = f"{prompt} [{default}]: " if default else f"{prompt}: "
    while True:
        response = input(display_prompt).strip()
        if response:
            return response
        if default:
            return default
        if not required:
            return ""
        print("This field is required.")


def ask_choice(prompt: str, choices: list[str], default: str | None = None) -> str:
    """Choice helper used by CLI fallback mode."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    while True:
        response = input("Enter choice (number or name): ").strip()
        if response.isdigit():
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        elif response in choices:
            return response
        elif not response and default:
            return default
        print("Invalid choice.")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Yes/no helper used by CLI fallback mode."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    if response in ("y", "yes"):
        return True
    if response in ("n", "no"):
        return False
    return default


def run_cli_fallback() -> int:
    """Original terminal flow for headless systems or --cli usage."""
    print("EXIF Editor - CLI mode")
    input_path = ask_input("Path to image or folder", required=True)
    if not Path(input_path).exists():
        print(f"Error: path does not exist: {input_path}")
        return 1

    is_batch = Path(input_path).is_dir()
    preset = ask_choice("Which camera preset?", ["random", *CAMERA_PRESETS.keys()], default="random")
    randomize = ask_yes_no("Randomize ISO/shutter/aperture?", default=True)

    use_random_date = ask_yes_no("Use random timestamp?", default=True)
    fixed_datetime = None
    days_back = 7
    if use_random_date:
        try:
            days_back = int(ask_input("Days back", default="7"))
        except ValueError:
            days_back = 7
    else:
        fixed_datetime = ask_input("Fixed timestamp (YYYY:MM:DD HH:MM:SS)", required=True)

    loc = ask_choice("How to set location?", ["City", "Manual", "None"], default="City")
    city = None
    lat = None
    lon = None
    alt = None
    if loc == "City":
        city = ask_input("City name", required=True)
    elif loc == "Manual":
        try:
            lat = float(ask_input("Latitude", required=True))
            lon = float(ask_input("Longitude", required=True))
            alt_raw = ask_input("Altitude (optional)")
            alt = float(alt_raw) if alt_raw else None
        except ValueError:
            print("Invalid GPS values. GPS will be skipped.")
            lat = lon = alt = None

    title = ask_input("Title (optional)")
    description = ask_input("Description (optional)")
    artist = ask_input("Artist (optional)")
    copyright_str = ask_input("Copyright (optional)")

    output_target = ask_input(
        "Output folder" if is_batch else "Output file",
        default=get_default_batch_output_dir(input_path) if is_batch else None,
    )

    cmd = ["fake", input_path, "-p", preset]
    if randomize:
        cmd.append("--random")
    if fixed_datetime:
        cmd.extend(["--datetime", fixed_datetime])
    else:
        cmd.extend(["--days-back", str(days_back)])
    if city:
        cmd.extend(["--city", city])
    elif lat is not None and lon is not None:
        cmd.extend(["--lat", str(lat), "--lon", str(lon)])
        if alt is not None:
            cmd.extend(["--alt", str(alt)])
    if title:
        cmd.extend(["--title", title])
    if description:
        cmd.extend(["--description", description])
    if artist:
        cmd.extend(["--artist", artist])
    if copyright_str:
        cmd.extend(["--copyright", copyright_str])

    if output_target:
        cmd.extend(["-d", output_target] if is_batch else ["-o", output_target])

    print("\nRunning:\n  python exif_editor.py " + " ".join(cmd))
    return run_exif_editor_args(cmd)


def run_gui() -> int:
    """Launch a Tkinter GUI for the fake metadata workflow."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    class App:
        def __init__(self, root: tk.Tk):
            self.root = root
            self.root.title("EXIF Editor - GUI")
            self.root.geometry("880x760")
            self.running = False

            self.input_path = tk.StringVar()
            self.mode_label = tk.StringVar(value="Mode: Not selected")
            self.preset = tk.StringVar(value="random")
            self.randomize = tk.BooleanVar(value=True)

            self.timestamp_mode = tk.StringVar(value="random")
            self.days_back = tk.StringVar(value="7")
            self.fixed_datetime = tk.StringVar()

            self.location_mode = tk.StringVar(value="city")
            self.city = tk.StringVar()
            self.lat = tk.StringVar()
            self.lon = tk.StringVar()
            self.alt = tk.StringVar()

            self.title_text = tk.StringVar()
            self.description = tk.StringVar()
            self.artist = tk.StringVar()
            self.copyright_str = tk.StringVar()

            self.output_target = tk.StringVar()

            self._build_ui()
            self._refresh_mode_label()
            self._refresh_field_visibility()

        def _build_ui(self):
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)

            main = ttk.Frame(self.root, padding=10)
            main.grid(row=0, column=0, sticky="nsew")
            main.columnconfigure(0, weight=1)
            main.rowconfigure(6, weight=1)

            input_frame = ttk.LabelFrame(main, text="1) Input")
            input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
            input_frame.columnconfigure(1, weight=1)
            ttk.Label(input_frame, text="Image file or folder").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            ttk.Entry(input_frame, textvariable=self.input_path).grid(row=0, column=1, sticky="ew", padx=8, pady=8)
            ttk.Button(input_frame, text="Browse File", command=self._pick_file).grid(row=0, column=2, padx=4, pady=8)
            ttk.Button(input_frame, text="Browse Folder", command=self._pick_folder).grid(row=0, column=3, padx=4, pady=8)
            ttk.Label(input_frame, textvariable=self.mode_label).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

            preset_frame = ttk.LabelFrame(main, text="2) Camera + Exposure")
            preset_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
            preset_frame.columnconfigure(1, weight=1)
            ttk.Label(preset_frame, text="Preset").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            ttk.Combobox(
                preset_frame,
                textvariable=self.preset,
                state="readonly",
                values=["random", *sorted(CAMERA_PRESETS.keys())],
            ).grid(row=0, column=1, sticky="ew", padx=8, pady=8)
            ttk.Checkbutton(
                preset_frame,
                text="Randomize ISO, shutter speed, and aperture",
                variable=self.randomize,
            ).grid(row=1, column=1, sticky="w", padx=8, pady=(0, 8))

            time_frame = ttk.LabelFrame(main, text="3) Timestamp")
            time_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
            time_frame.columnconfigure(2, weight=1)
            ttk.Radiobutton(time_frame, text="Random", variable=self.timestamp_mode, value="random", command=self._refresh_field_visibility).grid(row=0, column=0, sticky="w", padx=8, pady=8)
            ttk.Label(time_frame, text="Days back").grid(row=0, column=1, sticky="e", padx=8, pady=8)
            self.days_back_entry = ttk.Entry(time_frame, textvariable=self.days_back, width=10)
            self.days_back_entry.grid(row=0, column=2, sticky="w", padx=8, pady=8)
            ttk.Radiobutton(time_frame, text="Fixed", variable=self.timestamp_mode, value="fixed", command=self._refresh_field_visibility).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))
            ttk.Label(time_frame, text="YYYY:MM:DD HH:MM:SS").grid(row=1, column=1, sticky="e", padx=8, pady=(0, 8))
            self.fixed_dt_entry = ttk.Entry(time_frame, textvariable=self.fixed_datetime)
            self.fixed_dt_entry.grid(row=1, column=2, sticky="ew", padx=8, pady=(0, 8))

            loc_frame = ttk.LabelFrame(main, text="4) GPS")
            loc_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
            loc_frame.columnconfigure(3, weight=1)
            ttk.Radiobutton(loc_frame, text="City", variable=self.location_mode, value="city", command=self._refresh_field_visibility).grid(row=0, column=0, sticky="w", padx=8, pady=8)
            ttk.Label(loc_frame, text="City name").grid(row=0, column=1, sticky="e", padx=8, pady=8)
            self.city_entry = ttk.Entry(loc_frame, textvariable=self.city)
            self.city_entry.grid(row=0, column=2, columnspan=2, sticky="ew", padx=8, pady=8)

            ttk.Radiobutton(loc_frame, text="Manual", variable=self.location_mode, value="manual", command=self._refresh_field_visibility).grid(row=1, column=0, sticky="w", padx=8, pady=8)
            ttk.Label(loc_frame, text="Latitude").grid(row=1, column=1, sticky="e", padx=8, pady=8)
            self.lat_entry = ttk.Entry(loc_frame, textvariable=self.lat, width=14)
            self.lat_entry.grid(row=1, column=2, sticky="w", padx=8, pady=8)
            ttk.Label(loc_frame, text="Longitude").grid(row=1, column=3, sticky="e", padx=8, pady=8)
            self.lon_entry = ttk.Entry(loc_frame, textvariable=self.lon, width=14)
            self.lon_entry.grid(row=1, column=4, sticky="w", padx=8, pady=8)

            ttk.Label(loc_frame, text="Altitude (optional)").grid(row=2, column=1, sticky="e", padx=8, pady=(0, 8))
            self.alt_entry = ttk.Entry(loc_frame, textvariable=self.alt, width=14)
            self.alt_entry.grid(row=2, column=2, sticky="w", padx=8, pady=(0, 8))
            ttk.Radiobutton(loc_frame, text="No GPS", variable=self.location_mode, value="none", command=self._refresh_field_visibility).grid(row=2, column=0, sticky="w", padx=8, pady=(0, 8))

            meta_frame = ttk.LabelFrame(main, text="5) Metadata (optional)")
            meta_frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))
            meta_frame.columnconfigure(1, weight=1)
            self._add_labeled_entry(meta_frame, 0, "Title", self.title_text)
            self._add_labeled_entry(meta_frame, 1, "Description", self.description)
            self._add_labeled_entry(meta_frame, 2, "Artist", self.artist)
            self._add_labeled_entry(meta_frame, 3, "Copyright", self.copyright_str)

            out_frame = ttk.LabelFrame(main, text="6) Output")
            out_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8))
            out_frame.columnconfigure(1, weight=1)
            ttk.Label(out_frame, text="Output file/folder (optional)").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            ttk.Entry(out_frame, textvariable=self.output_target).grid(row=0, column=1, sticky="ew", padx=8, pady=8)
            ttk.Button(out_frame, text="Browse", command=self._pick_output).grid(row=0, column=2, padx=8, pady=8)

            run_frame = ttk.Frame(main)
            run_frame.grid(row=6, column=0, sticky="nsew")
            run_frame.columnconfigure(0, weight=1)
            run_frame.rowconfigure(1, weight=1)

            self.run_button = ttk.Button(run_frame, text="Apply Fake EXIF", command=self._start_run)
            self.run_button.grid(row=0, column=0, sticky="w", pady=(0, 8))

            self.log_box = scrolledtext.ScrolledText(run_frame, wrap="word", height=16)
            self.log_box.grid(row=1, column=0, sticky="nsew")

            self.input_path.trace_add("write", lambda *_: self._refresh_mode_label())

        @staticmethod
        def _add_labeled_entry(parent: ttk.LabelFrame, row: int, label: str, variable: tk.StringVar):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=8, pady=4)
            ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=4)

        def _append_log(self, text: str):
            self.log_box.insert("end", text + "\n")
            self.log_box.see("end")

        def _set_log(self, text: str):
            self.log_box.delete("1.0", "end")
            self._append_log(text)

        def _pick_file(self):
            selected = filedialog.askopenfilename(
                title="Select JPEG image",
                filetypes=[("JPEG files", "*.jpg *.jpeg *.jpe *.jfif"), ("All files", "*.*")],
            )
            if selected:
                self.input_path.set(selected)

        def _pick_folder(self):
            selected = filedialog.askdirectory(title="Select folder of images")
            if selected:
                self.input_path.set(selected)

        def _pick_output(self):
            input_val = self.input_path.get().strip()
            if input_val and Path(input_val).is_dir():
                selected = filedialog.askdirectory(title="Select output folder")
            else:
                selected = filedialog.asksaveasfilename(
                    title="Select output image file",
                    defaultextension=".jpg",
                    filetypes=[("JPEG files", "*.jpg *.jpeg *.jpe *.jfif"), ("All files", "*.*")],
                )
            if selected:
                self.output_target.set(selected)

        def _refresh_mode_label(self):
            raw = self.input_path.get().strip()
            if not raw:
                self.mode_label.set("Mode: Not selected")
                return
            p = Path(raw)
            if p.exists() and p.is_dir():
                self.mode_label.set("Mode: Batch (folder)")
            elif p.exists() and p.is_file():
                self.mode_label.set("Mode: Single image")
            else:
                self.mode_label.set("Mode: Path does not exist")

        def _refresh_field_visibility(self):
            random_ts = self.timestamp_mode.get() == "random"
            self.days_back_entry.configure(state="normal" if random_ts else "disabled")
            self.fixed_dt_entry.configure(state="disabled" if random_ts else "normal")

            mode = self.location_mode.get()
            self.city_entry.configure(state="normal" if mode == "city" else "disabled")
            manual_state = "normal" if mode == "manual" else "disabled"
            self.lat_entry.configure(state=manual_state)
            self.lon_entry.configure(state=manual_state)
            self.alt_entry.configure(state=manual_state)

        def _build_command(self) -> tuple[list[str] | None, str | None]:
            input_value = self.input_path.get().strip()
            if not input_value:
                return None, "Input path is required."

            input_path = Path(input_value)
            if not input_path.exists():
                return None, f"Input path does not exist: {input_value}"

            cmd = ["fake", input_value, "-p", self.preset.get()]

            if self.randomize.get():
                cmd.append("--random")

            if self.timestamp_mode.get() == "random":
                try:
                    days = int(self.days_back.get().strip())
                    if days < 0:
                        return None, "Days back must be zero or greater."
                except ValueError:
                    return None, "Days back must be an integer."
                cmd.extend(["--days-back", str(days)])
            else:
                fixed_dt = self.fixed_datetime.get().strip()
                if not fixed_dt:
                    return None, "Fixed timestamp is required in fixed mode."
                try:
                    datetime.strptime(fixed_dt, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    return None, "Timestamp must match YYYY:MM:DD HH:MM:SS"
                cmd.extend(["--datetime", fixed_dt])

            location_mode = self.location_mode.get()
            if location_mode == "city":
                city = self.city.get().strip()
                if not city:
                    return None, "City is required when GPS mode is City."
                cmd.extend(["--city", city])
            elif location_mode == "manual":
                try:
                    lat = float(self.lat.get().strip())
                    lon = float(self.lon.get().strip())
                except ValueError:
                    return None, "Latitude and longitude must be valid numbers."
                cmd.extend(["--lat", str(lat), "--lon", str(lon)])
                alt_raw = self.alt.get().strip()
                if alt_raw:
                    try:
                        alt = float(alt_raw)
                    except ValueError:
                        return None, "Altitude must be a valid number."
                    cmd.extend(["--alt", str(alt)])

            if self.title_text.get().strip():
                cmd.extend(["--title", self.title_text.get().strip()])
            if self.description.get().strip():
                cmd.extend(["--description", self.description.get().strip()])
            if self.artist.get().strip():
                cmd.extend(["--artist", self.artist.get().strip()])
            if self.copyright_str.get().strip():
                cmd.extend(["--copyright", self.copyright_str.get().strip()])

            output_target = self.output_target.get().strip()
            if input_path.is_dir():
                # Force a GUI default so output lands beside the input folder,
                # not inside it via exif_editor.py's internal default.
                cmd.extend(["-d", output_target or get_default_batch_output_dir(input_value)])
            elif output_target:
                cmd.extend(["-o", output_target])

            return cmd, None

        def _start_run(self):
            if self.running:
                return

            self._refresh_field_visibility()
            cmd, err = self._build_command()
            if err:
                messagebox.showerror("Validation error", err)
                return

            self.running = True
            self.run_button.configure(state="disabled")
            self._set_log("Running command:\n  python exif_editor.py " + " ".join(cmd))

            worker = threading.Thread(target=self._run_command, args=(cmd,), daemon=True)
            worker.start()

        def _run_command(self, cmd: list[str]):
            def emit(line: str):
                self.root.after(0, self._append_log, line)

            return_code = run_exif_editor_args(cmd, emit_line=emit)

            def finish():
                self.running = False
                self.run_button.configure(state="normal")
                if return_code == 0:
                    self._append_log("\nCompleted successfully.")
                    messagebox.showinfo("Done", "EXIF metadata applied successfully.")
                else:
                    self._append_log(f"\nCommand failed with exit code {return_code}.")
                    messagebox.showerror("Failed", f"Command failed with exit code {return_code}.")

            self.root.after(0, finish)

    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


def main() -> int:
    use_cli = "--cli" in sys.argv
    if use_cli:
        return run_cli_fallback()
    try:
        return run_gui()
    except Exception as exc:
        print(f"GUI unavailable ({exc}). Falling back to CLI mode.\n")
        return run_cli_fallback()


if __name__ == "__main__":
    raise SystemExit(main())
