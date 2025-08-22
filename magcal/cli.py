"""Beautiful CLI interface for magnetometer calibration using Rich"""

import click
import time
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich.align import Align
from rich.columns import Columns
from rich.status import Status
from datetime import datetime
import os
import questionary

from .core import MagnetometerCalibrator

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0")
def main(ctx):
    """🧭 A Magnetometer Calibration Tool for Embedded Systems"""
    if ctx.invoked_subcommand is None:
        # User just typed 'magcal' - show interactive menu
        _run_interactive_menu()

@main.command()
@click.option('--port', '-p', default='/dev/tty.usbmodem101', help='Serial port path')
@click.option('--baudrate', '-b', default=115200, help='Serial baudrate')
@click.option('--samples', '-n', default=1000, help='Number of samples to collect')
@click.option('--method', '-m', type=click.Choice(['sphere', 'ellipsoid']), default='ellipsoid', help='Calibration method')
@click.option('--pattern', help='Custom regex pattern for data parsing')
@click.option('--no-plot', is_flag=True, help='Disable real-time plotting')
def calibrate(port, baudrate, samples, method, pattern, no_plot):
    """🎯 Run complete magnetometer calibration workflow"""
    
    # Display beautiful header
    _display_header()
    
    # Show configuration
    _display_config(port, baudrate, samples, method, pattern, not no_plot)
    
    # Initialize calibrator
    cal = MagnetometerCalibrator(
        port=port,
        baudrate=baudrate,
        data_pattern=pattern
    )
    
    try:
        # Data collection phase
        if _collect_data_with_progress(cal, samples, not no_plot):
            # Calibration phase
            _perform_calibration_with_status(cal, method)
            
            # Results display
            _display_results(cal)
            
            # Save results
            _save_results_with_status(cal)
            
        else:
            console.print("❌ [red]Failed to collect sufficient data[/red]")
            
    except KeyboardInterrupt:
        _handle_interruption(cal)
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@main.command()
@click.option('--port', '-p', help='Serial port path')
@click.option('--baudrate', '-b', type=int, help='Serial baudrate')
@click.option('--samples', '-n', type=int, help='Number of samples to collect')
@click.option('--method', '-m', type=click.Choice(['sphere', 'ellipsoid']), help='Calibration method')
def interactive():
    """🎮 Interactive configuration and calibration"""
    
    _display_header()
    
    console.print("🎮 [bold cyan]Interactive Configuration Mode[/bold cyan]\n")
    
    # Get configuration interactively
    config = _get_interactive_config()
    
    # Confirm and proceed
    if Confirm.ask("🚀 Start calibration with these settings?"):
        cal = MagnetometerCalibrator(
            port=config['port'],
            baudrate=config['baudrate'],
            data_pattern=config.get('pattern')
        )
        
        try:
            if _collect_data_with_progress(cal, config['samples'], True):
                _perform_calibration_with_status(cal, config['method'])
                _display_results(cal)
                _save_results_with_status(cal)
        except KeyboardInterrupt:
            _handle_interruption(cal)

@main.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--method', '-m', type=click.Choice(['sphere', 'ellipsoid']), default='ellipsoid', help='Calibration method')
def from_file(data_file, method):
    """📁 Calibrate from existing data file"""
    
    _display_header()
    
    console.print(f"📁 [cyan]Loading data from: {data_file}[/cyan]\n")
    
    cal = MagnetometerCalibrator()
    
    with Status("Loading data...", spinner="dots") as status:
        cal.load_data_from_file(data_file)
        time.sleep(0.5)  # Visual feedback
    
    console.print(f"✅ [green]Loaded {len(cal.raw_data)} samples[/green]\n")
    
    _perform_calibration_with_status(cal, method)
    _display_results(cal)
    _save_results_with_status(cal)

@main.command()
@click.option('--port', '-p', default='/dev/tty.usbmodem101', help='Serial port path')
@click.option('--baudrate', '-b', default=115200, help='Serial baudrate')
@click.option('--pattern', help='Custom regex pattern for data parsing')
def monitor(port, baudrate, pattern):
    """📡 Monitor real-time magnetometer data"""
    
    _display_header()
    
    console.print("📡 [bold cyan]Real-time Magnetometer Monitor[/bold cyan]\n")
    console.print("Press Ctrl+C to stop monitoring\n")
    
    cal = MagnetometerCalibrator(
        port=port,
        baudrate=baudrate,
        data_pattern=pattern
    )
    
    _monitor_realtime_data(cal)

def _display_header():
    """Display beautiful application header with ASCII art"""
    ascii_banner = """
███╗   ███╗ █████╗  ██████╗  ██████╗ █████╗ ██╗     
████╗ ████║██╔══██╗██╔════╝ ██╔════╝██╔══██╗██║     
██╔████╔██║███████║██║  ███╗██║     ███████║██║     
██║╚██╔╝██║██╔══██║██║   ██║██║     ██╔══██║██║     
██║ ╚═╝ ██║██║  ██║╚██████╔╝╚██████╗██║  ██║███████╗
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝

[white]A CLI-based magnetometer calibration tool for embedded systems[/white]
"""
    
    console.print(Panel(
        Align.center(ascii_banner.strip()),
        style="bold white",
        padding=(1, 2),
        border_style="blue"
    ))
    console.print()

def _display_config(port, baudrate, samples, method, pattern, plot_enabled):
    """Display configuration in a beautiful table"""
    config_table = Table(title="📋 Configuration", style="cyan")
    config_table.add_column("Setting", style="bold")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Serial Port", port)
    config_table.add_row("Baudrate", str(baudrate))
    config_table.add_row("Samples", str(samples))
    config_table.add_row("Method", method.title())
    config_table.add_row("Custom Pattern", pattern or "Default")
    config_table.add_row("Real-time Plot", "Enabled" if plot_enabled else "Disabled")
    
    console.print(config_table)
    console.print()

def _collect_data_with_progress(cal, min_samples, enable_plot):
    """Collect data with beautiful progress display"""
    
    console.print("🔄 [bold yellow]Data Collection Phase[/bold yellow]\n")
    
    # Preparation instructions
    prep_panel = Panel(
        "[bold]Preparation Steps:[/bold]\n\n"
        "1. 🔌 Ensure magnetometer is connected and powered\n"
        "2. 📡 Verify device is sending raw magnetometer data\n"
        "3. 🔄 Prepare to rotate device in ALL orientations\n"
        "4. ⏰ Collection will start automatically",
        title="🚀 Get Ready",
        style="yellow"
    )
    console.print(prep_panel)
    console.print()
    
    if not questionary.confirm("Ready to start data collection?", default=True).ask():
        return False
    
    # Override the collect_data method to use Rich progress
    return _collect_with_rich_progress(cal, min_samples, enable_plot)

def _collect_with_rich_progress(cal, min_samples, enable_plot):
    """Custom data collection with Rich progress bars"""
    import serial
    import re
    
    if enable_plot:
        cal.setup_realtime_plot()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("samples"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("Collecting data...", total=min_samples)
        
        start_time = time.time()
        reconnect_delay = 3
        ser = None
        pattern = cal.data_pattern
        
        while len(cal.raw_data) < min_samples:
            try:
                # Connection management
                if ser is None or not ser.is_open:
                    progress.update(task, description="🔌 Connecting to device...")
                    ser = serial.Serial(cal.port, cal.baudrate, timeout=1)
                    progress.update(task, description="📡 Collecting data...")
                
                # Read data
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                match = re.search(pattern, line)
                
                if match and len(match.groups()) == 3:
                    try:
                        x, y, z = map(float, match.groups())
                        cal.raw_data.append([x, y, z])
                        
                        # Update progress
                        progress.update(task, completed=len(cal.raw_data))
                        
                        # Update plot periodically
                        if enable_plot and len(cal.raw_data) % 25 == 0:
                            cal.update_plot()
                            
                    except ValueError:
                        continue
                        
            except (serial.SerialException, OSError):
                progress.update(task, description="⚠️ Connection lost, reconnecting...")
                if ser and ser.is_open:
                    try:
                        ser.close()
                    except:
                        pass
                ser = None
                time.sleep(reconnect_delay)
                continue
            except Exception:
                time.sleep(0.1)
                continue
        
        # Cleanup
        if ser and ser.is_open:
            try:
                ser.close()
            except:
                pass
    
    console.print(f"✅ [green]Collection complete! Got {len(cal.raw_data)} samples[/green]\n")
    return True

def _perform_calibration_with_status(cal, method):
    """Perform calibration with status display"""
    
    console.print("🧮 [bold yellow]Calibration Phase[/bold yellow]\n")
    
    with Status(f"Running {method} calibration...", spinner="dots") as status:
        cal.calibrate(method=method)
        time.sleep(1)  # Visual feedback
    
    console.print(f"✅ [green]Calibration complete using {method} method[/green]\n")

def _display_results(cal):
    """Display calibration results in beautiful format"""
    
    console.print("📊 [bold yellow]Calibration Results[/bold yellow]\n")
    
    if cal.calibration_quality:
        # Quality metrics table
        quality_table = Table(title="📈 Quality Metrics", style="green")
        quality_table.add_column("Metric", style="bold")
        quality_table.add_column("Value", style="cyan")
        quality_table.add_column("Assessment", style="yellow")
        
        sphericity = cal.calibration_quality['sphericity']
        quality_score = cal.calibration_quality['quality_score']
        
        # Determine quality assessment
        if quality_score < 0.05:
            assessment = "🟢 Excellent"
        elif quality_score < 0.1:
            assessment = "🟡 Good"
        elif quality_score < 0.2:
            assessment = "🟠 Fair"
        else:
            assessment = "🔴 Poor"
        
        quality_table.add_row("Mean Radius", f"{cal.calibration_quality['mean_radius']:.3f} µT", "")
        quality_table.add_row("Radius Std Dev", f"{cal.calibration_quality['std_radius']:.3f} µT", "")
        quality_table.add_row("Quality Score", f"{quality_score:.4f}", assessment)
        quality_table.add_row("Sphericity", f"{sphericity:.4f}", "")
        
        console.print(quality_table)
        console.print()
    
    # Calibration parameters
    if cal.calibration_params:
        params_panel = Panel(
            _format_calibration_params(cal.calibration_params),
            title="🎯 Calibration Parameters",
            style="blue"
        )
        console.print(params_panel)
        console.print()

def _format_calibration_params(params):
    """Format calibration parameters for display"""
    text = f"[bold]Method:[/bold] {params['method'].title()}\n\n"
    
    # Hard iron offset
    center = params['center']
    text += f"[bold]Hard Iron Offset:[/bold]\n"
    text += f"  X: {center[0]:8.6f}\n"
    text += f"  Y: {center[1]:8.6f}\n"
    text += f"  Z: {center[2]:8.6f}\n\n"
    
    # Soft iron matrix
    if 'transform_matrix' in params:
        matrix = params['transform_matrix']
        text += f"[bold]Soft Iron Matrix:[/bold]\n"
        for i in range(3):
            text += f"  [{matrix[i,0]:8.6f}, {matrix[i,1]:8.6f}, {matrix[i,2]:8.6f}]\n"
    
    return text

def _save_results_with_status(cal):
    """Save results with status display"""
    
    console.print("💾 [bold yellow]Saving Results[/bold yellow]\n")
    
    with Status("Generating output files...", spinner="dots") as status:
        # Save data
        json_file = cal.save_data_to_file()
        time.sleep(0.5)
        
        # Save calibration
        cal.save_calibration()
        time.sleep(0.5)
    
    # Show saved files
    files_table = Table(title="📁 Generated Files", style="green")
    files_table.add_column("Type", style="bold")
    files_table.add_column("Location", style="cyan")
    
    files_table.add_row("Raw Data (JSON)", json_file)
    files_table.add_row("Calibration (C Header)", "output/mag_calibration_*.h")
    
    console.print(files_table)
    console.print()
    
    success_panel = Panel(
        "[bold green]🎉 Calibration Complete![/bold green]\n\n"
        "Your calibration files are ready for use in embedded systems.\n"
        "Check the 'output' directory for all generated files.",
        style="green"
    )
    console.print(success_panel)

def _handle_interruption(cal):
    """Handle keyboard interruption gracefully"""
    console.print("\n⚠️ [yellow]Calibration interrupted by user[/yellow]\n")
    
    if len(cal.raw_data) > 500:
        console.print(f"📊 Collected {len(cal.raw_data)} samples before interruption")
        
        if Confirm.ask("💾 Save partial data?"):
            with Status("Saving partial data...", spinner="dots"):
                cal.save_data_to_file()
                time.sleep(0.5)
            console.print("✅ [green]Partial data saved[/green]")

def _get_interactive_config():
    """Get configuration interactively with questionary prompts"""
    
    config = {}
    
    # Serial configuration
    console.print("🔌 [bold]Serial Configuration[/bold]\n")
    config['port'] = questionary.text("Serial port:", default="/dev/tty.usbmodem101").ask()
    config['baudrate'] = int(questionary.text("Baudrate:", default="115200").ask())
    console.print()
    
    # Data format
    console.print("📡 [bold]Data Format[/bold]\n")
    use_custom = questionary.confirm("Use custom data pattern?", default=False).ask()
    if use_custom:
        console.print("\n[yellow]Enter regex pattern with 3 capturing groups for x, y, z values[/yellow]")
        console.print("[dim]Example: r'MAG: ([-\\d.]+),([-\\d.]+),([-\\d.]+)'[/dim]\n")
        config['pattern'] = questionary.text("Pattern:").ask()
    console.print()
    
    # Sample configuration
    console.print("📊 [bold]Sample Configuration[/bold]\n")
    config['samples'] = int(questionary.text("Number of samples:", default="1000").ask())
    console.print()
    
    # Calibration method
    console.print("🧮 [bold]Calibration Method[/bold]\n")
    config['method'] = questionary.select(
        "Choose calibration method:",
        choices=[
            questionary.Choice("🌐 Ellipsoid (Advanced - hard + soft iron correction)", value="ellipsoid"),
            questionary.Choice("⚪ Sphere (Simple - hard iron correction only)", value="sphere")
        ],
        default="ellipsoid"
    ).ask()
    console.print()
    
    return config

def _monitor_realtime_data(cal):
    """Monitor real-time magnetometer data with live display"""
    import serial
    import re
    from collections import deque
    
    data_buffer = deque(maxlen=100)  # Keep last 100 readings
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Create data table
    def make_data_table():
        table = Table(title="📡 Live Magnetometer Data")
        table.add_column("Time", style="dim")
        table.add_column("X (µT)", style="red")
        table.add_column("Y (µT)", style="green") 
        table.add_column("Z (µT)", style="blue")
        table.add_column("Magnitude", style="yellow")
        
        for timestamp, x, y, z in list(data_buffer)[-10:]:  # Show last 10 readings
            magnitude = np.sqrt(x*x + y*y + z*z)
            table.add_row(
                timestamp.strftime("%H:%M:%S.%f")[:-3],
                f"{x:8.2f}",
                f"{y:8.2f}",
                f"{z:8.2f}",
                f"{magnitude:8.2f}"
            )
        return table
    
    try:
        with Live(layout, refresh_per_second=4, console=console) as live:
            layout["header"].update(Panel("🔄 Monitoring... Press Ctrl+C to stop", style="blue"))
            layout["footer"].update(Panel(f"Connected to: {cal.port} @ {cal.baudrate} baud", style="dim"))
            
            ser = serial.Serial(cal.port, cal.baudrate, timeout=1)
            
            while True:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    match = re.search(cal.data_pattern, line)
                    
                    if match and len(match.groups()) == 3:
                        x, y, z = map(float, match.groups())
                        data_buffer.append((datetime.now(), x, y, z))
                        
                        layout["main"].update(make_data_table())
                    
                except Exception:
                    continue
                    
    except KeyboardInterrupt:
        console.print("\n✅ [green]Monitoring stopped[/green]")
    except Exception as e:
        console.print(f"\n❌ [red]Monitor error: {e}[/red]")

def _run_interactive_menu():
    """Run the main interactive menu when user types just 'magcal'"""
    
    _display_header()
    
    # Check if this is a first-time user
    if _is_first_time_user():
        console.print("🎯 [bold white]Welcome to MAGCAL![/bold white]\n")
        console.print("👋 [yellow]Looks like this is your first time using MAGCAL![/yellow]")
        console.print("[dim]Let's get you set up with an interactive configuration...[/dim]\n")
        
        if questionary.confirm("🚀 Ready to configure your magnetometer calibration?", default=True).ask():
            _run_first_time_setup()
            return
        else:
            console.print("[dim]You can always run setup later by selecting 'Interactive Setup' from the menu.[/dim]\n")

    console.print("🎯 [bold white]Welcome back to MAGCAL![/bold white]\n")
    console.print("[dim]Use ↑↓ arrow keys to navigate and Enter to select[/dim]\n")
    
    # Create menu choices with questionary
    menu_choices = [
        questionary.Choice("🚀 Run Full Calibration", value="1"),
        questionary.Choice("📡 Monitor Real-time Data", value="2"), 
        questionary.Choice("📁 Calibrate from File", value="3"),
        questionary.Choice("⚙️ Interactive Setup", value="4"),
        questionary.Choice("❓ Show Help", value="5"),
        questionary.Choice("🚪 Exit", value="6")
    ]
    
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=menu_choices,
            style=questionary.Style([
                ('selected', 'bold bg:#0087ff fg:#ffffff'),  # Blue background for selected
                ('pointer', 'bold fg:#0087ff'),                # Blue arrow
                ('highlighted', 'bold fg:#0087ff'),            # Blue text for highlighted
                ('answer', 'bold fg:#00aa00'),                 # Green for final answer
            ])
        ).ask()
        
        if choice is None:  # User pressed Ctrl+C
            console.print("\n👋 [bold blue]Thanks for using MAGCAL! Happy calibrating! 🛰️[/bold blue]")
            break
        
        console.print()
        
        if choice == "1":
            # Run full calibration with default settings
            console.print("🚀 [bold green]Starting full calibration with default settings...[/bold green]\n")
            cal = MagnetometerCalibrator()
            try:
                if _collect_data_with_progress(cal, 1000, True):
                    _perform_calibration_with_status(cal, 'ellipsoid')
                    _display_results(cal)
                    _save_results_with_status(cal)
                    break
            except KeyboardInterrupt:
                _handle_interruption(cal)
                break
                
        elif choice == "2":
            # Monitor real-time data
            console.print("📡 [bold green]Starting real-time monitor...[/bold green]\n")
            cal = MagnetometerCalibrator()
            _monitor_realtime_data(cal)
            break
            
        elif choice == "3":
            # Calibrate from file
            console.print("📁 [bold green]Calibrate from existing file[/bold green]\n")
            
            # List available JSON files in output directory
            output_dir = "output"
            if os.path.exists(output_dir):
                json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
                if json_files:
                    console.print("📂 Available data files:")
                    for i, file in enumerate(json_files, 1):
                        console.print(f"  {i}. {file}")
                    console.print()
                    
                    file_choice = Prompt.ask("Enter file number or full path")
                    
                    try:
                        # Check if it's a number (selecting from list)
                        file_index = int(file_choice) - 1
                        if 0 <= file_index < len(json_files):
                            data_file = os.path.join(output_dir, json_files[file_index])
                        else:
                            console.print("❌ [red]Invalid file number[/red]")
                            continue
                    except ValueError:
                        # It's a file path
                        data_file = file_choice
                        
                    if os.path.exists(data_file):
                        cal = MagnetometerCalibrator()
                        cal.load_data_from_file(data_file)
                        _perform_calibration_with_status(cal, 'ellipsoid')
                        _display_results(cal)
                        _save_results_with_status(cal)
                        break
                    else:
                        console.print("❌ [red]File not found[/red]")
                        continue
                else:
                    console.print("❌ [red]No data files found in output directory[/red]")
                    data_file = Prompt.ask("Enter full path to data file")
                    if os.path.exists(data_file):
                        cal = MagnetometerCalibrator()
                        cal.load_data_from_file(data_file)
                        _perform_calibration_with_status(cal, 'ellipsoid')
                        _display_results(cal)
                        _save_results_with_status(cal)
                        break
                    else:
                        console.print("❌ [red]File not found[/red]")
                        continue
            else:
                data_file = Prompt.ask("Enter full path to data file")
                if os.path.exists(data_file):
                    cal = MagnetometerCalibrator()
                    cal.load_data_from_file(data_file)
                    _perform_calibration_with_status(cal, 'ellipsoid')
                    _display_results(cal)
                    _save_results_with_status(cal)
                    break
                else:
                    console.print("❌ [red]File not found[/red]")
                    continue
                    
        elif choice == "4":
            # Interactive setup
            console.print("⚙️ [bold green]Starting interactive setup...[/bold green]\n")
            config = _get_interactive_config()
            
            if questionary.confirm("🚀 Start calibration with these settings?", default=True).ask():
                cal = MagnetometerCalibrator(
                    port=config['port'],
                    baudrate=config['baudrate'],
                    data_pattern=config.get('pattern')
                )
                
                try:
                    if _collect_data_with_progress(cal, config['samples'], True):
                        _perform_calibration_with_status(cal, config['method'])
                        _display_results(cal)
                        _save_results_with_status(cal)
                        break
                except KeyboardInterrupt:
                    _handle_interruption(cal)
                    break
            else:
                console.print("🔄 [yellow]Returning to main menu...[/yellow]\n")
                continue
                
        elif choice == "5":
            # Show help
            console.print("❓ [bold green]Available Commands:[/bold green]\n")
            
            help_table = Table(title="🔧 Command Reference", style="blue")
            help_table.add_column("Command", style="bold cyan")
            help_table.add_column("Description", style="white")
            
            help_table.add_row("magcal", "Show this interactive menu")
            help_table.add_row("magcal calibrate", "Run calibration with command-line options")
            help_table.add_row("magcal interactive", "Interactive configuration mode")
            help_table.add_row("magcal monitor", "Real-time data monitoring")
            help_table.add_row("magcal from-file <file>", "Calibrate from existing data file")
            help_table.add_row("magcal --help", "Show detailed help for all commands")
            
            console.print(help_table)
            console.print()
            
            if not questionary.confirm("🔄 Return to main menu?", default=True).ask():
                break
                
        elif choice == "6":
            # Exit
            console.print("👋 [bold blue]Thanks for using MAGCAL! Happy calibrating! 🛰️[/bold blue]")
            break
    
    console.print()

def _is_first_time_user():
    """Check if this is a first-time user by looking for previous calibration files or config"""
    output_dir = "output"
    
    # Check if output directory exists and has any calibration files
    if os.path.exists(output_dir):
        json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        header_files = [f for f in os.listdir(output_dir) if f.endswith('.h')]
        if json_files or header_files:
            return False
    
    # Could also check for a config file in the future
    # if os.path.exists('.magcal_config'):
    #     return False
    
    return True

def _run_first_time_setup():
    """Run the first-time setup flow for new users"""
    console.print("🛠️ [bold green]First-Time Setup[/bold green]\n")
    
    # Show preparation instructions
    prep_panel = Panel(
        "[bold]Before we start, please ensure:[/bold]\n\n"
        "1. 🔌 Your magnetometer is connected via serial\n"
        "2. 📡 Device is sending RAW magnetometer data (not normalized)\n"
        "3. 🔧 You know your serial port and baudrate\n"
        "4. 📝 You have the correct data format pattern\n\n"
        "[yellow]💡 Tip: Check your device documentation for data format details[/yellow]",
        title="🚀 Preparation Checklist",
        style="yellow"
    )
    console.print(prep_panel)
    console.print()
    
    if not questionary.confirm("✅ Have you completed the preparation steps above?", default=True).ask():
        console.print("\n📖 [cyan]Please complete the preparation steps and run 'magcal' again when ready.[/cyan]")
        console.print("💡 [dim]You can also check the README for detailed setup instructions.[/dim]\n")
        return
    
    console.print("\n🎯 [bold cyan]Great! Let's configure your magnetometer...[/bold cyan]\n")
    
    # Get configuration interactively
    config = _get_interactive_config()
    
    # Show configuration summary
    console.print("📋 [bold]Configuration Summary:[/bold]\n")
    summary_table = Table(style="cyan", show_header=False)
    summary_table.add_column("Setting", style="bold")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Serial Port", config['port'])
    summary_table.add_row("Baudrate", str(config['baudrate']))
    summary_table.add_row("Samples", str(config['samples']))
    summary_table.add_row("Method", config['method'].title())
    summary_table.add_row("Custom Pattern", config.get('pattern', 'Default'))
    
    console.print(summary_table)
    console.print()
    
    if questionary.confirm("🚀 Start your first calibration with these settings?", default=True).ask():
        cal = MagnetometerCalibrator(
            port=config['port'],
            baudrate=config['baudrate'],
            data_pattern=config.get('pattern')
        )
        
        try:
            console.print("\n🎉 [bold green]Starting your first calibration![/bold green]\n")
            console.print("📝 [yellow]Remember to rotate your device in ALL orientations during data collection![/yellow]\n")
            
            if _collect_data_with_progress(cal, config['samples'], True):
                _perform_calibration_with_status(cal, config['method'])
                _display_results(cal)
                _save_results_with_status(cal)
                
                # Show success message for first-time users
                success_panel = Panel(
                    "[bold green]🎉 Congratulations![/bold green]\n\n"
                    "You've successfully completed your first magnetometer calibration!\n\n"
                    "✅ Your calibration files are ready in the 'output' directory\n"
                    "✅ You can now run 'magcal' anytime for quick access to all features\n"
                    "✅ Use 'magcal monitor' to view real-time data\n"
                    "✅ Use 'magcal from-file' to recalibrate existing data\n\n"
                    "[dim]Happy calibrating! 🛰️[/dim]",
                    title="🏁 Setup Complete",
                    style="green"
                )
                console.print(success_panel)
            else:
                console.print("❌ [red]Calibration failed. Please check your setup and try again.[/red]")
                
        except KeyboardInterrupt:
            _handle_interruption(cal)
            console.print("\n💡 [cyan]Setup interrupted. Run 'magcal' again to continue setup or access the main menu.[/cyan]")
    else:
        console.print("\n🔄 [yellow]Setup cancelled. You can run 'magcal' again anytime to continue.[/yellow]")

if __name__ == "__main__":
    main()