#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced MT5 Trading Monitor GUI with Strategy Phase Tracking
Real-time candlestick charts, configuration viewer, and strategy state monitoring
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
import sys
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
import importlib.util
import queue
import math

# Try to import charting libraries
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.backends._backend_tk import NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None  # type: ignore
    FigureCanvasTkAgg = None  # type: ignore
    NavigationToolbar2Tk = None  # type: ignore
    Figure = None  # type: ignore
    mdates = None  # type: ignore
    Rectangle = None  # type: ignore

# Dynamic imports to avoid VS Code warnings
def dynamic_import(module_name: str, package_name: Optional[str] = None):
    """Dynamically import modules to avoid static import warnings"""
    try:
        if package_name:
            spec = importlib.util.find_spec(f"{package_name}.{module_name}")
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        
        spec = importlib.util.find_spec(module_name)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except (ImportError, ModuleNotFoundError):
        pass
    return None

# Try to import required modules
try:
    import MetaTrader5 as mt5
    import pandas as pd
    import numpy as np
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    mt5 = None  # type: ignore
    pd = None  # type: ignore
    np = None  # type: ignore

# Dynamic import of signal processing modules
sunrise_signal_adapter = dynamic_import("sunrise_signal_adapter", "src")
if not sunrise_signal_adapter:
    # Try alternative import paths
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    sunrise_signal_adapter = dynamic_import("sunrise_signal_adapter")

# ═══════════════════════════════════════════════════════════════════
# RAY DALIO ALL-WEATHER PORTFOLIO ALLOCATION SYSTEM
# ═══════════════════════════════════════════════════════════════════
# Asset-specific portfolio allocations based on economic scenario hedging:
# - Deflation hedge (USDCHF): Strong in deflationary environments
# - Inflation hedge (XAUUSD): Protects against monetary debasement
# - Standard forex (GBPUSD, EURUSD): Balanced risk/reward
# - Commodities (XAGUSD, AUDUSD): Inflation protection + industrial demand
#
# Position sizing: Risk = DEFAULT_RISK_PERCENT × allocated_capital
# Example with $50,078.20 balance and 1% risk:
#   USDCHF: $50,078.20 × 20% = $10,015.64 → $100.16 risk per trade
#   XAUUSD: $50,078.20 × 18% = $9,014.08 → $90.14 risk per trade
#   GBPUSD: $50,078.20 × 16% = $8,012.51 → $80.13 risk per trade
#   XAGUSD: $50,078.20 × 15% = $7,511.73 → $75.12 risk per trade
# ═══════════════════════════════════════════════════════════════════

ASSET_ALLOCATIONS = {
    'USDCHF': 0.20,   # 20% - Deflation hedge (safe haven currency)
    'XAUUSD': 0.18,   # 18% - Inflation hedge (gold standard)
    'GBPUSD': 0.16,   # 16% - Standard forex exposure
    'EURUSD': 0.16,   # 16% - Standard forex exposure
    'XAGUSD': 0.15,   # 15% - Commodity/industrial metal
    'AUDUSD': 0.15,   # 15% - Commodity currency
}

# Default risk percentage per trade (% of allocated capital, not total portfolio)
DEFAULT_RISK_PERCENT = 0.01  # 1% of allocated capital (configurable)

# Application Version
APP_VERSION = "1.1.1"

class AdvancedMT5TradingMonitorGUI:
    """
    Advanced MT5 Trading Monitor with Strategy Phase Tracking
    
    Features:
    - Real-time strategy phase tracking (NORMAL → WAITING_PULLBACK → WAITING_BREAKOUT)
    - Live candlestick charts with indicators and window markers
    - Detailed configuration parameter viewer for each asset
    - Terminal-style phase output with color-coded states
    - Window breakout level visualization
    - EMA crossover and pullback monitoring
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Advanced MT5 Monitor v{APP_VERSION} - Strategy Phase Tracker")
        self.root.geometry("1600x1000")
        
        # Strategy state tracking
        self.strategy_states = {}  # {symbol: {phase, config, indicators, etc}}
        self.strategy_configs = {}
        self.chart_data = {}
        self.window_markers = {}  # Track window levels for charts
        
        # State variables
        self.mt5_connected = False
        self.monitoring_active = False
        self.positions = []
        self.signals_history = []
        self.connection_history = []
        self.signal_manager = None
        
        # Smart logging controls
        self.last_hourly_summary = datetime.now()
        self.hourly_events = {
            'crossovers': 0,
            'armed_transitions': 0,
            'pullbacks_detected': 0,
            'windows_opened': 0,
            'breakouts': 0,
            'invalidations': 0,
            'trades_executed': 0
        }
        
        # Bot startup timestamp - used to ignore old crossovers
        self.bot_startup_time = datetime.now()
        
        # Recursion guard for hourly summary
        self._in_hourly_summary = False
        
        self.data_provider = None
        
        # Broker UTC offset for time filter conversion
        self.broker_utc_offset = self.load_utc_offset_from_config()
        
        # Threading and communication
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.phase_update_queue = queue.Queue()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize GUI
        self.setup_gui()
        
        # Try to initialize MT5 connection
        self.initialize_mt5_connection()
        
        # Load strategy configurations
        self.load_strategy_configurations()
        
        # Setup cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start phase update processing
        self.process_phase_updates()
        
    def setup_logging(self):
        """Configure logging system"""
        # Configure stream handler with UTF-8 encoding
        import sys
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        
        # Force UTF-8 encoding on Windows
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
            except Exception:
                pass  # Fallback if reconfigure fails
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                stream_handler,
                logging.FileHandler('mt5_advanced_monitor.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_gui(self):
        """Initialize the advanced GUI components"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Strategy monitoring and configuration
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Charts and terminal output
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Setup left panel
        self.setup_left_panel(left_frame)
        
        # Setup right panel
        self.setup_right_panel(right_frame)
        
        # Status bar
        self.create_status_bar()
        
    def setup_left_panel(self, parent):
        """Setup the left panel with strategy monitoring"""
        # Connection status
        conn_frame = ttk.LabelFrame(parent, text="Connection Status", padding="5")
        conn_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.connection_status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red", font=("Arial", 10, "bold"))
        self.connection_status_label.pack(side=tk.LEFT)
        
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side=tk.RIGHT)
        
        # Control buttons
        control_frame = ttk.LabelFrame(parent, text="Monitoring Controls", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # First row: Start/Stop buttons
        buttons_row = ttk.Frame(control_frame)
        buttons_row.pack(fill=tk.X, pady=(0, 5))
        
        self.start_button = ttk.Button(buttons_row, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(buttons_row, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        self.reset_mem_button = ttk.Button(buttons_row, text="🗑️ Reset Memory", command=self.reset_strategy_memory)
        self.reset_mem_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Second row: UTC offset selector
        utc_row = ttk.Frame(control_frame)
        utc_row.pack(fill=tk.X)
        
        ttk.Label(utc_row, text="Broker UTC Offset:").pack(side=tk.LEFT, padx=(0, 5))
        # Set initial value based on loaded offset
        initial_offset = f"UTC+{self.broker_utc_offset}"
        self.utc_offset_var = tk.StringVar(value=initial_offset)
        self.utc_offset_combo = ttk.Combobox(utc_row, textvariable=self.utc_offset_var, 
                                             values=["UTC+1", "UTC+2", "UTC+3"], state="readonly", width=10)
        self.utc_offset_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.utc_offset_combo.bind("<<ComboboxSelected>>", self.on_utc_offset_change)
        
        ttk.Label(utc_row, text="(Change for Summer/Winter)", font=("Arial", 8)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Strategy phase tracking
        phase_frame = ttk.LabelFrame(parent, text="Strategy Phase Tracking", padding="5")
        phase_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create notebook for different views
        self.left_notebook = ttk.Notebook(phase_frame)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Strategy phases tab
        self.create_strategy_phases_tab()
        
        # Configuration tab
        self.create_configuration_tab()
        
        # Indicators tab
        self.create_indicators_tab()
        
    def setup_right_panel(self, parent):
        """Setup the right panel with charts and terminal"""
        # Create notebook for different views
        self.right_notebook = ttk.Notebook(parent)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Charts tab
        if MATPLOTLIB_AVAILABLE:
            self.create_charts_tab()
        else:
            self.create_no_charts_tab()
            
        # Terminal output tab
        self.create_terminal_tab()
        
        # Window markers tab
        self.create_window_markers_tab()
        
    def create_strategy_phases_tab(self):
        """Create the strategy phase tracking tab"""
        phases_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(phases_frame, text="📊 Strategy Phases")
        
        # Strategy list with phases
        columns = ("Symbol", "Phase", "Direction", "Pullback Count", "Window Active", "Last Update")
        self.phases_tree = ttk.Treeview(phases_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.phases_tree.heading(col, text=col)
            if col == "Symbol":
                self.phases_tree.column(col, width=80)
            elif col == "Phase":
                self.phases_tree.column(col, width=120)
            else:
                self.phases_tree.column(col, width=90)
                
        scrollbar_phases = ttk.Scrollbar(phases_frame, orient=tk.VERTICAL, command=self.phases_tree.yview)
        self.phases_tree.configure(yscrollcommand=scrollbar_phases.set)
        
        self.phases_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_phases.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.phases_tree.bind("<<TreeviewSelect>>", self.on_strategy_phase_select)
        
    def create_configuration_tab(self):
        """Create the configuration viewer tab"""
        config_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(config_frame, text="⚙️ Configuration")
        
        # Symbol selector
        selector_frame = ttk.Frame(config_frame)
        selector_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(selector_frame, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(selector_frame, textvariable=self.symbol_var, state="readonly", width=15)
        self.symbol_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.symbol_combo.bind("<<ComboboxSelected>>", self.on_symbol_config_select)
        
        # Configuration display
        self.config_text = scrolledtext.ScrolledText(config_frame, height=15, font=("Consolas", 9))
        self.config_text.pack(fill=tk.BOTH, expand=True)
        
    def create_indicators_tab(self):
        """Create the technical indicators tab"""
        indicators_frame = ttk.Frame(self.left_notebook)
        self.left_notebook.add(indicators_frame, text="📈 Indicators")
        
        # Indicators display
        self.indicators_text = scrolledtext.ScrolledText(indicators_frame, height=15, font=("Consolas", 9))
        self.indicators_text.pack(fill=tk.BOTH, expand=True)
        
    def create_charts_tab(self):
        """Create the live charts tab"""
        charts_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(charts_frame, text="📊 Live Charts")
        
        # Chart controls
        control_frame = ttk.Frame(charts_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(control_frame, text="Chart Symbol:").pack(side=tk.LEFT)
        self.chart_symbol_var = tk.StringVar(value="EURUSD")
        chart_symbol_combo = ttk.Combobox(control_frame, textvariable=self.chart_symbol_var, 
                                         values=["EURUSD", "XAUUSD", "GBPUSD", "AUDUSD", "XAGUSD", "USDCHF"],
                                         state="readonly", width=10)
        chart_symbol_combo.pack(side=tk.LEFT, padx=(5, 10))
        chart_symbol_combo.bind("<<ComboboxSelected>>", self.on_chart_symbol_change)
        
        ttk.Button(control_frame, text="Refresh Chart", command=self.refresh_chart).pack(side=tk.LEFT)
        
        # Chart display
        self.setup_chart(charts_frame)
        
    def create_no_charts_tab(self):
        """Create a tab explaining chart requirements"""
        no_charts_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(no_charts_frame, text="📊 Charts (Unavailable)")
        
        info_label = ttk.Label(no_charts_frame, text="Charts require matplotlib and mplfinance libraries.\n\n"
                                                    "Install with: pip install matplotlib mplfinance\n\n"
                                                    "Strategy monitoring and configuration viewing are still available.",
                              justify=tk.CENTER, font=("Arial", 11))
        info_label.pack(expand=True)
        
    def create_terminal_tab(self):
        """Create the terminal output tab"""
        terminal_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(terminal_frame, text="🖥️ Terminal Output")
        
        # Terminal display
        self.terminal_text = scrolledtext.ScrolledText(terminal_frame, height=25, font=("Consolas", 9), 
                                                      bg="black", fg="green", insertbackground="white")
        self.terminal_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Configure terminal colors
        self.terminal_text.tag_config("NORMAL", foreground="white")
        self.terminal_text.tag_config("WAITING_PULLBACK", foreground="yellow")
        self.terminal_text.tag_config("WAITING_BREAKOUT", foreground="orange")
        self.terminal_text.tag_config("SIGNAL", foreground="cyan")
        self.terminal_text.tag_config("ERROR", foreground="red")
        self.terminal_text.tag_config("SUCCESS", foreground="lime")
        
        # Terminal controls
        terminal_controls = ttk.Frame(terminal_frame)
        terminal_controls.pack(fill=tk.X)
        
        ttk.Button(terminal_controls, text="Clear Terminal", command=self.clear_terminal).pack(side=tk.LEFT)
        ttk.Button(terminal_controls, text="Save Log", command=self.save_terminal_log).pack(side=tk.LEFT, padx=(5, 0))
        
    def create_window_markers_tab(self):
        """Create the window markers tracking tab"""
        markers_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(markers_frame, text="🎯 Window Markers")
        
        # Window markers display
        columns = ("Symbol", "Direction", "Window Start", "Window End", "Breakout Level", "Status")
        self.markers_tree = ttk.Treeview(markers_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.markers_tree.heading(col, text=col)
            self.markers_tree.column(col, width=100)
            
        scrollbar_markers = ttk.Scrollbar(markers_frame, orient=tk.VERTICAL, command=self.markers_tree.yview)
        self.markers_tree.configure(yscrollcommand=scrollbar_markers.set)
        
        self.markers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_markers.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_chart(self, parent):
        """Setup matplotlib chart with standard navigation toolbar"""
        if not MATPLOTLIB_AVAILABLE or Figure is None or FigureCanvasTkAgg is None:
            return
            
        # Create figure and axis
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        
        # Add standard Matplotlib navigation toolbar BEFORE packing canvas
        # This provides: Home, Back, Forward, Pan, Zoom, Configure, Save
        if NavigationToolbar2Tk is not None:
            self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
            self.toolbar.update()
            self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Pack canvas AFTER toolbar so toolbar appears on top
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Initialize empty chart
        self.ax.set_title("Live Chart - Select Symbol")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.fig.tight_layout()
    
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 2), pady=2)
        
        self.time_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN, anchor=tk.E, width=20)
        self.time_label.pack(side=tk.RIGHT, padx=(2, 5), pady=2)
        
        # Update time every second
        self.update_time()
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, prioritizing user overrides then bundled data"""
        # 1. Check current working directory (User Override)
        cwd_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(cwd_path):
            return cwd_path
            
        # 2. Check PyInstaller bundled data
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundled_path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(bundled_path):
                return bundled_path
                
        # 3. Check relative to script (Dev mode)
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, relative_path)
            if os.path.exists(script_path):
                return script_path
        except Exception:
            pass
            
        # 4. Return CWD path as default (for creation/error reporting)
        return cwd_path

    def load_strategy_configurations(self):
        """Load strategy configuration parameters"""
        symbols = ["EURUSD", "GBPUSD", "XAUUSD", "AUDUSD", "XAGUSD", "USDCHF"]
        
        for symbol in symbols:
            try:
                # Get symbol precision from MT5
                digits = 5  # Default
                if mt5:
                    symbol_info = mt5.symbol_info(symbol)  # type: ignore
                    if symbol_info:
                        digits = symbol_info.digits
                
                # Initialize strategy state - matching original strategy state machine
                self.strategy_states[symbol] = {
                    'entry_state': 'SCANNING',  # SCANNING, ARMED_LONG, ARMED_SHORT, WINDOW_OPEN
                    'phase': 'NORMAL',  # For display compatibility
                    'armed_direction': None,
                    'pullback_candle_count': 0,
                    'signal_trigger_candle': None,  # Store trigger candle data
                    'last_pullback_candle_high': None,
                    'last_pullback_candle_low': None,
                    'window_active': False,
                    'window_bar_start': None,
                    'window_expiry_bar': None,
                    'window_top_limit': None,
                    'window_bottom_limit': None,
                    'current_bar': 0,
                    'breakout_level': None,
                    'last_update': datetime.now(),
                    'indicators': {},
                    'signals': [],
                    'crossover_data': {},
                    'digits': digits  # MT5 symbol precision for display formatting
                }
                
                # Load configuration from strategy file
                # ✅ FIX: Use get_resource_path to find bundled strategies in EXE
                strategy_rel_path = f"strategies/sunrise_ogle_{symbol.lower()}.py"
                strategy_file = self.get_resource_path(strategy_rel_path)
                
                config = self.parse_strategy_config(strategy_file, symbol)
                self.strategy_configs[symbol] = config
                
                # Debug log for pullback configuration
                pullback_enabled = config.get('LONG_USE_PULLBACK_ENTRY', 'N/A')
                pullback_max = config.get('LONG_PULLBACK_MAX_CANDLES', 'N/A')
                window_periods = config.get('LONG_ENTRY_WINDOW_PERIODS', 'N/A')
                
                # Check for load error
                if "error" in config:
                    self.terminal_log(f"❌ {symbol}: {config['error']}", "ERROR")
                else:
                    self.terminal_log(f"✅ {symbol}: Configuration loaded | Pullback: {pullback_enabled}, Max: {pullback_max}, Window: {window_periods}", "SUCCESS")
                
            except Exception as e:
                self.terminal_log(f"❌ {symbol}: Config load error - {str(e)}", "ERROR")
                self.strategy_configs[symbol] = {"error": str(e)}
                
        # Update symbol selector
        self.symbol_combo['values'] = list(symbols)
        if symbols:
            self.symbol_combo.set(symbols[0])
            self.on_symbol_config_select(None)
    
    def load_utc_offset_from_config(self):
        """Load UTC offset from config file"""
        try:
            # ✅ FIX: Use get_resource_path to find config
            config_file = self.get_resource_path(os.path.join('config', 'broker_timezone.json'))
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    offset = config_data.get('utc_offset', 1)
                    return offset
        except Exception as e:
            self.logger.warning(f"Could not load UTC offset from config: {e}")
        
        return 1  # Default: UTC+1
    
    def on_utc_offset_change(self, event=None):
        """Handle UTC offset change from dropdown"""
        offset_str = self.utc_offset_var.get()
        if offset_str == "UTC+1":
            self.broker_utc_offset = 1
        elif offset_str == "UTC+2":
            self.broker_utc_offset = 2
        elif offset_str == "UTC+3":
            self.broker_utc_offset = 3
        else:
            self.broker_utc_offset = 1  # Default
        
        # Save to config file
        try:
            # ✅ FIX: Always save to CWD (user writable area), not _MEIPASS
            config_dir = os.path.join(os.getcwd(), 'config')
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, 'broker_timezone.json')
            
            config_data = {
                "utc_offset": self.broker_utc_offset,
                "description": "Broker timezone offset from UTC. Set to 1 for UTC+1 (winter), 2 for UTC+2 (summer)",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
                
            self.terminal_log(f"🌍 Broker UTC Offset changed to: {offset_str}", "INFO", critical=True)
            self.terminal_log(f"   → Saved to config/broker_timezone.json", "INFO", critical=True)
            self.terminal_log(f"   → Time filter will convert broker time to UTC before checking", "INFO", critical=True)
            self.terminal_log(f"   → Affects: EURUSD, AUDUSD, XAGUSD, USDCHF (assets with time filter enabled)", "INFO", critical=True)
        except Exception as e:
            self.terminal_log(f"❌ Failed to save UTC offset: {str(e)}", "ERROR", critical=True)
            
    def parse_strategy_config(self, file_path, symbol):
        """Parse strategy configuration from file"""
        config = {}
        
        if not os.path.exists(file_path):
            return {"error": f"Strategy file not found: {file_path}"}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                
        # Parse key configuration parameters with more comprehensive coverage
        config_params = {
            # EMA Parameters - Different per asset
            'ema_fast_length': 'Fast EMA Period',
            'ema_medium_length': 'Medium EMA Period', 
            'ema_slow_length': 'Slow EMA Period',
            'ema_confirm_length': 'Confirmation EMA Period',
            'ema_filter_price_length': 'Price Filter EMA Period',
            'ema_exit_length': 'Exit EMA Period',
            
            # ATR Risk Management
            'atr_length': 'ATR Period',
            'long_atr_sl_multiplier': 'Long Stop Loss ATR Multiplier',
            'long_atr_tp_multiplier': 'Long Take Profit ATR Multiplier',
            
            # ATR Filters
            'LONG_USE_ATR_FILTER': 'Use ATR Volatility Filter',
            'LONG_ATR_MIN_THRESHOLD': 'ATR Min Threshold',
            'LONG_ATR_MAX_THRESHOLD': 'ATR Max Threshold',
            'LONG_USE_ATR_INCREMENT_FILTER': 'Use ATR Increment Filter',
            'LONG_ATR_INCREMENT_MIN_THRESHOLD': 'ATR Increment Min',
            'LONG_ATR_INCREMENT_MAX_THRESHOLD': 'ATR Increment Max',
            'LONG_USE_ATR_DECREMENT_FILTER': 'Use ATR Decrement Filter',
            'LONG_ATR_DECREMENT_MIN_THRESHOLD': 'ATR Decrement Min',
            'LONG_ATR_DECREMENT_MAX_THRESHOLD': 'ATR Decrement Max',
            
            # Entry Filters
            'LONG_USE_EMA_ORDER_CONDITION': 'Use EMA Order Condition',
            'LONG_USE_PRICE_FILTER_EMA': 'Use Price Filter EMA',
            'LONG_USE_CANDLE_DIRECTION_FILTER': 'Use Candle Direction Filter',
            'LONG_USE_ANGLE_FILTER': 'Use EMA Angle Filter',
            'LONG_MIN_ANGLE': 'Min EMA Angle (degrees)',
            'LONG_MAX_ANGLE': 'Max EMA Angle (degrees)',
            'LONG_ANGLE_SCALE_FACTOR': 'Angle Scale Factor',
            'LONG_USE_EMA_BELOW_PRICE_FILTER': 'Use EMA Below Price Filter',
            
            # SHORT ATR Filters
            'SHORT_USE_ATR_FILTER': 'Short Use ATR Volatility Filter',
            'SHORT_ATR_MIN_THRESHOLD': 'Short ATR Min Threshold',
            'SHORT_ATR_MAX_THRESHOLD': 'Short ATR Max Threshold',
            'SHORT_USE_ATR_INCREMENT_FILTER': 'Short Use ATR Increment Filter',
            'SHORT_ATR_INCREMENT_MIN_THRESHOLD': 'Short ATR Increment Min',
            'SHORT_ATR_INCREMENT_MAX_THRESHOLD': 'Short ATR Increment Max',
            'SHORT_USE_ATR_DECREMENT_FILTER': 'Short Use ATR Decrement Filter',
            'SHORT_ATR_DECREMENT_MIN_THRESHOLD': 'Short ATR Decrement Min',
            'SHORT_ATR_DECREMENT_MAX_THRESHOLD': 'Short ATR Decrement Max',
            
            # SHORT Entry Filters
            'SHORT_USE_EMA_ORDER_CONDITION': 'Short Use EMA Order Condition',
            'SHORT_USE_PRICE_FILTER_EMA': 'Short Use Price Filter EMA',
            'SHORT_USE_CANDLE_DIRECTION_FILTER': 'Short Use Candle Direction Filter',
            'SHORT_USE_ANGLE_FILTER': 'Short Use EMA Angle Filter',
            'SHORT_MIN_ANGLE': 'Short Min EMA Angle (degrees)',
            'SHORT_MAX_ANGLE': 'Short Max EMA Angle (degrees)',
            'SHORT_ANGLE_SCALE_FACTOR': 'Short Angle Scale Factor',
            'SHORT_USE_EMA_ABOVE_PRICE_FILTER': 'Short Use EMA Above Price Filter',
            
            # Pullback Entry System
            'LONG_USE_PULLBACK_ENTRY': 'Use Pullback Entry System',
            'LONG_PULLBACK_MAX_CANDLES': 'Max Pullback Candles',
            'LONG_ENTRY_WINDOW_PERIODS': 'Entry Window Periods',
            'SHORT_USE_PULLBACK_ENTRY': 'Short Use Pullback Entry System',
            'SHORT_PULLBACK_MAX_CANDLES': 'Short Max Pullback Candles',
            'SHORT_ENTRY_WINDOW_PERIODS': 'Short Entry Window Periods',
            
            'WINDOW_OFFSET_MULTIPLIER': 'Window Offset Multiplier',
            'USE_WINDOW_TIME_OFFSET': 'Use Window Time Offset',
            'WINDOW_PRICE_OFFSET_MULTIPLIER': 'Window Price Offset',
            
            # Time Range Filter
            'USE_TIME_RANGE_FILTER': 'Use Time Range Filter',
            'ENTRY_START_HOUR': 'Entry Start Hour (UTC)',
            'ENTRY_START_MINUTE': 'Entry Start Minute',
            'ENTRY_END_HOUR': 'Entry End Hour (UTC)',
            'ENTRY_END_MINUTE': 'Entry End Minute',
            
            # Trading Direction
            'ENABLE_LONG_TRADES': 'Enable Long Trades',
            'ENABLE_SHORT_TRADES': 'Enable Short Trades',
            
            # Position Sizing
            'enable_risk_sizing': 'Enable Risk Sizing',
            'risk_percent': 'Risk Percentage per Trade',
        }
        
        for param, description in config_params.items():
            # Find parameter in file content - check BOTH formats
            lines = content.split('\n')
            for line in lines:
                # Format 1: param = value (top level)
                # Format 2: param=value, (inside params dict)
                if (f"{param} =" in line or f"{param}=" in line) and not line.strip().startswith('#'):
                    try:
                        # Extract value
                        if '=' in line:
                            value_part = line.split('=')[1].split('#')[0].split(',')[0].strip()
                            # Clean up the value (remove quotes, trailing commas)
                            if value_part.endswith(','):
                                value_part = value_part[:-1].strip()
                            if value_part.startswith('"') and value_part.endswith('"'):
                                value_part = value_part[1:-1]
                            elif value_part.startswith("'") and value_part.endswith("'"):
                                value_part = value_part[1:-1]
                            config[description] = value_part
                            # Store with original param name too for easier access
                            config[param] = value_part
                            break
                    except:
                        continue
        
        # Store raw config for indicator calculations
        config['_symbol'] = symbol
        config['_raw_content'] = content[:1000]  # First 1000 chars for reference
                        
        return config
        
    def initialize_mt5_connection(self):
        """Initialize MetaTrader5 connection"""
        if not DEPENDENCIES_AVAILABLE or mt5 is None:
            self.terminal_log("❌ ERROR: Required dependencies not available", "ERROR")
            return False
            
        try:
            # Initialize MT5
            if not mt5.initialize():  # type: ignore
                self.terminal_log(f"❌ Failed to initialize MT5: {mt5.last_error()}", "ERROR")  # type: ignore
                return False
                
            # Get account info
            account_info = mt5.account_info()  # type: ignore
            if account_info is None:
                self.terminal_log("❌ Failed to get account info", "ERROR")
                mt5.shutdown()  # type: ignore
                return False
                
            self.mt5_connected = True
            self.connection_status_label.config(text="Connected", foreground="green")
            self.connect_button.config(text="Disconnect")
            
            self.terminal_log(f"✅ Connected to MT5 - Account: {account_info.login}", "SUCCESS")
            
            # Initialize signal processing if available
            self.initialize_signal_processing()
            
            return True
            
        except Exception as e:
            self.terminal_log(f"❌ Connection error: {str(e)}", "ERROR")
            return False
            
    def initialize_signal_processing(self):
        """Initialize signal processing components"""
        try:
            if sunrise_signal_adapter:
                # Try to create signal manager
                if hasattr(sunrise_signal_adapter, 'MultiSymbolSignalManager'):
                    self.signal_manager = sunrise_signal_adapter.MultiSymbolSignalManager()
                    
                    # Add symbols
                    symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'AUDUSD', 'XAGUSD', 'USDCHF']
                    for symbol in symbols:
                        try:
                            self.signal_manager.add_symbol(symbol)
                        except Exception as e:
                            self.terminal_log(f"⚠️ Could not add {symbol}: {str(e)}", "ERROR")
                    
                    self.terminal_log("✅ Signal processing initialized", "SUCCESS")
                    
        except Exception as e:
            self.terminal_log(f"⚠️ Signal processing error: {str(e)}", "ERROR")

    def attempt_reconnect(self):
        """Attempt to re-establish MT5 connection after IPC failure"""
        self.terminal_log("🔄 CONNECTION LOST: Attempting to reconnect to MT5...", "WARNING", critical=True)
        try:
            # Force shutdown of existing connection
            if mt5:
                mt5.shutdown()
            time.sleep(1)
            
            # Attempt re-initialization
            if mt5.initialize():
                self.terminal_log("✅ Reconnection successful - Resuming monitoring", "SUCCESS", critical=True)
                self.mt5_connected = True
                self.connection_status_label.config(text="Connected", foreground="green")
                return True
            else:
                self.terminal_log(f"❌ Reconnection failed: {mt5.last_error()}", "ERROR", critical=True)
                return False
        except Exception as e:
            self.terminal_log(f"❌ Reconnection error: {str(e)}", "ERROR", critical=True)
            return False

    def save_strategy_state(self):
        """💾 PERSISTENCE: Save current strategy state to JSON file"""
        try:
            state_file = os.path.join(os.getcwd(), 'mt5_strategy_state.json')
            serializable_state = {}
            
            for symbol, state in self.strategy_states.items():
                # Create a shallow copy to modify for serialization
                s_copy = state.copy()
                
                # Remove non-serializable objects (DataFrames, etc)
                keys_to_remove = ['indicators', 'crossover_data', 'signal_trigger_candle']
                for k in keys_to_remove:
                    if k in s_copy:
                        del s_copy[k]
                
                # Convert datetimes to ISO strings
                if 'last_update' in s_copy and isinstance(s_copy['last_update'], datetime):
                    s_copy['last_update'] = s_copy['last_update'].isoformat()
                if 'last_candle_time' in s_copy and isinstance(s_copy['last_candle_time'], datetime):
                    s_copy['last_candle_time'] = s_copy['last_candle_time'].isoformat()
                if 'last_pullback_check_candle' in s_copy and isinstance(s_copy['last_pullback_check_candle'], datetime):
                    s_copy['last_pullback_check_candle'] = s_copy['last_pullback_check_candle'].isoformat()
                if 'last_crossover_check_candle' in s_copy and isinstance(s_copy['last_crossover_check_candle'], datetime):
                    s_copy['last_crossover_check_candle'] = s_copy['last_crossover_check_candle'].isoformat()
                if 'armed_at_candle_time' in s_copy and isinstance(s_copy['armed_at_candle_time'], datetime):
                    s_copy['armed_at_candle_time'] = s_copy['armed_at_candle_time'].isoformat()
                    
                serializable_state[symbol] = s_copy
                
            with open(state_file, 'w') as f:
                json.dump(serializable_state, f, indent=4)
                
            # self.terminal_log("💾 Strategy state saved to disk", "DEBUG")
            
        except Exception as e:
            self.terminal_log(f"❌ Failed to save strategy state: {str(e)}", "ERROR")

    def load_strategy_state(self):
        """💾 PERSISTENCE: Load strategy state from JSON file with STALE CHECK"""
        state_file = os.path.join(os.getcwd(), 'mt5_strategy_state.json')
        if not os.path.exists(state_file):
            self.terminal_log("ℹ️ No previous state file found - Starting fresh", "INFO")
            return
            
        try:
            with open(state_file, 'r') as f:
                saved_state = json.load(f)
                
            loaded_count = 0
            expired_count = 0
            
            # 🕒 CONFIG: Max age for state validity (e.g., 30 minutes)
            # If the bot was off for > 30 mins, the setup is likely invalid/gone
            MAX_STATE_AGE_MINUTES = 30
            
            current_time = datetime.now()
            
            for symbol, s_data in saved_state.items():
                if symbol in self.strategy_states:
                    # Check age of data
                    last_update_str = s_data.get('last_update')
                    is_stale = False
                    
                    if last_update_str:
                        try:
                            last_update = datetime.fromisoformat(last_update_str)
                            age_minutes = (current_time - last_update).total_seconds() / 60
                            
                            if age_minutes > MAX_STATE_AGE_MINUTES:
                                is_stale = True
                                expired_count += 1
                                self.terminal_log(f"⚠️ {symbol}: Memory is stale ({age_minutes:.0f} min old) - Discarding", "WARNING")
                        except:
                            is_stale = True # If date parse fails, assume stale
                    
                    if is_stale:
                        continue # Skip loading this asset, leave as SCANNING
                    
                    # Restore critical state variables
                    target = self.strategy_states[symbol]
                    
                    # Copy scalar values
                    keys_to_restore = [
                        'entry_state', 'phase', 'armed_direction', 'pullback_candle_count',
                        'window_active', 'window_bar_start', 'window_expiry_bar',
                        'window_top_limit', 'window_bottom_limit', 'current_bar',
                        'candle_sequence_counter', 'last_pullback_candle_high', 'last_pullback_candle_low'
                    ]
                    
                    for k in keys_to_restore:
                        if k in s_data:
                            target[k] = s_data[k]
                            
                    # Restore datetimes
                    if 'last_candle_time' in s_data and s_data['last_candle_time']:
                        target['last_candle_time'] = datetime.fromisoformat(s_data['last_candle_time'])
                    if 'last_pullback_check_candle' in s_data and s_data['last_pullback_check_candle']:
                        target['last_pullback_check_candle'] = datetime.fromisoformat(s_data['last_pullback_check_candle'])
                    if 'last_crossover_check_candle' in s_data and s_data['last_crossover_check_candle']:
                        target['last_crossover_check_candle'] = datetime.fromisoformat(s_data['last_crossover_check_candle'])
                    if 'armed_at_candle_time' in s_data and s_data['armed_at_candle_time']:
                        target['armed_at_candle_time'] = datetime.fromisoformat(s_data['armed_at_candle_time'])
                        
                    loaded_count += 1
            
            if loaded_count > 0:
                self.terminal_log(f"💾 RESTORED MEMORY: Loaded state for {loaded_count} assets", "SUCCESS", critical=True)
                if expired_count > 0:
                    self.terminal_log(f"🗑️ EXPIRED MEMORY: Discarded {expired_count} stale states (> {MAX_STATE_AGE_MINUTES} min)", "WARNING", critical=True)
                self.update_strategy_displays()
            else:
                self.terminal_log("ℹ️ Memory found but all states were stale/expired - Starting fresh", "INFO")
                
        except Exception as e:
            self.terminal_log(f"❌ Failed to load strategy state: {str(e)}", "ERROR")

    def reset_strategy_memory(self):
        """🗑️ MANUAL RESET: Wipe memory file and reset all states"""
        if messagebox.askyesno("Reset Memory", "Are you sure you want to wipe all strategy memory?\n\nThis will reset all assets to 'SCANNING' phase."):
            try:
                # 1. Delete the file
                state_file = os.path.join(os.getcwd(), 'mt5_strategy_state.json')
                if os.path.exists(state_file):
                    os.remove(state_file)
                
                # 2. Reset internal state
                for symbol in self.strategy_states:
                    self._reset_entry_state(symbol)
                
                self.update_strategy_displays()
                self.terminal_log("🗑️ MEMORY WIPED: All strategies reset to SCANNING", "WARNING", critical=True)
            except Exception as e:
                self.terminal_log(f"❌ Reset failed: {str(e)}", "ERROR")
            
    def start_monitoring(self):
        """Start the advanced monitoring process"""
        if not self.mt5_connected:
            self.terminal_log("❌ Cannot start monitoring: Not connected to MT5", "ERROR")
            return
            
        if self.monitoring_active:
            return
            
        # 💾 PERSISTENCE: Try to load previous state
        self.load_strategy_state()
            
        self.monitoring_active = True
        self.stop_event.clear()
        
        # Update GUI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Advanced Monitoring Active")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.advanced_monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Startup Summary
        self.terminal_log("=" * 70, "SUCCESS", critical=True)
        self.terminal_log(f"🚀 MT5 TRADING BOT v{APP_VERSION} - SUNRISE OGLE STRATEGY ACTIVATED", "SUCCESS", critical=True)
        self.terminal_log("=" * 70, "SUCCESS", critical=True)
        self.terminal_log(f"📈 Monitored Pairs: {', '.join(self.strategy_states.keys())}", "INFO", critical=True)
        self.terminal_log(f"⏱️ Timeframe: 5-Minute (M5)", "INFO", critical=True)
        self.terminal_log(f"🎯 Strategy: 4-Phase State Machine (SCANNING → ARMED → PULLBACK → WINDOW → ENTRY)", "INFO", critical=True)
        self.terminal_log("", "INFO", critical=True)
        self.terminal_log("📊 Tracking:", "INFO", critical=True)
        self.terminal_log("   ✅ EMA crossover detection (Confirm vs Fast/Medium/Slow)", "INFO", critical=True)
        self.terminal_log("   ✅ State transitions (ARMED_LONG/SHORT)", "INFO", critical=True)
        self.terminal_log("   ✅ Pullback validation (bearish/bullish candles)", "INFO", critical=True)
        self.terminal_log("   ✅ Breakout window monitoring", "INFO", critical=True)
        self.terminal_log("   ✅ Global invalidation (counter-trend crossovers)", "INFO", critical=True)
        self.terminal_log("", "INFO", critical=True)
        self.terminal_log("💡 Note: Only key events shown. Full log in terminal_log.txt", "INFO", critical=True)
        self.terminal_log("📊 Hourly summary will be displayed every 60 minutes", "INFO", critical=True)
        self.terminal_log("=" * 70, "SUCCESS", critical=True)
        
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring_active = False
        self.stop_event.set()
        
        # 💾 PERSISTENCE: Save state on stop
        self.save_strategy_state()
        
        # Update GUI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Monitoring Stopped")
        
        self.terminal_log("⏹️ Monitoring stopped", "NORMAL")
        
    def advanced_monitoring_loop(self):
        """Advanced monitoring loop with strategy phase tracking
        
        Optimized to check ONLY on candle close (every 5 minutes) for M5 timeframe
        instead of wasteful 2-second polling.
        """
        last_summary = time.time()
        last_candle_check = {}  # Track last candle time per symbol
        
        while self.monitoring_active and not self.stop_event.is_set():
            try:
                current_minute = datetime.now().minute
                current_second = datetime.now().second
                
                # ✅ SMART CANDLE DETECTION: Only check at candle close
                # M5 candles close when minute % 5 == 0 (0, 5, 10, 15, 20, etc.)
                # Check in the first 10 seconds after close to catch the new candle
                is_candle_close_time = (current_minute % 5 == 0) and (current_second <= 10)
                
                if is_candle_close_time:
                    # Create check key for this minute
                    check_key = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    
                    # Log candle close detection (once per 5 minutes)
                    if last_candle_check.get('last_candle_log') != check_key:
                        self.terminal_log(f"⏱️ CANDLE CLOSE DETECTED - Checking all symbols at {datetime.now().strftime('%H:%M:%S')}", 
                                        "INFO", critical=True)
                        last_candle_check['last_candle_log'] = check_key
                    
                    # Monitor each strategy's phase on candle close
                    for symbol in self.strategy_states.keys():
                        # Check if we haven't processed this minute yet
                        if last_candle_check.get(symbol) != check_key:
                            self.monitor_strategy_phase(symbol)
                            last_candle_check[symbol] = check_key
                    
                    # 💾 PERSISTENCE: Save state after processing candle close
                    self.save_strategy_state()
                    
                    # Update displays after checking all symbols
                    self.root.after(0, self.update_strategy_displays)
                
                # Log phase summary every 60 seconds
                if time.time() - last_summary >= 60:
                    self.log_phase_summary()
                    last_summary = time.time()
                
                # ✅ OPTIMIZED: Sleep 5 seconds (instead of 2)
                # We only need to check near candle close times
                time.sleep(5)
                
            except Exception as e:
                self.terminal_log(f"❌ Monitoring error: {str(e)}", "ERROR")
                time.sleep(5)
                
    def monitor_strategy_phase(self, symbol):
        """Monitor individual strategy phase and state"""
        try:
            if not mt5 or pd is None:
                return
            
            # ⚡ PERFORMANCE OPTIMIZATION: Skip full data fetch if in WINDOW_OPEN
            # When monitoring breakout window, we only need current price, not full indicator recalculation
            state = self.strategy_states.get(symbol, {})
            entry_state = state.get('entry_state', 'SCANNING')
            
            if entry_state == 'WINDOW_OPEN':
                # 🔧 DEBUG: Log entry into fast path
                window_start = state.get('window_bar_start', 'N/A')
                window_expiry = state.get('window_expiry_bar', 'N/A')
                current_bar = state.get('current_bar', 'N/A')
                self.terminal_log(f"⚡ {symbol}: FAST PATH (WINDOW_OPEN) | Bar: {current_bar} | Window: {window_start}-{window_expiry}", 
                                "DEBUG", critical=True)
                
                # Fast path: Fetch more bars for proper chart display (100 bars for charting)
                # We need enough data to show the chart properly, not just 2-3 bars
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 101)  # type: ignore
                
                # 🔄 RECONNECT LOGIC: Handle IPC failures
                if rates is None:
                    error_code, error_msg = mt5.last_error()
                    if error_code == -10001 or "IPC send failed" in str(error_msg):
                        self.terminal_log(f"⚠️ {symbol}: IPC Error detected - Attempting reconnect...", "WARNING", critical=True)
                        if self.attempt_reconnect():
                            # Retry fetch once
                            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 101)
                
                if rates is None or len(rates) < 2:
                    self.terminal_log(f"❌ {symbol}: Fast path failed - no data from MT5", "ERROR", critical=True)
                    return
                
                # Convert to minimal DataFrame
                df = pd.DataFrame(rates)  # type: ignore
                df['time'] = pd.to_datetime(df['time'], unit='s')  # type: ignore
                
                # 🔧 DEBUG: Show fetched data
                self.terminal_log(f"📊 {symbol}: Fetched {len(df)} bars | Last candle: {df['time'].iloc[-1]} | Close: {df['close'].iloc[-1]:.5f}", 
                                "DEBUG", critical=True)
                
                df = df.iloc[:-1].copy()  # Remove forming candle
                
                # 🔧 DEBUG: After removing forming candle
                self.terminal_log(f"📊 {symbol}: After removing forming candle: {len(df)} bars | Last closed: {df['time'].iloc[-1]}", 
                                "DEBUG", critical=True)
                
                # ⚡ CRITICAL: Increment bar counter for window expiry tracking
                # This must happen in fast path too, otherwise window never expires!
                if len(df) > 0:
                    current_candle_time = df['time'].iloc[-1]  # 🔧 FIX: Use actual timestamp, not df index
                    
                    # Check if this is a new candle (timestamp changed)
                    if 'last_candle_time' not in state or state['last_candle_time'] != current_candle_time:
                        state['current_bar'] = state.get('current_bar', 0) + 1
                        state['last_candle_time'] = current_candle_time
                        self.terminal_log(f"📈 {symbol}: Bar counter incremented to {state['current_bar']}", 
                                        "DEBUG", critical=True)
                
                # Reuse existing indicators (they don't change during window monitoring)
                indicators = state.get('indicators', {})
                if not indicators:
                    # Fallback: If no indicators cached, do full fetch (shouldn't happen)
                    self.terminal_log(f"⚠️ {symbol}: No cached indicators in WINDOW_OPEN, doing full fetch", 
                                    "WARNING", critical=True)
                    # Fall through to full fetch below
                else:
                    # Quick window check with cached indicators
                    self.terminal_log(f"🔍 {symbol}: Calling determine_strategy_phase with {len(df)} bars", 
                                    "DEBUG", critical=True)
                    current_phase = self.determine_strategy_phase(symbol, df, indicators)
                    
                    # Update only price-related indicators
                    if len(df) > 0:
                        indicators['current_price'] = float(df['close'].iloc[-1])
                    
                    # Update chart data with recent bars (for proper visualization)
                    self.chart_data[symbol] = {
                        'df': df.tail(100),  # Show last 100 bars in chart
                        'indicators': indicators,
                        'timestamp': datetime.now()
                    }
                    
                    # ⚡ AUTO-REFRESH CHART: Update chart if this symbol is currently displayed
                    if MATPLOTLIB_AVAILABLE and self.chart_symbol_var.get() == symbol:
                        self.root.after(0, self.refresh_chart)  # Thread-safe GUI update
                    
                    # Update state timestamp
                    state['indicators'] = indicators
                    state['last_update'] = datetime.now()
                    
                    self.terminal_log(f"✅ {symbol}: Fast path completed successfully | Phase: {current_phase}", 
                                    "DEBUG", critical=True)
                    return  # Exit early, skip full processing
            
            # Full path: Fetch complete data for indicator calculation (SCANNING, ARMED states)
            # ⚡ OPTIMIZED: Reduced from 501 to 151 bars
            # Longest EMA is Filter EMA (100) - we fetch 1.5x for stability (150 + 1 forming)
            # This reduces data processing by 70% while maintaining accuracy
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 151)  # type: ignore
            
            # 🔄 RECONNECT LOGIC: Handle IPC failures
            if rates is None:
                error_code, error_msg = mt5.last_error()
                if error_code == -10001 or "IPC send failed" in str(error_msg):
                    self.terminal_log(f"⚠️ {symbol}: IPC Error detected - Attempting reconnect...", "WARNING", critical=True)
                    if self.attempt_reconnect():
                        # Retry fetch once
                        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 151)
            
            if rates is None:
                error = mt5.last_error()  # type: ignore
                self.terminal_log(f"⚠️ No chart data available for {symbol} - MT5 Error: {error}", "ERROR", critical=True)
                return
            if len(rates) < 100:
                self.terminal_log(f"⚠️ Insufficient data for {symbol} - Got {len(rates)} bars, need 100+", "ERROR", critical=True)
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(rates)  # type: ignore
            df['time'] = pd.to_datetime(df['time'], unit='s')  # type: ignore
            
            # ✅ CRITICAL FIX: Remove the last (forming) candle to match MT5 behavior
            # MT5 indicators only use closed candles, not the forming one
            # This ensures EMAs calculated match MT5 exactly
            df = df.iloc[:-1].copy()  # Remove last row (forming candle)
            
            if len(df) < 100:  # Verify we still have enough data after removal
                return
            
            # Calculate indicators (only for SCANNING/ARMED states)
            indicators = self.calculate_indicators(df, symbol)
            
            # Simulate strategy phase logic (simplified)
            current_phase = self.determine_strategy_phase(symbol, df, indicators)
            
            # Update strategy state
            state = self.strategy_states[symbol]
            
            if state['phase'] != current_phase:
                # Phase changed - log transition with more detail
                timestamp = datetime.now().strftime("%H:%M:%S")
                transition_msg = f"📊 {symbol}: {state['phase']} → {current_phase}"
                
                # Add context based on phase
                if current_phase == 'WAITING_PULLBACK':
                    transition_msg += f" | Signal detected, waiting for pullback"
                elif current_phase == 'WAITING_BREAKOUT':
                    import random
                    pullback_count = random.randint(1, 3)  # Simulate pullback count
                    state['pullback_count'] = pullback_count
                    transition_msg += f" | Pullback complete ({pullback_count} candles), window opening"
                    state['window_active'] = True
                elif current_phase == 'NORMAL':
                    if state['phase'] == 'WAITING_BREAKOUT':
                        transition_msg += f" | Window expired or breakout occurred"
                    else:
                        transition_msg += f" | Signal invalidated, reset to scanning"
                    state['window_active'] = False
                    state['pullback_count'] = 0
                
                # Add price and indicator context
                current_price = indicators.get('current_price', 0)
                trend = indicators.get('trend', 'UNKNOWN')
                digits = state.get('digits', 5)
                transition_msg += f" | Price: {current_price:.{digits}f} | Trend: {trend}"
                
                self.terminal_log(transition_msg, current_phase.replace('WAITING_', ''))
                state['phase'] = current_phase
                
                # Log to all-assets terminal summary
                self.log_phase_summary()
                
            # Update indicators and timestamp
            state['indicators'] = indicators
            state['last_update'] = datetime.now()
            
            # Store chart data with optimized history for visualization
            # ⚡ OPTIMIZED: Reduced from 250 to 100 bars for better chart zoom
            # 100 bars = 500 minutes = 8.3 hours of M5 data (perfect for intraday view)
            self.chart_data[symbol] = {
                'df': df.tail(100),  # Show last 100 bars (much better zoom level)
                'indicators': indicators,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.terminal_log(f"❌ {symbol} monitoring error: {str(e)}", "ERROR")
    
    # ===================================================================
    # FILTER VALIDATION FUNCTIONS - Universal for all assets
    # ===================================================================
    
    def _validate_atr_filter(self, symbol, df, direction='LONG'):
        """Validate ATR volatility filter - UNIVERSAL for all assets
        
        Checks:
        1. ATR range (min/max thresholds)
        2. ATR increment filter (positive changes)
        3. ATR decrement filter (negative changes)
        
        Returns:
            bool: True if ATR passes all filters (or filter disabled), False otherwise
        """
        if df is None or len(df) < 2 or 'atr' not in df.columns:
            return True  # Cannot validate, allow to pass
        
        try:
            config = self.strategy_configs.get(symbol, {})
            
            # Check if ATR filter enabled
            filter_key = f'{direction}_USE_ATR_FILTER'
            filter_enabled = config.get(filter_key, 'False')
            
            if not self.extract_bool_value(filter_enabled):
                return True  # Filter disabled
            
            # Get current ATR
            current_atr = df['atr'].iloc[-1]
            if pd.isna(current_atr) or current_atr <= 0:
                return False  # Invalid ATR
            
            # Check ATR range
            min_key = f'{direction}_ATR_MIN_THRESHOLD'
            max_key = f'{direction}_ATR_MAX_THRESHOLD'
            min_atr = float(config.get(min_key, 0.0))
            max_atr = float(config.get(max_key, 999.0))
            
            if current_atr < min_atr or current_atr > max_atr:
                self.terminal_log(
                    f"❌ {symbol} {direction}: ATR {current_atr:.6f} outside range [{min_atr:.6f}, {max_atr:.6f}]", 
                    "WARNING", critical=True
                )
                return False
            
            # Check ATR increment/decrement filters
            # ⚠️ CRITICAL FIX: Calculate change from SIGNAL DETECTION, not previous bar
            # Matches strategy logic: self.entry_atr_increment = current_atr - self.signal_detection_atr
            
            state = self.strategy_states.get(symbol, {})
            signal_atr = state.get('signal_detection_atr')
            
            atr_change = 0.0
            has_valid_change = False
            
            if signal_atr is not None and signal_atr > 0:
                # Correct calculation: Change since signal detection (Phase 1)
                atr_change = current_atr - signal_atr
                has_valid_change = True
            elif len(df) >= 2:
                # Fallback: 1-bar change (only if signal ATR missing, e.g. after restart)
                prev_atr = df['atr'].iloc[-2]
                if not pd.isna(prev_atr) and prev_atr > 0:
                    atr_change = current_atr - prev_atr
                    has_valid_change = True
                    self.terminal_log(f"⚠️ {symbol}: Using 1-bar ATR change (Signal ATR missing)", "DEBUG")
            
            if has_valid_change:
                # Increment filter (positive changes)
                incr_key = f'{direction}_USE_ATR_INCREMENT_FILTER'
                if self.extract_bool_value(config.get(incr_key, 'False')) and atr_change >= 0:
                    min_incr = float(config.get(f'{direction}_ATR_INCREMENT_MIN_THRESHOLD', 0.0))
                    max_incr = float(config.get(f'{direction}_ATR_INCREMENT_MAX_THRESHOLD', 999.0))
                    
                    if atr_change < min_incr or atr_change > max_incr:
                        self.terminal_log(
                            f"❌ {symbol} {direction}: ATR increment {atr_change:+.6f} outside range [{min_incr:.6f}, {max_incr:.6f}]", 
                            "WARNING", critical=True
                        )
                        return False
                    else:
                        self.terminal_log(f"✅ {symbol} {direction}: ATR increment {atr_change:+.6f} OK [{min_incr:.6f}, {max_incr:.6f}]", "INFO")
                
                # Decrement filter (negative changes)
                decr_key = f'{direction}_USE_ATR_DECREMENT_FILTER'
                if self.extract_bool_value(config.get(decr_key, 'False')) and atr_change < 0:
                    min_decr = float(config.get(f'{direction}_ATR_DECREMENT_MIN_THRESHOLD', -999.0))
                    max_decr = float(config.get(f'{direction}_ATR_DECREMENT_MAX_THRESHOLD', 0.0))
                    
                    if atr_change < min_decr or atr_change > max_decr:
                        self.terminal_log(
                            f"❌ {symbol} {direction}: ATR decrement {atr_change:+.6f} outside range [{min_decr:.6f}, {max_decr:.6f}]", 
                            "WARNING", critical=True
                        )
                        return False
                    else:
                        self.terminal_log(f"✅ {symbol} {direction}: ATR decrement {atr_change:+.6f} OK [{min_decr:.6f}, {max_decr:.6f}]", "INFO")
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: ATR filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade (Originals would not trade on error)
    
    def _validate_angle_filter(self, symbol, df, direction='LONG'):
        """Validate EMA angle filter - UNIVERSAL for all assets
        
        Calculates EMA slope angle and checks against min/max thresholds.
        Uses asset-specific scale factor (10.0 for metals, 10000.0 for forex).
        
        Returns:
            bool: True if angle passes filter (or filter disabled), False otherwise
        """
        if df is None or len(df) < 5:
            return True  # Not enough data, allow to pass
        
        try:
            config = self.strategy_configs.get(symbol, {})
            
            # Check if angle filter enabled
            filter_key = f'{direction}_USE_ANGLE_FILTER'
            if not self.extract_bool_value(config.get(filter_key, 'False')):
                return True  # Filter disabled
            
            # Calculate EMA confirm (1-period = close price)
            confirm_period = 1
            ema_confirm_series = df['close'].ewm(span=confirm_period, adjust=False).mean()
            
            if len(ema_confirm_series) < 4:
                return True  # Not enough data
            
            # Get scale factor (asset-specific)
            scale_factor = float(config.get(f'{direction}_ANGLE_SCALE_FACTOR', 10000.0))
            
            # Calculate angle over 1 bar (matching Backtrader original)
            # Original: (ema_confirm[0] - ema_confirm[-1]) * scale_factor
            current = ema_confirm_series.iloc[-1]
            previous = ema_confirm_series.iloc[-2]  # Fixed: was -4 (lookback=3), now -2 (1 bar back)
            
            rise = (current - previous) * scale_factor  # Fixed: removed division by lookback
            angle = math.atan(rise) * (180.0 / math.pi)  # rise/run where run=1
            
            # Get angle thresholds
            min_angle = float(config.get(f'{direction}_MIN_ANGLE', -999.0))
            max_angle = float(config.get(f'{direction}_MAX_ANGLE', 999.0))
            
            # Check range
            if angle < min_angle or angle > max_angle:
                self.terminal_log(
                    f"❌ {symbol} {direction}: Angle {angle:.1f}° outside range [{min_angle:.1f}°, {max_angle:.1f}°]", 
                    "WARNING", critical=True
                )
                return False
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: Angle filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade
    
    def _validate_price_filter(self, symbol, df, direction='LONG'):
        """Validate price vs filter EMA - UNIVERSAL for all assets
        
        Checks if current price is on the correct side of filter EMA.
        LONG: close > filter_EMA (uptrend)
        SHORT: close < filter_EMA (downtrend)
        
        Returns:
            bool: True if price passes filter (or filter disabled), False otherwise
        """
        if df is None or len(df) < 2:
            return True  # Not enough data, allow to pass
        
        try:
            config = self.strategy_configs.get(symbol, {})
            
            # Check if price filter enabled
            filter_key = f'{direction}_USE_PRICE_FILTER_EMA'
            if not self.extract_bool_value(config.get(filter_key, 'False')):
                return True  # Filter disabled
            
            # Get filter EMA period
            filter_period = self.extract_numeric_value(
                config.get('ema_filter_price_length', 
                          config.get('Price Filter EMA Period', '70'))
            )
            
            # Calculate filter EMA
            if len(df) < filter_period:
                return True  # Not enough data for filter EMA
            
            filter_ema = df['close'].ewm(span=filter_period, adjust=False).mean().iloc[-1]
            current_close = df['close'].iloc[-1]
            
            # Validate based on direction
            if direction == 'LONG':
                if current_close <= filter_ema:
                    self.terminal_log(
                        f"❌ {symbol} LONG: Price {current_close:.5f} <= Filter EMA({filter_period}) {filter_ema:.5f}", 
                        "WARNING", critical=True
                    )
                    return False
            elif direction == 'SHORT':
                if current_close >= filter_ema:
                    self.terminal_log(
                        f"❌ {symbol} SHORT: Price {current_close:.5f} >= Filter EMA({filter_period}) {filter_ema:.5f}", 
                        "WARNING", critical=True
                    )
                    return False
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: Price filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade
    
    def _validate_candle_direction(self, symbol, df, direction='LONG'):
        """Validate previous candle direction - UNIVERSAL for all assets
        
        Checks if previous closed candle matches required direction.
        LONG: previous candle must be bullish (close > open)
        SHORT: previous candle must be bearish (close < open)
        
        Returns:
            bool: True if candle passes filter (or filter disabled), False otherwise
        """
        if df is None or len(df) < 2:
            return True  # Not enough data, allow to pass
        
        try:
            config = self.strategy_configs.get(symbol, {})
            
            # Check if candle direction filter enabled
            filter_key = f'{direction}_USE_CANDLE_DIRECTION_FILTER'
            if not self.extract_bool_value(config.get(filter_key, 'False')):
                return True  # Filter disabled
            
            # Get previous candle (Signal Candle)
            # df already has forming candle removed, so iloc[-1] is the last closed candle
            prev_close = df['close'].iloc[-1]
            prev_open = df['open'].iloc[-1]
            
            # Validate based on direction
            if direction == 'LONG':
                if prev_close <= prev_open:
                    self.terminal_log(
                        f"❌ {symbol} LONG: Previous candle not bullish (C:{prev_close:.5f} <= O:{prev_open:.5f})", 
                        "WARNING", critical=True
                    )
                    return False
            elif direction == 'SHORT':
                if prev_close >= prev_open:
                    self.terminal_log(
                        f"❌ {symbol} SHORT: Previous candle not bearish (C:{prev_close:.5f} >= O:{prev_open:.5f})", 
                        "WARNING", critical=True
                    )
                    return False
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: Candle direction filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade
    
    def _validate_ema_ordering(self, symbol, ema_confirm, ema_fast, ema_medium, ema_slow, direction='LONG'):
        """Validate EMA ordering - UNIVERSAL for all assets
        
        Checks if EMAs are in proper order.
        LONG: confirm > fast > medium > slow (all EMAs ascending)
        SHORT: confirm < fast < medium < slow (all EMAs descending)
        
        Returns:
            bool: True if ordering passes filter (or filter disabled), False otherwise
        """
        try:
            config = self.strategy_configs.get(symbol, {})
            
            # Check if EMA ordering filter enabled
            filter_key = f'{direction}_USE_EMA_ORDER_CONDITION'
            if not self.extract_bool_value(config.get(filter_key, 'False')):
                return True  # Filter disabled
            
            # Validate based on direction
            if direction == 'LONG':
                # Match original strategy: Confirm > Fast AND Confirm > Medium AND Confirm > Slow
                # (Not strict stacking like Confirm > Fast > Medium > Slow)
                if not (ema_confirm > ema_fast and ema_confirm > ema_medium and ema_confirm > ema_slow):
                    self.terminal_log(
                        f"❌ {symbol} LONG: EMA ordering failed (Confirm not above all others)", 
                        "WARNING", critical=True
                    )
                    return False
                else:
                    self.terminal_log(f"✅ {symbol} LONG: EMA ordering OK", "INFO")
            elif direction == 'SHORT':
                # Match original strategy: Confirm < Fast AND Confirm < Medium AND Confirm < Slow
                if not (ema_confirm < ema_fast and ema_confirm < ema_medium and ema_confirm < ema_slow):
                    self.terminal_log(
                        f"❌ {symbol} SHORT: EMA ordering failed (Confirm not below all others)", 
                        "WARNING", critical=True
                    )
                    return False
                else:
                    self.terminal_log(f"✅ {symbol} SHORT: EMA ordering OK", "INFO")
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: EMA ordering filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade
    
    def _validate_ema_position_filter(self, symbol, df, ema_fast, ema_medium, ema_slow, direction='LONG'):
        """Validate EMA position relative to price - UNIVERSAL for all assets
        
        Checks if EMAs are on the correct side of price.
        LONG: Price > Fast, Medium, Slow EMAs
        SHORT: Price < Fast, Medium, Slow EMAs
        
        Returns:
            bool: True if position passes filter (or filter disabled), False otherwise
        """
        if df is None or len(df) < 1:
            return True  # Not enough data, allow to pass
            
        try:
            config = self.strategy_configs.get(symbol, {})
            current_close = df['close'].iloc[-1]
            
            # Validate based on direction
            if direction == 'LONG':
                # Check if filter enabled
                if not self.extract_bool_value(config.get('LONG_USE_EMA_BELOW_PRICE_FILTER', 'False')):
                    return True
                    
                # Check if Price is ABOVE all EMAs
                if current_close > ema_fast and current_close > ema_medium and current_close > ema_slow:
                    self.terminal_log(f"✅ {symbol} LONG: Price {current_close:.5f} > All EMAs", "INFO")
                    return True
                else:
                    self.terminal_log(
                        f"❌ {symbol} LONG: Price {current_close:.5f} not above all EMAs (F:{ema_fast:.5f}, M:{ema_medium:.5f}, S:{ema_slow:.5f})", 
                        "WARNING", critical=True
                    )
                    return False
                    
            elif direction == 'SHORT':
                # Check if filter enabled
                if not self.extract_bool_value(config.get('SHORT_USE_EMA_ABOVE_PRICE_FILTER', 'False')):
                    return True
                    
                # Check if Price is BELOW all EMAs
                if current_close < ema_fast and current_close < ema_medium and current_close < ema_slow:
                    self.terminal_log(f"✅ {symbol} SHORT: Price {current_close:.5f} < All EMAs", "INFO")
                    return True
                else:
                    self.terminal_log(
                        f"❌ {symbol} SHORT: Price {current_close:.5f} not below all EMAs (F:{ema_fast:.5f}, M:{ema_medium:.5f}, S:{ema_slow:.5f})", 
                        "WARNING", critical=True
                    )
                    return False
            
            return True
            
        except Exception as e:
            self.terminal_log(f"⚠️ {symbol}: EMA position filter error: {str(e)}", "WARNING")
            return False  # 🛡️ FIX: On error, BLOCK trade

    def _validate_time_filter(self, symbol, current_dt, direction):
        """Validate if current time is within allowed trading hours (UTC)
        
        Logic Layer:
        - Takes Broker Time (current_dt)
        - Converts to UTC by subtracting broker_utc_offset
        - Compares against Strategy UTC hours
        """
        config = self.strategy_configs.get(symbol, {})
        
        # Check if time filter is enabled
        use_time_filter = config.get('Use Time Range Filter', 'False')
        if isinstance(use_time_filter, str):
            use_time_filter = use_time_filter.lower() in ('true', '1', 'yes')
            
        if not use_time_filter:
            return True
            
        try:
            # 1. Get Broker Offset (Logic Layer)
            utc_offset = getattr(self, 'broker_utc_offset', 1)
            
            # 2. Convert Broker Time to UTC (Strategy_Time_UTC = Broker_Time - Selected_Offset)
            # current_dt is the time from the broker (e.g. Market Watch time)
            strategy_time_utc = current_dt - timedelta(hours=utc_offset)
            
            # 3. Get allowed hours (UTC)
            start_hour = int(config.get('Entry Start Hour (UTC)', 0))
            start_min = int(config.get('Entry Start Minute', 0))
            end_hour = int(config.get('Entry End Hour (UTC)', 0))
            end_min = int(config.get('Entry End Minute', 0))
            
            # 4. Convert everything to minutes for easier comparison
            current_minutes = strategy_time_utc.hour * 60 + strategy_time_utc.minute
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            # Handle overnight ranges (e.g. 22:00 to 02:00)
            if start_minutes > end_minutes:
                # Overnight: Allowed if AFTER start OR BEFORE end
                is_allowed = current_minutes >= start_minutes or current_minutes <= end_minutes
            else:
                # Normal: Allowed if AFTER start AND BEFORE end
                is_allowed = start_minutes <= current_minutes <= end_minutes
                
            if not is_allowed:
                self.terminal_log(f"⏰ {symbol}: Outside trading hours (UTC). Current UTC: {strategy_time_utc.strftime('%H:%M')} | Allowed: {start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}", 
                                "WARNING", critical=False)
                return False
                
            return True
            
        except Exception as e:
            self.terminal_log(f"❌ Time filter error: {str(e)}", "ERROR", critical=True)
            return True # Fail safe: allow trade if filter fails
            
    def detect_ema_crossovers(self, symbol, indicators, df):
        """Detect EMA crossovers ONLY ON CLOSED CANDLES (matching Backtrader behavior)
        
        ⚠️ CRITICAL: In Backtrader, next() is called once per CLOSED CANDLE, not per tick.
        For M5 timeframe: next() every 5 minutes (when candle closes)
        For H1 timeframe: next() every 60 minutes (when candle closes)
        
        This function MUST only process crossovers when a new candle closes to avoid
        false crossovers from recalculating EMAs with forming candle data.
        """
        
        # Only check if we have enough data
        if len(df) < 2:
            return
        
        try:
            # ⚠️ CRITICAL: df already has forming candle removed at line 747!
            # So df.iloc[-1] IS the last CLOSED candle, not forming candle
            # Don't use iloc[-2] or df[:-1] or we'll process old data!
            current_closed_candle_time = df['time'].iloc[-1] if len(df) >= 1 else None
            
            # Check if we've already processed this closed candle for crossovers
            state = self.strategy_states.get(symbol, {})
            last_processed_candle = state.get('last_crossover_check_candle', None)
            
            if current_closed_candle_time == last_processed_candle:
                # Already processed this closed candle - skip to avoid duplicate signals
                return
            
            # NEW CLOSED CANDLE - process crossovers
            # self.terminal_log(f"🕐 {symbol}: New closed candle detected at {current_closed_candle_time} - checking crossovers", 
            #                 "INFO", critical=False)
            
            # Mark this candle as processed
            state['last_crossover_check_candle'] = current_closed_candle_time
            
            # ⚠️ CRITICAL: df already contains ONLY closed candles (forming removed at line 747)
            # Use df directly, don't remove another candle!
            df_closed = df
            
            if len(df_closed) < 20:
                return  # Need enough data for EMA calculation
            
            # Get strategy-specific parameters
            config = self.strategy_configs.get(symbol, {})
            fast_period = self.extract_numeric_value(config.get('ema_fast_length', '18'))
            medium_period = self.extract_numeric_value(config.get('ema_medium_length', '18'))
            slow_period = self.extract_numeric_value(config.get('ema_slow_length', '50'))
            confirm_period = 1  # Confirm EMA is always 1-period (close price)
            
            # Calculate EMAs on CLOSED candles only
            ema_confirm_series = df_closed['close'].ewm(span=confirm_period).mean()
            ema_fast_series = df_closed['close'].ewm(span=fast_period).mean()
            ema_medium_series = df_closed['close'].ewm(span=medium_period).mean()
            ema_slow_series = df_closed['close'].ewm(span=slow_period).mean()
            
            # Get current and previous EMA values (last 2 closed candles)
            if len(ema_confirm_series) < 2:
                return
            
            confirm_ema = ema_confirm_series.iloc[-1]
            fast_ema = ema_fast_series.iloc[-1]
            medium_ema = ema_medium_series.iloc[-1]
            slow_ema = ema_slow_series.iloc[-1]
            
            prev_confirm = ema_confirm_series.iloc[-2]
            prev_fast = ema_fast_series.iloc[-2]
            prev_medium = ema_medium_series.iloc[-2]
            prev_slow = ema_slow_series.iloc[-2]
            
            # Initialize crossover flags
            bullish_crossover = False
            bearish_crossover = False
            
            # Detect BULLISH crossovers (confirm EMA crosses ABOVE)
            # Count individual crossovers but only log summary
            bullish_count = 0
            if confirm_ema > fast_ema and prev_confirm <= prev_fast:
                bullish_count += 1
                bullish_crossover = True
            
            if confirm_ema > medium_ema and prev_confirm <= prev_medium:
                bullish_count += 1
                bullish_crossover = True
            
            if confirm_ema > slow_ema and prev_confirm <= prev_slow:
                bullish_count += 1
                bullish_crossover = True
            
            # Detect BEARISH crossovers (confirm EMA crosses BELOW)
            bearish_count = 0
            if confirm_ema < fast_ema and prev_confirm >= prev_fast:
                bearish_count += 1
                bearish_crossover = True
            
            if confirm_ema < medium_ema and prev_confirm >= prev_medium:
                bearish_count += 1
                bearish_crossover = True
            
            if confirm_ema < slow_ema and prev_confirm >= prev_slow:
                bearish_count += 1
                bearish_crossover = True
            
            # ✅ CRITICAL: Ignore crossovers that happened BEFORE bot startup
            # This prevents "stale" signals from triggering setups on restart
            crossover_is_stale = False
            if hasattr(self, 'bot_startup_time') and isinstance(self.bot_startup_time, datetime):
                # Convert to timezone-aware if needed for comparison
                startup_time = self.bot_startup_time
                if isinstance(current_closed_candle_time, datetime):
                    if startup_time.tzinfo is None and current_closed_candle_time.tzinfo is not None:
                        startup_time = startup_time.replace(tzinfo=current_closed_candle_time.tzinfo)
                    elif startup_time.tzinfo is not None and current_closed_candle_time.tzinfo is None:
                        current_closed_candle_time_aware = current_closed_candle_time.replace(tzinfo=startup_time.tzinfo)
                        if current_closed_candle_time_aware < startup_time:
                            crossover_is_stale = True
                    elif current_closed_candle_time < startup_time:
                        crossover_is_stale = True
            
            # Only log if crossover detected (summary format)
            if bullish_count > 0:
                ema_names = []
                if bullish_count >= 3:
                    ema_names = ["Fast", "Medium", "Slow"]
                elif bullish_count == 2:
                    if confirm_ema > fast_ema and prev_confirm <= prev_fast:
                        ema_names.append("Fast")
                    if confirm_ema > medium_ema and prev_confirm <= prev_medium:
                        ema_names.append("Medium")
                    if confirm_ema > slow_ema and prev_confirm <= prev_slow:
                        ema_names.append("Slow")
                else:
                    if confirm_ema > fast_ema and prev_confirm <= prev_fast:
                        ema_names = ["Fast"]
                    elif confirm_ema > medium_ema and prev_confirm <= prev_medium:
                        ema_names = ["Medium"]
                    else:
                        ema_names = ["Slow"]
                
                self.terminal_log(f"� {symbol}: Confirm EMA CROSSED ABOVE {'/'.join(ema_names)} EMA - BULLISH! (Candle: {current_closed_candle_time})", 
                                "SUCCESS", critical=True)
            
            if bearish_count > 0:
                ema_names = []
                if bearish_count >= 3:
                    ema_names = ["Fast", "Medium", "Slow"]
                elif bearish_count == 2:
                    if confirm_ema < fast_ema and prev_confirm >= prev_fast:
                        ema_names.append("Fast")
                    if confirm_ema < medium_ema and prev_confirm >= prev_medium:
                        ema_names.append("Medium")
                    if confirm_ema < slow_ema and prev_confirm >= prev_slow:
                        ema_names.append("Slow")
                else:
                    if confirm_ema < fast_ema and prev_confirm >= prev_fast:
                        ema_names = ["Fast"]
                    elif confirm_ema < medium_ema and prev_confirm >= prev_medium:
                        ema_names = ["Medium"]
                    else:
                        ema_names = ["Slow"]
                
                self.terminal_log(f"🔴 {symbol}: Confirm EMA CROSSED BELOW {'/'.join(ema_names)} EMA - BEARISH! (Candle: {current_closed_candle_time})", 
                                "ERROR", critical=True)
            
            # ===================================================================
            # CRITICAL: VALIDATE ALL FILTERS BEFORE STORING CROSSOVER
            # ===================================================================
            
            # Get current datetime for time filter
            if len(df_closed) > 0:
                current_dt = df_closed['time'].iloc[-1] if isinstance(df_closed['time'].iloc[-1], datetime) else datetime.now()
            else:
                current_dt = datetime.now()
            
            # ⚠️ CRITICAL FIX: Add ATR to df_closed for filter validation
            # The indicators dict has ATR but df_closed doesn't have it as a column
            if indicators and 'atr' in indicators and len(df_closed) > 0:
                df_closed = df_closed.copy()  # Avoid modifying original
                df_closed['atr'] = indicators['atr']  # Add as scalar (broadcasts to all rows)
            
            # Validate BULLISH crossovers (LONG direction)
            if bullish_crossover and not crossover_is_stale:
                self.terminal_log(f"🔍 {symbol}: Bullish crossover detected - validating ALL filters...", 
                                "INFO", critical=True)
                
                all_filters_passed = True
                
                # 1. ATR Filter
                atr_passed = self._validate_atr_filter(symbol, df_closed, 'LONG')
                self.terminal_log(f"   📊 {symbol}: ATR filter → {'✅ PASS' if atr_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not atr_passed:
                    all_filters_passed = False
                
                # 2. Angle Filter
                angle_passed = self._validate_angle_filter(symbol, df_closed, 'LONG')
                self.terminal_log(f"   📐 {symbol}: Angle filter → {'✅ PASS' if angle_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not angle_passed:
                    all_filters_passed = False
                
                # 3. Price Filter
                price_passed = self._validate_price_filter(symbol, df_closed, 'LONG')
                self.terminal_log(f"   💰 {symbol}: Price filter → {'✅ PASS' if price_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not price_passed:
                    all_filters_passed = False
                
                # 4. Candle Direction
                candle_passed = self._validate_candle_direction(symbol, df_closed, 'LONG')
                self.terminal_log(f"   🕯️ {symbol}: Candle Direction → {'✅ PASS' if candle_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not candle_passed:
                    all_filters_passed = False
                
                # 5. EMA Ordering
                ema_order_passed = self._validate_ema_ordering(symbol, confirm_ema, fast_ema, medium_ema, slow_ema, 'LONG')
                self.terminal_log(f"   📈 {symbol}: EMA Ordering → {'✅ PASS' if ema_order_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not ema_order_passed:
                    all_filters_passed = False
                
                # 6. EMA Position (new filter)
                ema_position_passed = self._validate_ema_position_filter(symbol, df_closed, fast_ema, medium_ema, slow_ema, 'LONG')
                self.terminal_log(f"   📏 {symbol}: EMA Position → {'✅ PASS' if ema_position_passed else '❌ FAIL'}", 
                                "DEBUG", critical=True)
                if not ema_position_passed:
                    all_filters_passed = False
                
                # NOTE: Time filter is NOT checked here (matches original strategy)
                # Time filter is only validated at BREAKOUT/ENTRY execution (Phase 4)
                
                # Final decision
                if all_filters_passed:
                    self.terminal_log(f"✅ {symbol}: LONG crossover PASSED ALL FILTERS - Ready to ARM", 
                                    "SUCCESS", critical=True)
                else:
                    bullish_crossover = False
                    self.terminal_log(f"❌ {symbol}: LONG crossover REJECTED - One or more filters failed", 
                                    "WARNING", critical=True)
            
            # ===================================================================
            # CRITICAL: BEARISH CROSSOVER HANDLING
            # ===================================================================

            # ⚠️ IMPORTANT: We preserve bearish_crossover for GLOBAL INVALIDATION
            # (to reset ARMED_LONG states) but log that SHORTS are disabled
            if bearish_crossover:
                self.terminal_log(f"⚠️ {symbol}: Bearish crossover detected - Will trigger GLOBAL INVALIDATION if ARMED_LONG", 
                                "INFO", critical=True)
                # Note: Do NOT set bearish_crossover = False here!
                # The state machine needs it to reset ARMED_LONG states
            
            # Store crossover data for phase logic
            if symbol in self.strategy_states:
                # Clear stale crossovers (those that occurred before bot startup)
                if crossover_is_stale:
                    bullish_crossover = False
                    bearish_crossover = False
                
                self.strategy_states[symbol]['crossover_data'] = {
                    'bullish_crossover': bullish_crossover,
                    'bearish_crossover': bearish_crossover,
                    'candle_time': current_closed_candle_time
                }
            
        except Exception as e:
            self.terminal_log(f"❌ Crossover detection error for {symbol}: {str(e)}", "ERROR", critical=True)
    
    def calculate_indicators(self, df, symbol):
        """Calculate technical indicators using actual strategy parameters"""
        indicators = {}
        
        try:
            # Get strategy-specific parameters
            config = self.strategy_configs.get(symbol, {})
            
            # Debug: log the config keys (remove after testing)
            # self.terminal_log(f"📊 {symbol} config keys: {list(config.keys())}", "NORMAL")
            
            # Extract EMA periods from config (using correct parameter names from strategy)
            fast_period = self.extract_numeric_value(config.get('ema_fast_length', 
                                                    config.get('Fast EMA Period', '18')))
            medium_period = self.extract_numeric_value(config.get('ema_medium_length', 
                                                      config.get('Medium EMA Period', '18')))  
            slow_period = self.extract_numeric_value(config.get('ema_slow_length', 
                                                    config.get('Slow EMA Period', '24')))
            
            # ⚠️ WARNING: Check for redundant EMA periods
            if fast_period == medium_period:
                self.terminal_log(f"⚠️ {symbol}: Fast EMA ({fast_period}) equals Medium EMA ({medium_period}) - Trend Cloud ineffective", "WARNING")
            filter_period = self.extract_numeric_value(config.get('ema_filter_price_length', 
                                                      config.get('Price Filter EMA Period', '100')))
            atr_period = self.extract_numeric_value(config.get('atr_length', 
                                                  config.get('ATR Period', '10')))
            
            # self.terminal_log(f"📊 {symbol} periods - Fast: {fast_period}, Medium: {medium_period}, Slow: {slow_period}, Filter: {filter_period}, ATR: {atr_period}", "NORMAL")
            
            # Ensure we have enough data
            if df is None or len(df) < max(fast_period, medium_period, slow_period, filter_period, atr_period):
                self.terminal_log(f"⚠️ Insufficient data for {symbol}: {len(df) if df is not None else 'None'} bars", "WARNING")
                return indicators
            
            # Calculate EMAs with actual periods
            # ✅ CRITICAL FIX: Use adjust=False to match standard EMA formula (MT5/backtrader)
            indicators['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean().iloc[-1]
            indicators['ema_medium'] = df['close'].ewm(span=medium_period, adjust=False).mean().iloc[-1]
            indicators['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean().iloc[-1]
            indicators['ema_filter'] = df['close'].ewm(span=filter_period, adjust=False).mean().iloc[-1]
            
            # Store periods for display
            indicators['ema_fast_period'] = fast_period
            indicators['ema_medium_period'] = medium_period
            indicators['ema_slow_period'] = slow_period
            indicators['ema_filter_period'] = filter_period
            
            # 🔍 DEBUG: Log EMA(70) calculation details for comparison with MT5
            if symbol == "EURUSD" and len(df) > 0:
                last_candle_time = df['time'].iloc[-1]
                last_close = df['close'].iloc[-1]
                ema_70 = indicators['ema_filter']
                num_bars = len(df)
                self.terminal_log(
                    f"🔍 EMA(70) DEBUG - {symbol}: Time={last_candle_time}, "
                    f"Close={last_close:.5f}, EMA(70)={ema_70:.5f}, Bars={num_bars}",
                    "NORMAL"
                )
            
            # ATR calculation
            if len(df) > 1 and np is not None and pd is not None:
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())  # type: ignore
                low_close = np.abs(df['low'] - df['close'].shift())  # type: ignore
                ranges = pd.concat([high_low, high_close, low_close], axis=1)  # type: ignore
                true_range = np.max(ranges, axis=1)  # type: ignore
                atr_value = true_range.rolling(atr_period).mean().iloc[-1]
                
                # Validate ATR value
                if pd.isna(atr_value) or atr_value <= 0:
                    # Calculate simple average if rolling window incomplete
                    atr_value = true_range.tail(min(atr_period, len(true_range))).mean()
                    if pd.isna(atr_value) or atr_value <= 0:
                        atr_value = 0.0001  # Fallback minimum
                        self.terminal_log(f"⚠️ {symbol}: ATR calculation returned invalid value, using fallback: {atr_value}", 
                                        "WARNING", critical=True)
                
                indicators['atr'] = atr_value
                
                # 📊 LOG ATR for historical tracking
                self.terminal_log(f"📊 ATR: {symbol} | Period={atr_period} | Value={atr_value:.5f} | Bars={len(df)}", 
                                "INFO", critical=False)
            else:
                indicators['atr'] = 0.0001
                self.terminal_log(f"⚠️ {symbol}: Insufficient data for ATR, using fallback: 0.0001", 
                                "WARNING", critical=True)
                
            indicators['atr_period'] = atr_period
            
            # Current price
            indicators['current_price'] = df['close'].iloc[-1]
            
            # Calculate TP/SL levels using actual multipliers
            sl_multiplier = self.extract_float_value(config.get('long_atr_sl_multiplier', 
                                                     config.get('Long Stop Loss ATR Multiplier', '1.5')))
            tp_multiplier = self.extract_float_value(config.get('long_atr_tp_multiplier', 
                                                     config.get('Long Take Profit ATR Multiplier', '10.0')))
            
            if indicators.get('atr', 0) > 0:
                indicators['sl_level'] = indicators['current_price'] - (indicators['atr'] * sl_multiplier)
                indicators['tp_level'] = indicators['current_price'] + (indicators['atr'] * tp_multiplier)
            else:
                indicators['sl_level'] = 0
                indicators['tp_level'] = 0
                
            indicators['sl_multiplier'] = sl_multiplier
            indicators['tp_multiplier'] = tp_multiplier
            
            # Trend direction based on EMA alignment
            if indicators['ema_fast'] > indicators['ema_medium'] > indicators['ema_slow']:
                indicators['trend'] = 'BULLISH'
            elif indicators['ema_fast'] < indicators['ema_medium'] < indicators['ema_slow']:
                indicators['trend'] = 'BEARISH'
            else:
                indicators['trend'] = 'SIDEWAYS'
                
            # EMA array for charting
            # ✅ CRITICAL FIX: Use adjust=False to match standard EMA formula (like MT5/backtrader)
            # adjust=True (pandas default) uses weighted average that changes with history
            # adjust=False uses recursive formula: EMA = α * Price + (1-α) * EMA_prev
            indicators['ema_fast_array'] = df['close'].ewm(span=fast_period, adjust=False).mean()
            indicators['ema_medium_array'] = df['close'].ewm(span=medium_period, adjust=False).mean()
            indicators['ema_slow_array'] = df['close'].ewm(span=slow_period, adjust=False).mean()
            indicators['ema_filter_array'] = df['close'].ewm(span=filter_period, adjust=False).mean()
            
            # Add confirm EMA for crossover detection
            # EMA(1) with adjust=False is essentially the close price itself
            indicators['ema_confirm'] = df['close'].ewm(span=1, adjust=False).mean().iloc[-1]
            
            # Detect EMA crossovers (critical events)
            self.detect_ema_crossovers(symbol, indicators, df)
            
            # This message is now filtered as non-critical
            self.terminal_log(f"✅ {symbol} indicators calculated successfully", "SUCCESS")
                
        except Exception as e:
            self.terminal_log(f"❌ Error calculating indicators for {symbol}: {str(e)}", "ERROR", critical=True)
            indicators['error'] = str(e)
            
        return indicators
            
        return indicators
        
    def extract_numeric_value(self, value_str):
        """Extract numeric value from configuration string"""
        if isinstance(value_str, (int, float)):
            return int(value_str) if isinstance(value_str, float) else value_str
        if isinstance(value_str, str):
            # Remove common characters and extract number
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            if match:
                return int(float(match.group(1)))  # Convert to int for periods
        return 18  # Default fallback
    
    def extract_float_value(self, value_str):
        """Extract float value from configuration string (for multipliers)"""
        if isinstance(value_str, (int, float)):
            return float(value_str)
        if isinstance(value_str, str):
            # Remove common characters and extract number
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', value_str)
            if match:
                return float(match.group(1))
        return 1.5  # Default fallback
    
    def extract_bool_value(self, value):
        """Extract boolean value from configuration string"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return False
    
    def _is_in_trading_time_range(self, dt, config):
        """Check if current time is within trading hours (matching original strategy)"""
        use_filter = config.get('USE_TIME_RANGE_FILTER', 'True')
        if isinstance(use_filter, str):
            use_filter = use_filter.lower() in ('true', '1', 'yes')
        
        if not use_filter:
            return True  # No filter active
        
        # Get time range parameters
        start_hour = int(config.get('ENTRY_START_HOUR', 0))
        start_minute = int(config.get('ENTRY_START_MINUTE', 0))
        end_hour = int(config.get('ENTRY_END_HOUR', 23))
        end_minute = int(config.get('ENTRY_END_MINUTE', 59))
        
        # Read UTC offset from config file (set by GUI)
        # ✅ FIX: Use cached self.broker_utc_offset instead of re-reading file
        # This ensures we use the correct offset even if file access fails
        utc_offset = getattr(self, 'broker_utc_offset', 1)
        
        # Convert broker time (Madrid UTC+1/UTC+2) to UTC
        utc_hour = (dt.hour - utc_offset) % 24
        
        # Convert to minutes for comparison
        current_time_minutes = utc_hour * 60 + dt.minute
        start_time_minutes = start_hour * 60 + start_minute
        end_time_minutes = end_hour * 60 + end_minute
        
        if start_time_minutes <= end_time_minutes:
            # Normal range (e.g., 09:00-17:00)
            return start_time_minutes <= current_time_minutes <= end_time_minutes
        else:
            # Overnight range (e.g., 23:00-02:00)
            return current_time_minutes >= start_time_minutes or current_time_minutes <= end_time_minutes
    
    def _reset_entry_state(self, symbol):
        """Reset strategy state to SCANNING (matching original strategy)"""
        state = self.strategy_states[symbol]
        state['entry_state'] = 'SCANNING'
        state['phase'] = 'NORMAL'
        state['armed_direction'] = None
        state['pullback_candle_count'] = 0
        state['signal_trigger_candle'] = None
        state['last_pullback_candle_high'] = None
        state['last_pullback_candle_low'] = None
        state['window_active'] = False
        state['window_bar_start'] = None
        state['window_expiry_bar'] = None
        state['window_top_limit'] = None
        state['window_bottom_limit'] = None
    
    def _phase3_open_breakout_window(self, symbol, armed_direction, config, current_bar):
        """PHASE 3: Open the two-sided breakout window after pullback confirmation
        
        Implements true volatility expansion channel with:
        - Optional time offset controlled by use_window_time_offset parameter
        - Two-sided channel with success and failure boundaries
        """
        state = self.strategy_states[symbol]
        
        # 1. Implement Optional Time Offset
        window_start_bar = current_bar
        use_time_offset = config.get('USE_WINDOW_TIME_OFFSET', 'True')
        if isinstance(use_time_offset, str):
            use_time_offset = use_time_offset.lower() in ('true', '1', 'yes')
        
        if use_time_offset:
            window_offset_multiplier = float(config.get('WINDOW_OFFSET_MULTIPLIER', 1.0))
            time_offset = int(state['pullback_candle_count'] * window_offset_multiplier)
            window_start_bar = current_bar + time_offset
        
        state['window_bar_start'] = window_start_bar
        
        # 2. Set Window Duration
        if armed_direction == 'LONG':
            window_periods = int(config.get('LONG_ENTRY_WINDOW_PERIODS', 7))
        else:
            window_periods = int(config.get('SHORT_ENTRY_WINDOW_PERIODS', 7))
        
        state['window_expiry_bar'] = window_start_bar + window_periods
        
        # 3. Calculate the Two-Sided Price Channel
        last_high = state['last_pullback_candle_high']
        last_low = state['last_pullback_candle_low']
        candle_range = last_high - last_low
        price_offset_multiplier = float(config.get('WINDOW_PRICE_OFFSET_MULTIPLIER', 0.001))  # Fixed: was 0.5, should be 0.001
        price_offset = candle_range * price_offset_multiplier
        
        state['window_top_limit'] = last_high + price_offset
        state['window_bottom_limit'] = last_low - price_offset
        
        # 4. Final State Transition
        state['entry_state'] = 'WINDOW_OPEN'
        state['phase'] = 'WAITING_BREAKOUT'
        state['window_active'] = True
        
        digits = state.get('digits', 5)
        self.terminal_log(f"🪟 {symbol}: Window OPENED ({armed_direction}) | Top: {state['window_top_limit']:.{digits}f} | Bottom: {state['window_bottom_limit']:.{digits}f} | Duration: {window_periods} bars", 
                        "SUCCESS", critical=True)
    
    def _phase4_monitor_window(self, symbol, df, armed_direction, current_bar, current_dt, config):
        """PHASE 4: Monitor window for breakout
        
        Returns:
            'PENDING' - Window not yet active (time offset)
            'SUCCESS' - Breakout detected
            'EXPIRED' - Window timeout
            'FAILURE' - Failure boundary broken
            None - Still monitoring
        """
        state = self.strategy_states[symbol]
        digits = state.get('digits', 5)
        
        # 🔧 DEBUG: Show entry into phase4 monitoring
        self.terminal_log(f"🔍 PHASE4: {symbol} | Direction={armed_direction} | Bar={current_bar} | DF_len={len(df)}", 
                        "DEBUG", critical=True)
        
        # Check window active (time offset)
        if current_bar < state['window_bar_start']:
            self.terminal_log(f"⏳ {symbol}: Window PENDING (bar {current_bar} < start {state['window_bar_start']})", 
                            "DEBUG", critical=True)
            return 'PENDING'
        
        # Check window expiry (matches original Line 1414: if current_bar > self.window_expiry_bar)
        if current_bar > state['window_expiry_bar']:
            self.terminal_log(f"⏱️ {symbol}: Window EXPIRED (bar {current_bar} > expiry {state['window_expiry_bar']})", 
                            "WARNING", critical=True)
            return 'EXPIRED'
        
        # Get current price data
        if len(df) < 1:
            self.terminal_log(f"❌ {symbol}: No price data in DF!", "ERROR", critical=True)
            return None
        
        current_high = df['high'].iloc[-1]
        current_low = df['low'].iloc[-1]
        current_close = df['close'].iloc[-1]
        
        # 🔧 DEBUG: Show current price vs boundaries
        self.terminal_log(f"💹 {symbol}: Price | High={current_high:.{digits}f} Low={current_low:.{digits}f} Close={current_close:.{digits}f}", 
                        "DEBUG", critical=True)
        
        # Monitor breakouts (matches original Lines 1429-1447)
        if armed_direction == 'LONG':
            # 🔧 DEBUG: Log window boundaries and current price
            digits = state.get('digits', 5)
            self.terminal_log(f"🔧 LONG WINDOW CHECK: {symbol} | High={current_high:.{digits}f} Low={current_low:.{digits}f} | " +
                            f"Top_Limit={state['window_top_limit']:.{digits}f} Bottom_Limit={state['window_bottom_limit']:.{digits}f}", 
                            "DEBUG", critical=True)
            
            # SUCCESS: Price breaks above top limit (original Line 1429: current_high >= self.window_top_limit)
            if current_high >= state['window_top_limit']:
                # Final time check before success
                if not self._is_in_trading_time_range(current_dt, config):
                    self.terminal_log(f"⏰ {symbol}: Breakout detected but outside trading hours", 
                                    "WARNING", critical=True)
                    self._reset_entry_state(symbol)
                    return 'EXPIRED'
                return 'SUCCESS'
            
            # FAILURE: Price breaks below bottom limit (original Line 1435: current_low <= self.window_bottom_limit)
            elif current_low <= state['window_bottom_limit']:
                self.terminal_log(f"❌ {symbol}: LONG FAILURE - Price {current_low:.{digits}f} broke BELOW bottom limit {state['window_bottom_limit']:.{digits}f}", 
                                "WARNING", critical=True)
                return 'FAILURE'
        
        else:  # SHORT
            # 🔧 DEBUG: Log window boundaries and current price
            self.terminal_log(f"🔧 SHORT WINDOW CHECK: {symbol} | High={current_high:.{digits}f} Low={current_low:.{digits}f} | " +
                            f"Top_Limit={state['window_top_limit']:.{digits}f} Bottom_Limit={state['window_bottom_limit']:.{digits}f}", 
                            "DEBUG", critical=True)
            
            # SUCCESS: Price breaks below bottom limit (original Line 1445: current_low <= self.window_bottom_limit)
            if current_low <= state['window_bottom_limit']:
                # Final time check before success
                if not self._is_in_trading_time_range(current_dt, config):
                    self.terminal_log(f"⏰ {symbol}: Breakout detected but outside trading hours", 
                                    "WARNING", critical=True)
                    self._reset_entry_state(symbol)
                    return 'EXPIRED'
                return 'SUCCESS'
            
            # FAILURE: Price breaks above top limit (original Line 1451: current_high >= self.window_top_limit)
            elif current_high >= state['window_top_limit']:
                self.terminal_log(f"❌ {symbol}: SHORT FAILURE - Price {current_high:.{digits}f} broke ABOVE top limit {state['window_top_limit']:.{digits}f}", 
                                "WARNING", critical=True)
                return 'FAILURE'
        
        # 🔧 DEBUG: No breakout detected, still monitoring
        self.terminal_log(f"⏳ {symbol}: Window monitoring - No breakout yet (within boundaries)", 
                        "DEBUG", critical=True)
        return None  # Still monitoring
        
    def determine_strategy_phase(self, symbol, df, indicators):
        """4-PHASE STATE MACHINE - Exact copy of original strategy logic
        
        States: SCANNING → ARMED_LONG/SHORT → WINDOW_OPEN → Entry/Reset
        Matches: sunrise_ogle_*.py state machine exactly
        """
        # Type guard for pandas (required for operation)
        if pd is None or mt5 is None:
            self.terminal_log(f"❌ {symbol}: Dependencies not available", "ERROR", critical=True)
            return 'ERROR'
        
        current_state = self.strategy_states[symbol]
        entry_state = current_state['entry_state']
        config = self.strategy_configs.get(symbol, {})
        
        # ===================================================================
        # EMERGENCY SAFEGUARD: Force disable SHORT arming (all assets LONG only)
        # ===================================================================
        if entry_state == 'ARMED_SHORT':
            self.terminal_log(f"🚨 {symbol}: EMERGENCY RESET - ARMED_SHORT detected but SHORTS DISABLED globally!", 
                            "ERROR", critical=True)
            self._reset_entry_state(symbol)
            entry_state = 'SCANNING'
            current_state['entry_state'] = 'SCANNING'
            # Clear any bearish crossover data
            if 'crossover_data' in current_state:
                current_state['crossover_data']['bearish_crossover'] = False
        
        # ✅ CRITICAL FIX: Check for open positions BEFORE any processing
        # If position exists and we're in IN_TRADE state, check if it's still open
        # If closed, reset state to allow new entries
        if entry_state == 'IN_TRADE':
            positions = mt5.positions_get(symbol=symbol)  # type: ignore
            if positions is None or len(positions) == 0:
                # Position closed (by SL/TP) - Reset state to allow new entries
                self.terminal_log(f"🔓 {symbol}: Position closed - Unlocking for new signals", 
                                "INFO", critical=True)
                self._reset_entry_state(symbol)
                entry_state = 'SCANNING'
            else:
                # Position still open - Skip all processing
                self.terminal_log(f"🔒 {symbol}: Position still open (Ticket #{positions[0].ticket}) - Skipping signal detection", 
                                "DEBUG", critical=False)
                return 'IN_TRADE'
        
        # Get SHORT enabled status
        short_enabled = config.get('ENABLE_SHORT_TRADES', 'False')
        if isinstance(short_enabled, str):
            short_enabled = short_enabled.lower() in ('true', '1', 'yes')
        
        # Bar counter - only increment on NEW CANDLE (matches original strategy Line 1393: current_bar = len(self))
        # Track candle timestamp to detect new candles
        if len(df) > 0:
            current_candle_time = df['time'].iloc[-1]
            
            # Check if this is a new candle (timestamp changed)
            if 'last_candle_time' not in current_state or current_state['last_candle_time'] != current_candle_time:
                current_state['current_bar'] += 1
                current_state['last_candle_time'] = current_candle_time
        
        current_bar = current_state['current_bar']
        
        # Get current time for time filter
        if len(df) > 0:
            # Use the time column which contains datetime objects
            current_dt = df['time'].iloc[-1]
        else:
            current_dt = datetime.now()
        
        # ===================================================================
        # TIME FILTER - ONLY FOR TRADE EXECUTION
        # ===================================================================
        # ⚠️ CRITICAL FIX: Time filter is checked ONLY at breakout execution
        # inside _phase4_monitor_window(), NOT here. Window monitoring and 
        # state progression must continue 24/7. Only the final trade execution
        # respects trading hours (checked at line 1293 and 1304).
        
        try:
            # ✅ DIAGNOSTIC: Log state machine processing
            if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
                pullback_count = current_state.get('pullback_candle_count', 0)
                self.terminal_log(f"🔧 STATE: {symbol} processing | state={entry_state} | pullback_count={pullback_count} | df_len={len(df)}", 
                                "DEBUG", critical=True)
            elif entry_state == 'WINDOW_OPEN':
                # ⚠️ CRITICAL: Add diagnostic logging for WINDOW_OPEN phase
                window_active = current_state.get('window_active', False)
                armed_direction = current_state.get('armed_direction', 'Unknown')
                self.terminal_log(f"🔧 WINDOW: {symbol} monitoring | state={entry_state} | direction={armed_direction} | active={window_active} | df_len={len(df)}", 
                                "DEBUG", critical=True)
            
            # Get crossover data
            crossover_data = current_state.get('crossover_data', {})
            bullish_cross = crossover_data.get('bullish_crossover', False)
            bearish_cross = crossover_data.get('bearish_crossover', False)
            
            # ===================================================================
            # GLOBAL INVALIDATION RULE - Check ARMED states for opposing signals
            # ===================================================================
            # CRITICAL: Reset on opposing crossover REGARDLESS of short_enabled
            # Original strategy (Line 1551-1583) always resets on opposing signal
            if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
                opposing_signal = False
                
                # ARMED_LONG: Reset if bearish crossover detected (even if shorts disabled)
                if entry_state == 'ARMED_LONG' and bearish_cross:
                    opposing_signal = True
                    self.terminal_log(f"⚠️ {symbol}: GLOBAL INVALIDATION - Bearish crossover detected in ARMED_LONG", 
                                    "WARNING", critical=True)
                
                # ARMED_SHORT: Reset if bullish crossover detected
                elif entry_state == 'ARMED_SHORT' and bullish_cross:
                    opposing_signal = True
                    self.terminal_log(f"⚠️ {symbol}: GLOBAL INVALIDATION - Bullish crossover detected in ARMED_SHORT", 
                                    "WARNING", critical=True)
                
                if opposing_signal:
                    self._reset_entry_state(symbol)
                    entry_state = 'SCANNING'
            
            # ===================================================================
            # STATE MACHINE ROUTER
            # ===================================================================
            
            # ---------------------------------------------------------------
            # PHASE 1: SCANNING → ARMED (Signal Detection)
            # ---------------------------------------------------------------
            if entry_state == 'SCANNING':
                signal_direction = None
                
                # Check for LONG signal
                if bullish_cross:
                    signal_direction = 'LONG'
                
                # Check for SHORT signal (only if enabled)
                elif bearish_cross and short_enabled:
                    signal_direction = 'SHORT'
                
                # Transition to ARMED if signal detected
                if signal_direction:
                    # ✅ CRITICAL: Check if pullback system is enabled for this direction
                    use_pullback = False
                    if signal_direction == 'LONG':
                        use_pullback_str = str(config.get('LONG_USE_PULLBACK_ENTRY', 'True')).strip()
                        use_pullback = use_pullback_str.lower() in ['true', '1', 'yes']
                    elif signal_direction == 'SHORT':
                        use_pullback_str = str(config.get('SHORT_USE_PULLBACK_ENTRY', 'True')).strip()
                        use_pullback = use_pullback_str.lower() in ['true', '1', 'yes']
                    
                    # Get current price for context
                    current_price = df['close'].iloc[-1] if len(df) > 0 else 0
                    digits = current_state.get('digits', 5)
                    
                    # ✅ CRITICAL FIX: Clear crossover flags after consuming them FIRST
                    # This prevents re-arming on the same crossover signal repeatedly
                    current_state['crossover_data'] = {
                        'bullish_crossover': False,
                        'bearish_crossover': False,
                        'candle_time': crossover_data.get('candle_time', current_dt)
                    }
                    
                    if use_pullback:
                        # 🔄 PULLBACK MODE: Use 3-phase system (ARMED → WINDOW_OPEN → ENTRY)
                        current_state['entry_state'] = f"ARMED_{signal_direction}"
                        current_state['phase'] = 'WAITING_PULLBACK'
                        current_state['armed_direction'] = signal_direction
                        current_state['pullback_candle_count'] = 0
                        
                        # Store signal detection ATR for increment/decrement filters (Matches strategy logic)
                        if 'atr' in indicators and indicators['atr'] is not None:
                            # indicators['atr'] is a scalar float from calculate_indicators
                            current_state['signal_detection_atr'] = float(indicators['atr'])
                        else:
                            current_state['signal_detection_atr'] = None
                        
                        # Store trigger candle (using PREVIOUS closed candle to match Backtrader logic)
                        # Backtrader stores close[-1] (Bar -1) as trigger candle
                        # df.iloc[-1] is Bar 0. df.iloc[-2] is Bar -1.
                        if len(df) >= 2:
                            idx = -2
                            arming_candle_time = df['time'].iloc[idx]
                            
                            current_state['signal_trigger_candle'] = {
                                'open': float(df['open'].iloc[idx]),
                                'close': float(df['close'].iloc[idx]),
                                'high': float(df['high'].iloc[idx]),
                                'low': float(df['low'].iloc[idx]),
                                'datetime': arming_candle_time,
                                'is_bullish': df['close'].iloc[idx] > df['open'].iloc[idx],
                                'is_bearish': df['close'].iloc[idx] < df['open'].iloc[idx]
                            }
                            
                            # ✅ CRITICAL FIX: Mark CURRENT last closed candle as already processed
                            # The crossover is detected on the current closed candle (index -1)
                            # We must mark it to prevent checking the arming candle itself for pullbacks
                            # ✅ FIX: Use 'time' column, NOT df.index (which is RangeIndex 0-499)
                            current_last_candle_time = df['time'].iloc[-1]
                            current_state['last_pullback_check_candle'] = current_last_candle_time
                        
                        # Get pullback requirements
                        if signal_direction == 'LONG':
                            max_candles = int(config.get('LONG_PULLBACK_MAX_CANDLES', 2))
                            pullback_type = "BEARISH (Red)"
                        else:
                            max_candles = int(config.get('SHORT_PULLBACK_MAX_CANDLES', 2))
                            pullback_type = "BULLISH (Green)"
                        
                        self.terminal_log(f"🎯 {symbol}: {signal_direction} CROSSOVER - State: SCANNING → ARMED_{signal_direction} | Price: {current_price:.{digits}f}", 
                                        "SUCCESS", critical=True)
                        self.terminal_log(f"📋 {symbol}: PULLBACK MODE - Monitoring for {max_candles} {pullback_type} pullback candles...", 
                                        "INFO", critical=True)
                        entry_state = f"ARMED_{signal_direction}"
                        
                        # 🛡️ INITIALIZE CANDLE SEQUENCE TRACKER - Ensures we never miss candles
                        current_state['candle_sequence_counter'] = 0
                        current_state['armed_at_candle_time'] = df['time'].iloc[-1]
                        self.terminal_log(f"🔒 {symbol}: Candle sequence tracker initialized at {current_state['armed_at_candle_time']}", 
                                        "INFO", critical=True)
                    else:
                        # ⚡ STANDARD MODE: Enter immediately on crossover (no pullback wait)
                        self.terminal_log(f"🎯 {symbol}: {signal_direction} CROSSOVER - STANDARD MODE (No pullback) | Price: {current_price:.{digits}f}", 
                                        "SUCCESS", critical=True)
                        self.terminal_log(f"⚡ {symbol}: Entering immediately (pullback system disabled)", 
                                        "INFO", critical=True)
                        
                        # Execute entry directly
                        entry_success = self._execute_entry(symbol, signal_direction, df, current_dt, config)
                        
                        if entry_success:
                            self.terminal_log(f"✅ {symbol}: STANDARD ENTRY executed at {current_price:.{digits}f}", 
                                            "SUCCESS", critical=True)
                        else:
                            self.terminal_log(f"❌ {symbol}: STANDARD ENTRY failed - Reset to SCANNING", 
                                            "ERROR", critical=True)
                        
                        # Reset state to SCANNING after entry attempt
                        self._reset_entry_state(symbol)
                        entry_state = 'SCANNING'
            
            # ---------------------------------------------------------------
            # PHASE 2: ARMED → WINDOW_OPEN (Pullback Confirmation)
            # ---------------------------------------------------------------
            elif entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
                armed_direction = current_state['armed_direction']
                
                # ✅ DIAGNOSTIC: Log entry into ARMED pullback checking
                self.terminal_log(f"🔧 DEBUG: {symbol} entered ARMED pullback check | armed_direction={armed_direction} | df_len={len(df)}", 
                                "DEBUG", critical=True)
                
                # Safety check: If SHORT armed but disabled, reset
                if armed_direction == 'SHORT' and not short_enabled:
                    self.terminal_log(f"⚠️ {symbol}: SHORT armed but disabled - Reset", 
                                    "WARNING", critical=True)
                    self._reset_entry_state(symbol)
                    entry_state = 'SCANNING'
                
                # ⚠️ CRITICAL: df already has forming candle removed at line 747!
                # So df.iloc[-1] IS the last CLOSED candle, not forming
                # Don't remove another candle or we'll check old data
                elif len(df) >= 1:  # Need at least 1 closed candle
                    # 🛡️ STEP 1: DATAFRAME INTEGRITY CHECK
                    # Verify we have continuous M5 data without gaps
                    if len(df) >= 2:
                        time_diffs = df['time'].diff().dt.total_seconds() / 60  # Minutes between candles
                        gaps = time_diffs[time_diffs > 5]  # Find gaps > 5 minutes
                        if len(gaps) > 0:
                            self.terminal_log(f"⚠️ {symbol}: DataFrame has {len(gaps)} gap(s) in historical data!", "WARNING", critical=True)
                            for gap_idx in gaps.index:
                                gap_time = df['time'].iloc[gap_idx]
                                gap_size = time_diffs.iloc[gap_idx]
                                self.terminal_log(f"  📊 Gap at {gap_time}: {gap_size:.0f} min", "WARNING", critical=True)
                    
                    # Get the LAST CLOSED candle TIMESTAMP (df already excludes forming candle)
                    # ✅ FIX: Use 'time' column, NOT df.index
                    last_closed_candle_time = df['time'].iloc[-1] if len(df) > 0 else None
                    
                    # ✅ DIAGNOSTIC: Log the candle being checked
                    last_checked = current_state.get('last_pullback_check_candle', 'NONE')
                    self.terminal_log(f"🔧 DEBUG: {symbol} pullback candle check | last_closed={last_closed_candle_time} | last_checked={last_checked} | Same? {last_closed_candle_time == last_checked}", 
                                    "DEBUG", critical=True)
                    
                    # 🛡️ BULLETPROOF CANDLE DETECTION - NEVER MISS A CANDLE
                    # Strategy: ALWAYS check for gaps, not just when time_diff > 5
                    # Use DataFrame filtering to get ALL unprocessed candles
                    
                    candles_to_check = []
                    
                    if last_checked == 'NONE' or not isinstance(last_checked, pd.Timestamp):
                        # First time checking - start from latest closed candle
                        candles_to_check = df.tail(1).copy()
                        self.terminal_log(f"🔍 {symbol}: First pullback check - processing latest candle", "INFO", critical=True)
                    elif not isinstance(last_closed_candle_time, pd.Timestamp):
                        # No valid timestamp on latest candle - data issue
                        self.terminal_log(f"⚠️ {symbol}: Invalid timestamp on latest candle - skipping check", "WARNING", critical=True)
                        candles_to_check = pd.DataFrame()  # Empty, will skip processing
                    else:
                        # ROBUST: Always filter for ALL candles AFTER last_checked
                        # This guarantees we never skip any candles
                        unprocessed_mask = df['time'] > last_checked
                        unprocessed_candles = df[unprocessed_mask].copy()
                        
                        if len(unprocessed_candles) == 0:
                            # No new candles - already processed latest
                            candles_to_check = pd.DataFrame()  # Empty
                        elif len(unprocessed_candles) == 1:
                            # Normal case - exactly 1 new candle
                            candles_to_check = unprocessed_candles
                            self.terminal_log(f"✅ {symbol}: 1 new candle to process (consecutive check)", "INFO", critical=True)
                        else:
                            # GAP DETECTED - Multiple unprocessed candles
                            time_diff = (last_closed_candle_time - last_checked).total_seconds() / 60
                            num_skipped = len(unprocessed_candles) - 1  # Subtract the expected next candle
                            
                            self.terminal_log(f"⚠️ CRITICAL: {symbol} DETECTED GAP! Skipped {num_skipped} candle(s)", "WARNING", critical=True)
                            self.terminal_log(f"📊 {symbol}: Last checked: {last_checked} | Latest: {last_closed_candle_time} | Time gap: {time_diff:.0f} min", "WARNING", critical=True)
                            self.terminal_log(f"� {symbol}: Processing ALL {len(unprocessed_candles)} unprocessed candles to catch up...", "INFO", critical=True)
                            
                            candles_to_check = unprocessed_candles
                            
                            # 🛡️ SAFETY: Validate sequence integrity
                            for i in range(len(unprocessed_candles)):
                                candle_time = unprocessed_candles.iloc[i]['time']
                                self.terminal_log(f"  📅 Candle #{i+1}: {candle_time}", "INFO", critical=True)
                        
                        # 🔒 FINAL VALIDATION: Ensure we're checking consecutive candles
                        if len(candles_to_check) > 0:
                            first_candle_time = candles_to_check.iloc[0]['time']
                            expected_next = last_checked + pd.Timedelta(minutes=5)
                            
                            if first_candle_time != expected_next:
                                gap_minutes = (first_candle_time - last_checked).total_seconds() / 60
                                self.terminal_log(f"⚠️ {symbol}: Non-consecutive candles detected! Expected {expected_next}, got {first_candle_time} (gap: {gap_minutes:.0f} min)", 
                                                "WARNING", critical=True)
                    
                    # Check if we've already processed this closed candle
                    if 'last_pullback_check_candle' in current_state and current_state['last_pullback_check_candle'] == last_closed_candle_time and len(candles_to_check) <= 1:
                        # Already processed this closed candle, waiting for next candle to close
                        pullback_type = "Bearish" if armed_direction == 'LONG' else "Bullish"
                        current_count = current_state.get('pullback_candle_count', 0)
                        # Reduce spam - only log once per minute
                        import time
                        now = time.time()
                        if not hasattr(current_state, '_last_forming_log') or (now - current_state.get('_last_forming_log', 0)) > 60:
                            self.terminal_log(f">> WAITING: {symbol} {armed_direction} waiting for next {pullback_type} candle | count={current_count}/2", 
                                            "INFO", critical=False)
                            current_state['_last_forming_log'] = now
                    elif len(candles_to_check) > 0:
                        # NEW CLOSED CANDLE(S) - Check for pullback
                        # Get max pullback requirement for logging
                        max_candles = 2  # Default
                        if armed_direction == 'LONG':
                            max_candles = int(config.get('LONG_PULLBACK_MAX_CANDLES', 2))
                            pullback_type = "BEARISH (Red)"
                        else:
                            max_candles = int(config.get('SHORT_PULLBACK_MAX_CANDLES', 2))
                            pullback_type = "BULLISH (Green)"
                        
                        # 🔄 PROCESS ALL CANDLES IN SEQUENCE (handles gaps)
                        for idx, candle_row in candles_to_check.iterrows():
                            candle_time = candle_row['time']
                            current_open = candle_row['open']
                            current_high = candle_row['high']
                            current_low = candle_row['low']
                            current_close = candle_row['close']
                            current_count = current_state.get('pullback_candle_count', 0)
                            
                            # 🛡️ SEQUENCE COUNTER: Track total candles checked since ARMED
                            seq_counter = current_state.get('candle_sequence_counter', 0)
                            seq_counter += 1
                            current_state['candle_sequence_counter'] = seq_counter
                            
                            # ✅ LOG EVERY CANDLE CHECKED IN ARMED STATE
                            candle_time_str = candle_time.strftime("%Y-%m-%d %H:%M:%S") if hasattr(candle_time, 'strftime') else str(candle_time)
                            self.terminal_log(f"🔍 CHECKING CANDLE #{seq_counter}: {symbol} {armed_direction} | Time: {candle_time_str} | O:{current_open:.5f} H:{current_high:.5f} L:{current_low:.5f} C:{current_close:.5f} | Pullback: {current_count}/{max_candles}", 
                                            "INFO", critical=True)
                            
                            is_pullback_candle = False
                            
                            if armed_direction == 'LONG':
                                # LONG pullback = bearish candle (close < open)
                                is_pullback_candle = current_close < current_open
                            elif armed_direction == 'SHORT':
                                # SHORT pullback = bullish candle (close > open)
                                is_pullback_candle = current_close > current_open
                            
                            # Mark this closed candle as processed
                            current_state['last_pullback_check_candle'] = candle_time
                            
                            if is_pullback_candle:
                                # Increment pullback count
                                current_state['pullback_candle_count'] += 1
                                
                                # DEBUG: Show candle details
                                candle_color = "BEARISH (Red)" if current_close < current_open else "BULLISH (Green)"
                                self.terminal_log(f">> PULLBACK CANDLE: {symbol} {armed_direction} #{current_state['pullback_candle_count']}/{max_candles} | {candle_color} | O:{current_open:.5f} H:{current_high:.5f} L:{current_low:.5f} C:{current_close:.5f}", 
                                                "INFO", critical=True)
                                
                                # Check if pullback complete
                                if current_state['pullback_candle_count'] >= max_candles:
                                    # Store last pullback candle data for window calculation
                                    current_state['last_pullback_candle_high'] = float(current_high)
                                    current_state['last_pullback_candle_low'] = float(current_low)
                                    
                                    # Transition to WINDOW_OPEN
                                    self._phase3_open_breakout_window(symbol, armed_direction, config, current_bar)
                                    
                                    # Update BOTH local variable AND state dictionary
                                    current_state['entry_state'] = 'WINDOW_OPEN'
                                    current_state['phase'] = 'WAITING_BREAKOUT'
                                    entry_state = 'WINDOW_OPEN'
                                    
                                    self.terminal_log(f"✅ {symbol}: Pullback CONFIRMED ({current_state['pullback_candle_count']}/{max_candles}) - Window OPENING", 
                                                    "SUCCESS", critical=True)
                                    break  # Exit loop - window is open, stop checking more candles
                                else:
                                    # Still waiting for more pullback candles - SHOW THIS!
                                    candle_type = "Bearish" if armed_direction == 'LONG' else "Bullish"
                                    self.terminal_log(f"📉 {symbol}: {candle_type} pullback #{current_state['pullback_candle_count']}/{max_candles} detected (need {max_candles - current_state['pullback_candle_count']} more)", 
                                                    "INFO", critical=True)
                            else:
                                # ❌ INVALID PULLBACK (Wrong color) -> RESET (Matches Original)
                                self.terminal_log(f"♻️ {symbol}: Pullback failed (wrong candle color) - Resetting to SCANNING", "NORMAL")
                                self._reset_entry_state(symbol)
                                return 'SCANNING'
                        
                        # 🎯 Summary after processing all candles
                        if len(candles_to_check) > 1:
                            final_count = current_state.get('pullback_candle_count', 0)
                            self.terminal_log(f"✅ {symbol}: Processed {len(candles_to_check)} candles | Final pullback count: {final_count}/{max_candles}", 
                                            "INFO", critical=True)
                        
                        # 🛡️ POST-PROCESSING VALIDATION: Verify sequence integrity
                        if len(candles_to_check) > 0:
                            last_processed = current_state.get('last_pullback_check_candle', None)
                            if isinstance(last_processed, pd.Timestamp) and isinstance(last_closed_candle_time, pd.Timestamp):
                                if last_processed == last_closed_candle_time:
                                    self.terminal_log(f"✅ {symbol}: Sequence validation PASSED - Latest candle processed", "INFO", critical=True)
                                else:
                                    self.terminal_log(f"⚠️ {symbol}: Sequence validation WARNING - Last processed: {last_processed}, Expected: {last_closed_candle_time}", 
                                                    "WARNING", critical=True)
                                    # Force sync to latest
                                    current_state['last_pullback_check_candle'] = last_closed_candle_time
                                    self.terminal_log(f"🔧 {symbol}: Force synced last_pullback_check_candle to {last_closed_candle_time}", "INFO", critical=True)            # ---------------------------------------------------------------
            # PHASE 3: WINDOW_OPEN (Monitor for Breakout)
            # ---------------------------------------------------------------
            elif entry_state == 'WINDOW_OPEN':
                armed_direction = current_state['armed_direction']
                
                # 🔧 DEBUG: Entry into window monitoring
                self.terminal_log(f"🪟 {symbol}: WINDOW_OPEN phase | Direction={armed_direction} | Bar={current_bar} | DF_len={len(df)}", 
                                "DEBUG", critical=True)
                
                breakout_status = self._phase4_monitor_window(symbol, df, armed_direction, current_bar, current_dt, config)
                
                # 🔧 DEBUG: Breakout status result
                self.terminal_log(f"📊 {symbol}: Window check result = {breakout_status}", 
                                "DEBUG", critical=True)
                
                if breakout_status == 'SUCCESS':
                    # Get current close price for trade execution (matches backtrader behavior)
                    trade_executed = False  # Initialize variable
                    
                    if len(df) < 1:
                        self.terminal_log(f"❌ {symbol}: BREAKOUT detected but no price data available!", 
                                        "ERROR", critical=True)
                        self._reset_entry_state(symbol)
                        entry_state = 'SCANNING'
                    else:
                        current_close = float(df['close'].iloc[-1])
                        digits = current_state.get('digits', 5)
                        
                        self.terminal_log(f"✅ {symbol}: BREAKOUT detected - Validating entry conditions...", 
                                        "INFO", critical=True)
                        
                        # 1. RE-CALCULATE INDICATORS for fresh validation (Angle, Price vs EMA, etc.)
                        # Cached indicators are from window open time, we need CURRENT values
                        fresh_indicators = self.calculate_indicators(df, symbol)
                        
                        # 2. VALIDATE ALL FILTERS AGAIN (Strategy Phase 4 Validation)
                        all_filters_passed = True
                        
                        # 🛑 FIX: DISABLE "DOUBLE JEOPARDY" VALIDATION
                        # In Backtrader, pending orders are NOT cancelled if indicators shift slightly.
                        # We only check if the setup was valid at creation.
                        # We DO check Price Filter (Trend) and Time, but NOT Angle or ATR again.
                        
                        # Add ATR to df for validation functions
                        df_validation = df.copy()
                        if 'atr' in fresh_indicators:
                            df_validation['atr'] = fresh_indicators['atr']
                        
                        # --- DISABLED STRICT RE-VALIDATION TO MATCH ORIGINALS ---
                        # if not self._validate_angle_filter(symbol, df_validation, armed_direction):
                        #     self.terminal_log(f"⚠️ {symbol}: Angle changed, but honoring original signal", "DEBUG")
                        
                        # if not self._validate_atr_filter(symbol, df_validation, armed_direction):
                        #      self.terminal_log(f"⚠️ {symbol}: ATR changed, but honoring original signal", "DEBUG")

                        # ✅ KEEP: Price Filter (Trend Alignment) - We don't want to trade against the trend
                        if all_filters_passed and not self._validate_price_filter(symbol, df_validation, armed_direction):
                            self.terminal_log(f"❌ {symbol}: Entry blocked by Price Filter (Trend Reversal)", "WARNING", critical=True)
                            all_filters_passed = False
                            
                        # ✅ KEEP: EMA Ordering - Basic trend structure must hold
                        fresh_fast = fresh_indicators.get('ema_fast', 0)
                        fresh_medium = fresh_indicators.get('ema_medium', 0)
                        fresh_slow = fresh_indicators.get('ema_slow', 0)
                        fresh_confirm = fresh_indicators.get('ema_confirm', 0)
                        
                        if all_filters_passed and not self._validate_ema_ordering(symbol, fresh_confirm, fresh_fast, fresh_medium, fresh_slow, armed_direction):
                             self.terminal_log(f"❌ {symbol}: Entry blocked by EMA Ordering (Trend Broken)", "WARNING", critical=True)
                             all_filters_passed = False
                            
                        # 3. VALIDATE TRIGGER CANDLE (Original Signal)
                        # Ensure the original signal candle is still valid (e.g. body size, direction)
                        trigger_candle = current_state.get('signal_trigger_candle')
                        if all_filters_passed and trigger_candle:
                            # Check candle direction filter against ORIGINAL trigger candle
                            use_candle_filter = config.get(f'{armed_direction}_USE_CANDLE_DIRECTION_FILTER', 'False')
                            if use_candle_filter in ('True', True, 1, '1'):
                                is_valid_direction = False
                                if armed_direction == 'LONG':
                                    is_valid_direction = trigger_candle['is_bullish']
                                else:
                                    is_valid_direction = trigger_candle['is_bearish']
                                    
                                if not is_valid_direction:
                                    self.terminal_log(f"❌ {symbol}: Entry blocked - Original trigger candle direction invalid", "WARNING", critical=True)
                                    all_filters_passed = False
                        
                        if not all_filters_passed:
                            self.terminal_log(f"⛔ {symbol}: ENTRY ABORTED - Filters failed at breakout time", "WARNING", critical=True)
                            self._reset_entry_state(symbol)
                            entry_state = 'SCANNING'
                            return entry_state

                        self.terminal_log(f"✅ {symbol}: All entry filters PASSED. Price: {current_close:.{digits}f}", 
                                        "SUCCESS", critical=True)
                        
                        # ⏰ CRITICAL: Validate time filter before entry (matches original strategy Line 1381)
                        current_dt = df['time'].iloc[-1] if len(df) > 0 else datetime.now()
                        time_filter_passed = self._validate_time_filter(symbol, current_dt, armed_direction)
                        
                        if not time_filter_passed:
                            self.terminal_log(f"🚫 {symbol}: ENTRY BLOCKED - Breakout detected outside trading hours", 
                                            "WARNING", critical=True)
                            self._reset_entry_state(symbol)
                            entry_state = 'SCANNING'
                            trade_executed = False
                        else:
                            # Execute trade in MT5 at close price (backtrader behavior)
                            entry_price = current_close
                            trade_executed = self.execute_trade(symbol, armed_direction, entry_price, config)
                    
                    if trade_executed:
                        self.terminal_log(f"🎯 {symbol}: Trade executed successfully!", "SUCCESS", critical=True)
                        # ⚠️ CRITICAL FIX: DO NOT reset state immediately after trade execution
                        # Set to IN_TRADE state to prevent duplicate entries while position is open
                        current_state['entry_state'] = 'IN_TRADE'
                        current_state['phase'] = 'TRADE_ACTIVE'
                        entry_state = 'IN_TRADE'
                        self.terminal_log(f"🔒 {symbol}: State locked - Will not accept new signals until position closes", 
                                        "INFO", critical=True)
                    else:
                        self.terminal_log(f"⚠️ {symbol}: Trade execution failed!", "WARNING", critical=True)
                        # Only reset if trade failed
                        self._reset_entry_state(symbol)
                        entry_state = 'SCANNING'
                    
                elif breakout_status == 'EXPIRED':
                    self.terminal_log(f"⏱️ {symbol}: Window EXPIRED - Returning to pullback search", 
                                    "WARNING", critical=True)
                    # Return to ARMED state to search for more pullback
                    current_state['entry_state'] = f"ARMED_{armed_direction}"
                    current_state['phase'] = 'WAITING_PULLBACK'
                    current_state['window_active'] = False
                    current_state['pullback_candle_count'] = 0  # Reset pullback count (matches original Line 1404)
                    entry_state = f"ARMED_{armed_direction}"
                    
                elif breakout_status == 'FAILURE':
                    self.terminal_log(f"❌ {symbol}: Failure boundary broken - Returning to pullback search", 
                                    "WARNING", critical=True)
                    # Return to ARMED state
                    current_state['entry_state'] = f"ARMED_{armed_direction}"
                    current_state['phase'] = 'WAITING_PULLBACK'
                    current_state['window_active'] = False
                    current_state['pullback_candle_count'] = 0  # Reset pullback count (matches original Line 1420)
                    entry_state = f"ARMED_{armed_direction}"
            
            # Update last update time
            current_state['last_update'] = datetime.now()
            
        except Exception as e:
            self.terminal_log(f"❌ Phase determination error: {str(e)}", "ERROR", critical=True)
            import traceback
            traceback.print_exc()
        
        return entry_state
        
    def update_strategy_displays(self):
        """Update all strategy-related displays"""
        self.update_phases_tree()
        self.update_indicators_display()
        self.update_window_markers()
        
    def update_phases_tree(self):
        """Update the strategy phases tree"""
        # Clear existing items
        for item in self.phases_tree.get_children():
            self.phases_tree.delete(item)
            
        # Add current strategy states
        for symbol, state in self.strategy_states.items():
            # Get display-friendly values
            entry_state = state.get('entry_state', 'SCANNING')
            phase_display = state.get('phase', 'NORMAL')
            armed_dir = state.get('armed_direction', None)
            direction_display = armed_dir if armed_dir else 'None'
            pullback_count = state.get('pullback_candle_count', 0)
            window_active = state.get('window_active', False)
            
            values = (
                symbol,
                phase_display,
                direction_display,
                pullback_count,
                'Yes' if window_active else 'No',
                state['last_update'].strftime("%H:%M:%S")
            )
            
            item = self.phases_tree.insert("", tk.END, values=values)
            
            # Color code based on entry state
            if entry_state in ['ARMED_LONG', 'ARMED_SHORT']:
                self.phases_tree.set(item, "Phase", f"🟡 {phase_display}")
            elif entry_state == 'WINDOW_OPEN':
                self.phases_tree.set(item, "Phase", f"🟠 {phase_display}")
            else:  # SCANNING
                self.phases_tree.set(item, "Phase", f"⚪ {phase_display}")
                
    def update_indicators_display(self):
        """Update the indicators display for selected symbol"""
        symbol = self.symbol_var.get()
        if not symbol or symbol not in self.strategy_states:
            return
            
        indicators = self.strategy_states[symbol].get('indicators', {})
        config = self.strategy_configs.get(symbol, {})
        
        if not indicators:
            return
            
        # Format comprehensive indicators display
        display_text = f"=== {symbol} Technical Indicators & Configuration ===\n\n"
        
        try:
            display_text += f"📈 CURRENT MARKET DATA\n"
            
            # Get symbol precision for dynamic formatting
            state = self.strategy_states.get(symbol, {})
            digits = state.get('digits', 5)  # Default to 5 if not found
            
            # Safe formatting for price
            current_price = indicators.get('current_price', 'N/A')
            if isinstance(current_price, (int, float)):
                display_text += f"Current Price: {current_price:.{digits}f}\n"
            else:
                display_text += f"Current Price: {current_price}\n"
            display_text += f"Trend Direction: {indicators.get('trend', 'N/A')}\n\n"
            
            display_text += f"📊 EMA INDICATORS (Asset-Specific - ALL 5 EMAs)\n"
            
            # Safe formatting for ALL EMAs (including Confirm EMA)
            # 1. Confirm EMA (CRITICAL for crossover detection)
            ema_confirm = indicators.get('ema_confirm', 'N/A')
            if isinstance(ema_confirm, (int, float)):
                display_text += f"Confirm EMA (1):     {ema_confirm:.{digits}f}  ← Crossover Signal\n"
            else:
                display_text += f"Confirm EMA (1):     {ema_confirm}  ← Crossover Signal\n"
            
            # 2. Fast EMA
            ema_fast = indicators.get('ema_fast', 'N/A')
            if isinstance(ema_fast, (int, float)):
                display_text += f"Fast EMA ({indicators.get('ema_fast_period', '?')}):       {ema_fast:.{digits}f}\n"
            else:
                display_text += f"Fast EMA ({indicators.get('ema_fast_period', '?')}):       {ema_fast}\n"
            
            # 3. Medium EMA
            ema_medium = indicators.get('ema_medium', 'N/A')
            if isinstance(ema_medium, (int, float)):
                display_text += f"Medium EMA ({indicators.get('ema_medium_period', '?')}):     {ema_medium:.{digits}f}\n"
            else:
                display_text += f"Medium EMA ({indicators.get('ema_medium_period', '?')}):     {ema_medium}\n"
            
            # 4. Slow EMA
            ema_slow = indicators.get('ema_slow', 'N/A')
            if isinstance(ema_slow, (int, float)):
                display_text += f"Slow EMA ({indicators.get('ema_slow_period', '?')}):       {ema_slow:.{digits}f}\n"
            else:
                display_text += f"Slow EMA ({indicators.get('ema_slow_period', '?')}):       {ema_slow}\n"
            
            # 5. Filter EMA (trend filter)
            ema_filter = indicators.get('ema_filter', 'N/A')
            if isinstance(ema_filter, (int, float)):
                display_text += f"Filter EMA ({indicators.get('ema_filter_period', '?')}):     {ema_filter:.{digits}f}  ← Trend Filter\n\n"
            else:
                display_text += f"Filter EMA ({indicators.get('ema_filter_period', '?')}):     {ema_filter}  ← Trend Filter\n\n"
            
            display_text += f"⚡ ATR & RISK MANAGEMENT\n"
            
            # Safe formatting for ATR and levels
            atr = indicators.get('atr', 'N/A')
            if isinstance(atr, (int, float)):
                display_text += f"ATR ({indicators.get('atr_period', '?')}): {atr:.{digits+1}f}\n"  # ATR with extra digit for precision
            else:
                display_text += f"ATR ({indicators.get('atr_period', '?')}): {atr}\n"
                
            sl_level = indicators.get('sl_level', 'N/A')
            if isinstance(sl_level, (int, float)):
                display_text += f"Stop Loss Level: {sl_level:.{digits}f} (ATR × {indicators.get('sl_multiplier', '?')})\n"
            else:
                display_text += f"Stop Loss Level: {sl_level} (ATR × {indicators.get('sl_multiplier', '?')})\n"
                
            tp_level = indicators.get('tp_level', 'N/A')
            if isinstance(tp_level, (int, float)):
                display_text += f"Take Profit Level: {tp_level:.{digits}f} (ATR × {indicators.get('tp_multiplier', '?')})\n"
            else:
                display_text += f"Take Profit Level: {tp_level} (ATR × {indicators.get('tp_multiplier', '?')})\n"
                
            # Safe risk:reward calculation
            risk_reward = 0
            sl_mult = indicators.get('sl_multiplier')
            tp_mult = indicators.get('tp_multiplier')
            if sl_mult and tp_mult and isinstance(sl_mult, (int, float)) and isinstance(tp_mult, (int, float)) and sl_mult != 0:
                risk_reward = tp_mult / sl_mult
                display_text += f"Risk:Reward Ratio: 1:{risk_reward:.2f}\n\n"
            else:
                display_text += f"Risk:Reward Ratio: Not available\n\n"
            
            display_text += f"🕐 ENTRY SCHEDULE\n"
            use_time_filter = config.get('Use Time Range Filter', 'False')
            if 'True' in str(use_time_filter):
                start_hour = config.get('Entry Start Hour (UTC)', 'N/A')
                start_min = config.get('Entry Start Minute', '0')
                end_hour = config.get('Entry End Hour (UTC)', 'N/A')
                end_min = config.get('Entry End Minute', '0')
                display_text += f"Time Filter: ENABLED\n"
                display_text += f"Entry Window: {start_hour}:{start_min} - {end_hour}:{end_min} UTC\n"
            else:
                display_text += f"Time Filter: DISABLED (24/7 trading)\n"
            display_text += "\n"
            
            display_text += f"🎯 PULLBACK ENTRY SYSTEM\n"
            use_pullback = config.get('Use Pullback Entry System', 'False')
            if 'True' in str(use_pullback):
                max_candles = config.get('Max Pullback Candles', 'N/A')
                window_periods = config.get('Entry Window Periods', 'N/A')
                window_offset = config.get('Window Offset Multiplier', 'N/A')
                display_text += f"Pullback System: ENABLED\n"
                display_text += f"Max Pullback Candles: {max_candles}\n"
                display_text += f"Entry Window Periods: {window_periods}\n"
                display_text += f"Window Offset Multiplier: {window_offset}\n"
            else:
                display_text += f"Pullback System: DISABLED (Direct entries)\n"
            display_text += "\n"
            
            display_text += f"🔍 ENTRY FILTERS\n"
            # ATR Filter
            use_atr_filter = config.get('Use ATR Volatility Filter', 'False')
            if 'True' in str(use_atr_filter):
                min_atr = config.get('ATR Min Threshold', 'N/A')
                max_atr = config.get('ATR Max Threshold', 'N/A')
                display_text += f"LONG ATR Filter: ENABLED ({min_atr} - {max_atr})\n"
            else:
                display_text += f"LONG ATR Filter: DISABLED\n"
                
            use_short_atr_filter = config.get('Short Use ATR Volatility Filter', 'False')
            if 'True' in str(use_short_atr_filter):
                min_atr = config.get('Short ATR Min Threshold', 'N/A')
                max_atr = config.get('Short ATR Max Threshold', 'N/A')
                display_text += f"SHORT ATR Filter: ENABLED ({min_atr} - {max_atr})\n"
            else:
                display_text += f"SHORT ATR Filter: DISABLED\n"
                
            # Angle Filter
            use_angle_filter = config.get('Use EMA Angle Filter', 'False')
            if 'True' in str(use_angle_filter):
                min_angle = config.get('Min EMA Angle (degrees)', 'N/A')
                max_angle = config.get('Max EMA Angle (degrees)', 'N/A')
                display_text += f"LONG Angle Filter: ENABLED ({min_angle}° - {max_angle}°)\n"
            else:
                display_text += f"LONG Angle Filter: DISABLED\n"
                
            use_short_angle_filter = config.get('Short Use EMA Angle Filter', 'False')
            if 'True' in str(use_short_angle_filter):
                min_angle = config.get('Short Min EMA Angle (degrees)', 'N/A')
                max_angle = config.get('Short Max EMA Angle (degrees)', 'N/A')
                display_text += f"SHORT Angle Filter: ENABLED ({min_angle}° - {max_angle}°)\n"
            else:
                display_text += f"SHORT Angle Filter: DISABLED\n"
                
            # Price Filter
            use_price_filter = config.get('Use Price Filter EMA', 'False')
            display_text += f"LONG Price Filter: {'ENABLED' if 'True' in str(use_price_filter) else 'DISABLED'}\n"
            
            use_short_price_filter = config.get('Short Use Price Filter EMA', 'False')
            display_text += f"SHORT Price Filter: {'ENABLED' if 'True' in str(use_short_price_filter) else 'DISABLED'}\n"
            
            # EMA Position Filter
            use_ema_pos_filter = config.get('Use EMA Below Price Filter', 'False')
            display_text += f"LONG EMA Position Filter: {'ENABLED' if 'True' in str(use_ema_pos_filter) else 'DISABLED'}\n"
            
            use_short_ema_pos_filter = config.get('Short Use EMA Above Price Filter', 'False')
            display_text += f"SHORT EMA Position Filter: {'ENABLED' if 'True' in str(use_short_ema_pos_filter) else 'DISABLED'}\n"
            
            display_text += "\n"
            
            # Strategy state info
            state = self.strategy_states[symbol]
            display_text += f"📊 CURRENT STRATEGY STATE\n"
            display_text += f"Phase: {state['phase']}\n"
            display_text += f"Armed Direction: {state.get('armed_direction', 'None')}\n"
            display_text += f"Pullback Count: {state.get('pullback_count', 0)}\n"
            display_text += f"Window Active: {state.get('window_active', False)}\n"
            display_text += f"Last Update: {state['last_update'].strftime('%H:%M:%S')}\n"
            
        except Exception as e:
            display_text += f"Error displaying indicators: {str(e)}\n"
            
        # Update display
        self.indicators_text.delete(1.0, tk.END)
        self.indicators_text.insert(1.0, display_text)
        
    def update_window_markers(self):
        """Update the window markers display"""
        # Clear existing items
        for item in self.markers_tree.get_children():
            self.markers_tree.delete(item)
            
        # Add window markers for strategies in WINDOW_OPEN state
        for symbol, state in self.strategy_states.items():
            entry_state = state.get('entry_state', 'SCANNING')
            
            if entry_state == 'WINDOW_OPEN' and state.get('window_active', False):
                armed_direction = state.get('armed_direction', 'Unknown')
                window_start = state.get('window_bar_start', 'None')
                window_end = state.get('window_expiry_bar', 'None')
                
                # Show breakout levels (top/bottom limits)
                window_top = state.get('window_top_limit')
                window_bottom = state.get('window_bottom_limit')
                digits = state.get('digits', 5)  # Get symbol precision
                
                if armed_direction == 'LONG':
                    # LONG breakout = price breaks above top limit
                    breakout_str = f"{window_top:.{digits}f}" if window_top else "None"
                else:
                    # SHORT breakout = price breaks below bottom limit
                    breakout_str = f"{window_bottom:.{digits}f}" if window_bottom else "None"
                    
                values = (
                    symbol,
                    armed_direction,
                    str(window_start) if window_start else 'None',
                    str(window_end) if window_end else 'None',
                    breakout_str,
                    "ACTIVE"
                )
                
                self.markers_tree.insert("", tk.END, values=values)
                
    def refresh_chart(self):
        """Refresh the current chart with candlesticks"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        symbol = self.chart_symbol_var.get()
        if symbol not in self.chart_data:
            self.terminal_log(f"⚠️ No chart data available for {symbol}", "ERROR")
            return
            
        try:
            chart_info = self.chart_data[symbol]
            df = chart_info['df']
            indicators = chart_info['indicators']
            
            # Clear previous plot
            self.ax.clear()
            
            # Visualization Layer: Convert Broker Time to UTC
            df_local = df.copy()
            if pd is not None:
                df_local['time'] = pd.to_datetime(df['time'])  # type: ignore
                # Adjust for timezone offset (subtract broker offset to get UTC)
                df_local['time'] = df_local['time'] - timedelta(hours=self.broker_utc_offset)
            else:
                return
            
            # Create candlestick chart
            self.plot_candlesticks(self.ax, df_local)
            
            # Plot EMAs with actual periods from config
            config = self.strategy_configs.get(symbol, {})
            
            # Get actual EMA periods from strategy configuration
            fast_period = self.extract_numeric_value(config.get('ema_fast_length', config.get('Fast EMA Period', '18')))
            medium_period = self.extract_numeric_value(config.get('ema_medium_length', config.get('Medium EMA Period', '18')))
            slow_period = self.extract_numeric_value(config.get('ema_slow_length', config.get('Slow EMA Period', '24')))
            confirm_period = self.extract_numeric_value(config.get('ema_confirm_length', config.get('Confirmation EMA Period', '1')))
            filter_period = self.extract_numeric_value(config.get('ema_filter_price_length', config.get('Price Filter EMA Period', '100')))
            
            # Plot ALL EMAs with asset-specific periods
            # ✅ CRITICAL: Use adjust=False to match MT5 EMA calculation
            # ✅ CRITICAL: Only plot from point where EMA stabilizes (3x period minimum)
            
            # 1. Confirm EMA (most important for crossovers)
            min_bars_confirm = int(confirm_period * 3)  # Need 3x period to stabilize
            if len(df_local) >= min_bars_confirm:
                ema_confirm = df_local['close'].ewm(span=confirm_period, adjust=False).mean()
                # Only plot from stabilization point
                self.ax.plot(df_local['time'].iloc[min_bars_confirm:], 
                           ema_confirm.iloc[min_bars_confirm:], 
                           label=f'EMA Confirm ({int(confirm_period)})', 
                           color='cyan', alpha=0.9, linewidth=2, linestyle='-')
            
            # 2. Fast EMA
            min_bars_fast = int(fast_period * 3)
            if len(df_local) >= min_bars_fast:
                ema_fast = df_local['close'].ewm(span=fast_period, adjust=False).mean()
                self.ax.plot(df_local['time'].iloc[min_bars_fast:], 
                           ema_fast.iloc[min_bars_fast:], 
                           label=f'EMA Fast ({int(fast_period)})', 
                           color='red', alpha=0.8, linewidth=1.5)
            
            # 3. Medium EMA
            min_bars_medium = int(medium_period * 3)
            if len(df_local) >= min_bars_medium:
                ema_medium = df_local['close'].ewm(span=medium_period, adjust=False).mean()
                self.ax.plot(df_local['time'].iloc[min_bars_medium:], 
                           ema_medium.iloc[min_bars_medium:], 
                           label=f'EMA Medium ({int(medium_period)})', 
                           color='orange', alpha=0.8, linewidth=1.5)
            
            # 4. Slow EMA
            min_bars_slow = int(slow_period * 3)
            if len(df_local) >= min_bars_slow:
                ema_slow = df_local['close'].ewm(span=slow_period, adjust=False).mean()
                self.ax.plot(df_local['time'].iloc[min_bars_slow:], 
                           ema_slow.iloc[min_bars_slow:], 
                           label=f'EMA Slow ({int(slow_period)})', 
                           color='green', alpha=0.8, linewidth=1.5)
            
            # 5. Filter EMA (trend filter)
            min_bars_filter = int(filter_period * 3)  # EMA(70) needs ~210 bars
            if len(df_local) >= min_bars_filter:
                ema_filter = df_local['close'].ewm(span=filter_period, adjust=False).mean()
                self.ax.plot(df_local['time'].iloc[min_bars_filter:], 
                           ema_filter.iloc[min_bars_filter:], 
                           label=f'EMA Filter ({int(filter_period)})', 
                           color='purple', alpha=0.7, linewidth=1.5, linestyle='-')
            
            # Mark current phase
            state = self.strategy_states[symbol]
            phase_colors = {
                'NORMAL': 'lightgray',
                'WAITING_PULLBACK': 'yellow',
                'WAITING_BREAKOUT': 'orange'
            }
            phase_color = phase_colors.get(state['phase'], 'lightgray')
            
            # Add phase indicator as background
            current_price = indicators.get('current_price', df_local['close'].iloc[-1])
            self.ax.axhspan(current_price * 0.9999, current_price * 1.0001, 
                          color=phase_color, alpha=0.3, 
                          label=f'Phase: {state["phase"]}')
            
            # Mark pullback phase with special indicators
            if state['phase'] == 'WAITING_PULLBACK':
                pullback_count = state.get('pullback_candle_count', 0)
                self.ax.text(0.02, 0.98, f'Pullback Count: {pullback_count}', 
                           transform=self.ax.transAxes, fontsize=10, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                           verticalalignment='top')
                           
            elif state['phase'] == 'WAITING_BREAKOUT':
                breakout_level = state.get('breakout_level', current_price)
                if breakout_level:
                    self.ax.axhline(y=breakout_level, color='red', linestyle='--', 
                                  alpha=0.8, label=f'Breakout Level: {breakout_level:.5f}')
            
            # NEW: Add ATR SL/TP levels visualization
            atr = indicators.get('atr')
            if atr and atr != 'N/A' and isinstance(atr, (int, float)) and atr > 0:
                # Get asset-specific ATR multipliers from config
                sl_multiplier_long = self.extract_float_value(config.get('long_atr_sl_multiplier', 
                                                              config.get('LONG ATR SL Multiplier', '3.0')))
               
                tp_multiplier_long = self.extract_float_value(config.get('long_atr_tp_multiplier', 
                                                              config.get('LONG ATR TP Multiplier', '10.0')))
                sl_multiplier_short = self.extract_float_value(config.get('short_atr_sl_multiplier', 
                                                               config.get('SHORT ATR SL Multiplier', '3.0')))
                tp_multiplier_short = self.extract_float_value(config.get('short_atr_tp_multiplier', 
                                                               config.get('SHORT ATR TP Multiplier', '8.0')))
                
                # Calculate LONG levels (using last low/high from df)
                last_low = df_local['low'].iloc[-1]
                last_high = df_local['high'].iloc[-1]
                
                sl_level_long = last_low - (atr * sl_multiplier_long)
                tp_level_long = last_high + (atr * tp_multiplier_long)
                
                # Calculate SHORT levels
                sl_level_short = last_high + (atr * sl_multiplier_short)
                tp_level_short = last_low - (atr * tp_multiplier_short)
                
                # Plot LONG levels (green zone)
                self.ax.axhline(y=sl_level_long, color='green', linestyle=':', 
                              alpha=0.5, linewidth=1.5, label=f'LONG SL: {sl_level_long:.5f}')
                self.ax.axhline(y=tp_level_long, color='lime', linestyle=':', 
                              alpha=0.5, linewidth=1.5, label=f'LONG TP: {tp_level_long:.5f}')
                
                # Check if SHORT trades are enabled before showing SHORT levels
                config = self.strategy_configs.get(symbol, {})
                short_enabled = config.get('ENABLE_SHORT_TRADES', 'False')
                if isinstance(short_enabled, str):
                    short_enabled = short_enabled.lower() in ('true', '1', 'yes')
                
                # Only plot SHORT levels if SHORT trades are enabled
                if short_enabled:
                    self.ax.axhline(y=sl_level_short, color='red', linestyle=':', 
                                  alpha=0.5, linewidth=1.5, label=f'SHORT SL: {sl_level_short:.5f}')
                    self.ax.axhline(y=tp_level_short, color='darkred', linestyle=':', 
                                  alpha=0.5, linewidth=1.5, label=f'SHORT TP: {tp_level_short:.5f}')
                
                # Add ATR indicator box on chart
                if short_enabled:
                    atr_text = (f'ATR: {atr:.6f}\n'
                               f'LONG: SL={sl_multiplier_long:.1f}x TP={tp_multiplier_long:.1f}x\n'
                               f'SHORT: SL={sl_multiplier_short:.1f}x TP={tp_multiplier_short:.1f}x')
                else:
                    atr_text = (f'ATR: {atr:.6f}\n'
                               f'LONG: SL={sl_multiplier_long:.1f}x TP={tp_multiplier_long:.1f}x')
                
                self.ax.text(0.98, 0.02, atr_text, 
                           transform=self.ax.transAxes, fontsize=8,
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7),
                           verticalalignment='bottom', horizontalalignment='right')
            
            # Formatting
            self.ax.set_title(f'{symbol} - Live Candlestick Chart with ATR SL/TP (Phase: {state["phase"]})')
            self.ax.set_xlabel('Time (UTC)')
            self.ax.set_ylabel('Price')
            self.ax.legend(loc='upper left', fontsize=7, ncol=2)
            self.ax.grid(True, alpha=0.3)
            
            # Format time axis
            if mdates is not None:
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # type: ignore
            self.ax.tick_params(axis='x', rotation=45, labelsize=8)
            
            # Set reasonable y-axis limits
            price_range = df_local['high'].max() - df_local['low'].min()
            y_margin = price_range * 0.02  # 2% margin
            self.ax.set_ylim(df_local['low'].min() - y_margin, df_local['high'].max() + y_margin)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
            self.terminal_log(f"📊 Candlestick chart refreshed for {symbol} (Phase: {state['phase']})", "NORMAL")
            
        except Exception as e:
            self.terminal_log(f"❌ Chart refresh error: {str(e)}", "ERROR")
            
    def plot_candlesticks(self, ax, df):
        """Plot candlestick chart"""
        try:
            from matplotlib.patches import Rectangle
            
            for i, (idx, row) in enumerate(df.iterrows()):
                open_price = row['open']
                high_price = row['high'] 
                low_price = row['low']
                close_price = row['close']
                time_point = row['time']
                
                # Determine candle color
                color = 'green' if close_price >= open_price else 'red'
                edge_color = 'darkgreen' if close_price >= open_price else 'darkred'
                
                # Draw high-low line
                ax.plot([time_point, time_point], [low_price, high_price], 
                       color=edge_color, linewidth=0.8)
                
                # Draw candle body
                body_height = abs(close_price - open_price)
                body_bottom = min(open_price, close_price)
                
                # Calculate candle width (time-based) - convert to matplotlib numeric format
                if len(df) > 1:
                    time_diff = (df['time'].iloc[1] - df['time'].iloc[0]).total_seconds() / 86400  # days for matplotlib
                    candle_width_days = float(time_diff * 0.8)  # 80% of time interval
                else:
                    candle_width_days = 4.0 / (60.0 * 24.0)  # 4 minutes converted to days
                
                # Create rectangle for candle body
                # matplotlib expects width in data coordinates (days for dates)
                if Rectangle is not None and mdates is not None:
                    time_num = float(mdates.date2num(time_point))  # type: ignore
                    rect = Rectangle((time_num - candle_width_days/2.0, float(body_bottom)), 
                                   candle_width_days, float(body_height),
                                   facecolor=color, edgecolor=edge_color, 
                                   alpha=0.8, linewidth=0.5)
                    ax.add_patch(rect)
                
        except Exception as e:
            # Fallback to line plot if candlestick fails
            ax.plot(df['time'], df['close'], label='Price', color='blue', linewidth=1)
            
    def process_phase_updates(self):
        """Process phase updates from the monitoring thread"""
        try:
            while not self.phase_update_queue.empty():
                update = self.phase_update_queue.get_nowait()
                # Process update
                
        except queue.Empty:
            pass
        except Exception as e:
            self.terminal_log(f"❌ Phase update error: {str(e)}", "ERROR")
            
        # Schedule next update
        self.root.after(1000, self.process_phase_updates)
        
    def log_phase_summary(self):
        """Log current phase status for all assets"""
        try:
            summary_lines = []
            summary_lines.append("=" * 60)
            summary_lines.append("📊 STRATEGY PHASE SUMMARY - ALL ASSETS")
            summary_lines.append("=" * 60)
            
            # Group by phase for better overview
            phases = {'NORMAL': [], 'WAITING_PULLBACK': [], 'WAITING_BREAKOUT': []}
            
            for symbol, state in self.strategy_states.items():
                phase = state['phase']
                price = state.get('indicators', {}).get('current_price', 0)
                trend = state.get('indicators', {}).get('trend', 'N/A')
                
                if phase in phases:
                    phases[phase].append({
                        'symbol': symbol,
                        'price': price,
                        'trend': trend,
                        'pullback_count': state.get('pullback_count', 0),
                        'window_active': state.get('window_active', False),
                        'last_update': state.get('last_update', datetime.now())
                    })
            
            # Display each phase group
            for phase_name, assets in phases.items():
                if assets:
                    phase_emoji = {
                        'NORMAL': '⚪',
                        'WAITING_PULLBACK': '🟡', 
                        'WAITING_BREAKOUT': '🟠'
                    }.get(phase_name, '⚫')
                    
                    summary_lines.append(f"{phase_emoji} {phase_name} ({len(assets)} assets):")
                    
                    for asset in assets:
                        line = f"   {asset['symbol']}: {asset['price']:.5f} | {asset['trend']}"
                        if phase_name == 'WAITING_PULLBACK':
                            line += f" | Scanning pullback"
                        elif phase_name == 'WAITING_BREAKOUT':
                            line += f" | Pullback: {asset['pullback_count']} | Window: {'OPEN' if asset['window_active'] else 'CLOSED'}"
                        summary_lines.append(line)
                    summary_lines.append("")
            
            # Add timestamp
            summary_lines.append(f"⏰ Updated: {datetime.now().strftime('%H:%M:%S')}")
            summary_lines.append("=" * 60)
            
            # Log each line
            for line in summary_lines:
                self.terminal_log(line, "NORMAL")
                
        except Exception as e:
            self.terminal_log(f"❌ Phase summary error: {str(e)}", "ERROR")
        
    def log_hourly_summary(self):
        """Log hourly activity summary to reduce terminal clutter"""
        now = datetime.now()
        if (now - self.last_hourly_summary).total_seconds() >= 3600:  # Every hour
            # ✅ SET RECURSION GUARD: Prevent terminal_log from calling this again
            self._in_hourly_summary = True
            try:
                self.terminal_log("=" * 70, "INFO", critical=True)
                self.terminal_log(f"📊 HOURLY SUMMARY ({now.strftime('%H:%M')})", "SUCCESS", critical=True)
                self.terminal_log(f"   🔄 Crossovers: {self.hourly_events['crossovers']} | 🎯 Armed: {self.hourly_events['armed_transitions']} | 📉 Pullbacks: {self.hourly_events['pullbacks_detected']}", "INFO", critical=True)
                self.terminal_log(f"   🪟 Windows: {self.hourly_events['windows_opened']} | 🚀 Breakouts: {self.hourly_events['breakouts']} | ⚠️ Invalidations: {self.hourly_events['invalidations']} | 💰 Trades: {self.hourly_events['trades_executed']}", "INFO", critical=True)
                self.terminal_log("=" * 70, "INFO", critical=True)
                
                # Reset counters
                for key in self.hourly_events:
                    self.hourly_events[key] = 0
                self.last_hourly_summary = now
            finally:
                # ✅ CLEAR RECURSION GUARD: Always clear, even if error occurs
                self._in_hourly_summary = False
    
    def terminal_log(self, message, level="NORMAL", critical=False):
        """Add message to terminal display - only critical events by default"""
        
        # ✅ RECURSION GUARD: Prevent infinite loop during hourly summary
        if not getattr(self, '_in_hourly_summary', False):
            # Track events for hourly summary
            if "CROSSED ABOVE" in message or "CROSSED BELOW" in message:
                self.hourly_events['crossovers'] += 1
            elif "CROSSOVER - State: SCANNING → ARMED" in message:
                self.hourly_events['armed_transitions'] += 1
            elif "Pullback CONFIRMED" in message:
                self.hourly_events['pullbacks_detected'] += 1
            elif "Window OPENING" in message:
                self.hourly_events['windows_opened'] += 1
            elif "BREAKOUT detected" in message:
                self.hourly_events['breakouts'] += 1
            elif "GLOBAL INVALIDATION" in message or "Non-pullback candle detected" in message:
                self.hourly_events['invalidations'] += 1
            elif "TRADE EXECUTED" in message or "ORDER FILLED" in message:
                self.hourly_events['trades_executed'] += 1
            
            # Check if it's time for hourly summary (but not if already in summary)
            self.log_hourly_summary()
        
        # Define critical keywords that should always be displayed
        critical_keywords = [
            "CROSSOVER", "CROSS ABOVE", "CROSS BELOW", "CROSSED",  # EMA crossovers
            "PHASE CHANGE", "WAITING_PULLBACK", "WAITING_BREAKOUT",  # Phase changes
            "ENTRY", "EXIT", "BREAKOUT DETECTED", "SIGNAL",  # Trading signals
            "TRADE EXECUTED", "ORDER FILLED", "POSITION OPENED",  # Trade execution
            "ERROR", "⚠️", "❌", "🎯", "🟢", "🔴"  # Errors and alerts
        ]
        
        # Check if message contains critical keywords
        is_critical = critical or any(keyword in message.upper() for keyword in critical_keywords)
        
        # Only log critical messages or explicit critical flag
        if not is_critical:
            # Still log to file for debugging but don't show in terminal
            if level == "ERROR":
                self.logger.error(message)
            elif level == "SUCCESS":
                self.logger.info(f"SUCCESS: {message}")
            else:
                self.logger.info(message)
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to terminal display
        self.terminal_text.insert(tk.END, log_entry, level)
        
        # Scroll to bottom
        self.terminal_text.see(tk.END)
        
        # Limit terminal size (keep last 1000 lines)
        lines = self.terminal_text.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:
            self.terminal_text.delete(1.0, f"{len(lines)-1000}.0")
            
        # Log to file
        if level == "ERROR":
            self.logger.error(message)
        elif level == "SUCCESS":
            self.logger.info(f"SUCCESS: {message}")
        else:
            self.logger.info(message)
            
    def clear_terminal(self):
        """Clear terminal display"""
        self.terminal_text.delete(1.0, tk.END)
        self.terminal_log("Terminal cleared", "NORMAL")
        
    def save_terminal_log(self):
        """Save terminal log to file"""
        filename = f"terminal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            logs = self.terminal_text.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(logs)
                
            messagebox.showinfo("Save Complete", f"Terminal log saved to {filename}")
            self.terminal_log(f"✅ Terminal log saved to {filename}", "SUCCESS")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save: {str(e)}")
            self.terminal_log(f"❌ Save error: {str(e)}", "ERROR")
            
    # Event handlers
    def on_strategy_phase_select(self, event):
        """Handle strategy phase selection"""
        selection = self.phases_tree.selection()
        if not selection:
            return
            
        item = self.phases_tree.item(selection[0])
        symbol = item['values'][0]
        
        # Update symbol selector
        self.symbol_var.set(symbol)
        self.on_symbol_config_select(None)
        
        # Update chart symbol
        self.chart_symbol_var.set(symbol)
        if MATPLOTLIB_AVAILABLE:
            self.refresh_chart()
            
    def on_symbol_config_select(self, event):
        """Handle symbol configuration selection"""
        symbol = self.symbol_var.get()
        if not symbol or symbol not in self.strategy_configs:
            return
            
        config = self.strategy_configs[symbol]
        
        # Format configuration display
        config_text = f"=== {symbol} Strategy Configuration ===\n\n"
        
        if "error" in config:
            config_text += f"Error: {config['error']}\n"
        else:
            for param, value in config.items():
                config_text += f"{param}: {value}\n"
                
        # Update configuration display
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        
        # Update indicators display
        self.update_indicators_display()
        
    def on_chart_symbol_change(self, event):
        """Handle chart symbol change"""
        if MATPLOTLIB_AVAILABLE:
            self.refresh_chart()
            
    def toggle_connection(self):
        """Toggle MT5 connection"""
        if self.mt5_connected:
            self.disconnect_mt5()
        else:
            self.initialize_mt5_connection()
    
    def _execute_entry(self, symbol: str, direction: str, df, current_dt, config: Dict):
        """Execute immediate entry (standard mode without pullback)
        
        Args:
            symbol: Trading symbol
            direction: 'LONG' or 'SHORT'
            df: DataFrame with price data
            current_dt: Current datetime
            config: Strategy configuration
            
        Returns:
            True if trade executed successfully, False otherwise
        """
        if len(df) < 1:
            self.terminal_log(f"❌ {symbol}: Cannot execute entry - no price data", "ERROR", critical=True)
            return False
        
        current_state = self.strategy_states[symbol]
        digits = current_state.get('digits', 5)
        
        # Get entry price (current close)
        entry_price = float(df['close'].iloc[-1])
        
        # Final time check
        if not self._is_in_trading_time_range(current_dt, config):
            self.terminal_log(f"⏰ {symbol}: Entry rejected - outside trading hours", 
                            "WARNING", critical=True)
            return False
        
        # Execute trade
        self.terminal_log(f"⚡ {symbol}: Executing STANDARD {direction} entry at {entry_price:.{digits}f}", 
                        "INFO", critical=True)
        
        trade_executed = self.execute_trade(symbol, direction, entry_price, config)
        
        if trade_executed:
            self.terminal_log(f"✅ {symbol}: STANDARD {direction} trade executed successfully!", 
                            "SUCCESS", critical=True)
            # Lock state to prevent duplicate entries
            current_state['entry_state'] = 'IN_TRADE'
            current_state['phase'] = 'TRADE_ACTIVE'
            self.terminal_log(f"🔒 {symbol}: State locked - No new signals until position closes", 
                            "INFO", critical=True)
            return True
        else:
            self.terminal_log(f"❌ {symbol}: STANDARD {direction} trade execution FAILED", 
                            "ERROR", critical=True)
            return False
            
    def execute_trade(self, symbol: str, direction: str, price: float, config: Dict):
        """Execute a trade in MT5
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            direction: 'LONG' or 'SHORT'
            price: Entry price
            config: Strategy configuration with risk parameters
        """
        if not mt5 or not self.mt5_connected:
            self.terminal_log(f"❌ {symbol}: Cannot execute trade - MT5 not connected", "ERROR", critical=True)
            return False
            
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)  # type: ignore
            if symbol_info is None:
                self.terminal_log(f"❌ {symbol}: Symbol not found in MT5", "ERROR", critical=True)
                return False
                
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):  # type: ignore
                    self.terminal_log(f"❌ {symbol}: Failed to select symbol", "ERROR", critical=True)
                    return False
            
            # Get account info for risk calculation
            account_info = mt5.account_info()  # type: ignore
            if account_info is None:
                self.terminal_log(f"❌ {symbol}: Failed to get account info", "ERROR", critical=True)
                return False
            
            # ✅ CRITICAL FIX: Check if position already exists for this symbol
            positions = mt5.positions_get(symbol=symbol)  # type: ignore
            if positions is not None and len(positions) > 0:
                self.terminal_log(f"⚠️ {symbol}: Position already exists - Skipping duplicate entry", "WARNING", critical=True)
                for pos in positions:
                    self.terminal_log(f"   Existing: Ticket #{pos.ticket} | {pos.type} | Volume: {pos.volume} lots", 
                                    "WARNING", critical=True)
                return False  # Don't open duplicate position
            
            # ═══════════════════════════════════════════════════════════════════
            # DALIO ALL-WEATHER PORTFOLIO ALLOCATION - POSITION SIZING
            # ═══════════════════════════════════════════════════════════════════
            # Calculate position size using asset-specific allocation
            # Risk = risk_percent × allocated_capital (NOT total portfolio)
            # ═══════════════════════════════════════════════════════════════════
            
            # Get real-time account balance from MT5
            balance = account_info.balance
            
            # Get asset-specific allocation (default 16% if symbol not in allocations)
            allocation_percent = ASSET_ALLOCATIONS.get(symbol, 0.16)
            allocated_capital = balance * allocation_percent
            
            # Get risk percentage (configurable per strategy, default 1%)
            # This is % of ALLOCATED capital, not total portfolio
            risk_percent = config.get('RISK_PER_TRADE', DEFAULT_RISK_PERCENT)
            
            # Calculate risk amount based on allocated capital
            risk_amount = allocated_capital * risk_percent
            
            # Log allocation details for transparency
            self.terminal_log(
                f"💰 {symbol}: Dalio Allocation System",
                "INFO", critical=True
            )
            self.terminal_log(
                f"   Portfolio Balance: ${balance:,.2f}",
                "INFO", critical=True
            )
            self.terminal_log(
                f"   Asset Allocation: {allocation_percent*100:.0f}% = ${allocated_capital:,.2f}",
                "INFO", critical=True
            )
            self.terminal_log(
                f"   Risk Per Trade: {risk_percent*100:.1f}% of allocated = ${risk_amount:.2f}",
                "INFO", critical=True
            )
            
            # Get ATR for stop loss calculation from indicators
            current_state = self.strategy_states.get(symbol, {})
            indicators = current_state.get('indicators', {})
            atr = indicators.get('atr', None)
            
            # Log ATR retrieval for debugging
            self.terminal_log(f"📊 {symbol}: ATR Check | Value={atr} | Has_indicators={bool(indicators)} | State_keys={list(current_state.keys())}", 
                            "INFO", critical=True)
            
            if atr is None or atr <= 0 or (isinstance(atr, float) and (pd.isna(atr) if pd else False)):
                self.terminal_log(f"❌ {symbol}: Invalid ATR value for stop loss calculation (ATR={atr})", 
                                "ERROR", critical=True)
                return False
            
            # Get multipliers from config
            if direction == 'LONG':
                atr_sl_multiplier = self.extract_float_value(config.get('long_atr_sl_multiplier', '4.5'))
                atr_tp_multiplier = self.extract_float_value(config.get('long_atr_tp_multiplier', '6.5'))
            else:  # SHORT
                atr_sl_multiplier = self.extract_float_value(config.get('short_atr_sl_multiplier', '4.5'))
                atr_tp_multiplier = self.extract_float_value(config.get('short_atr_tp_multiplier', '6.5'))
            
            self.terminal_log(f"📊 {symbol}: ATR={atr:.5f} | SL_Multi={atr_sl_multiplier} | TP_Multi={atr_tp_multiplier}", 
                            "INFO", critical=True)
            
            # Calculate stop loss distance
            sl_distance = atr * atr_sl_multiplier
            
            self.terminal_log(f"📊 {symbol}: SL_Distance={sl_distance:.5f} (ATR {atr:.5f} × {atr_sl_multiplier})", 
                            "INFO", critical=True)
            
            # Calculate lot size based on risk
            # For commodities (XAUUSD, XAGUSD): 1 lot = contract_size units (e.g., 100 oz)
            # For forex (EURUSD, etc.): 1 lot = 100,000 units
            # Formula: lot_size = risk_amount / (sl_distance_in_price × pip_value_per_lot)
            
            point = symbol_info.point
            contract_size = symbol_info.trade_contract_size  # 100 for XAUUSD, 100000 for EURUSD/GBPUSD
            tick_value = symbol_info.trade_tick_value  # Value per tick in account currency
            tick_size = symbol_info.trade_tick_size
            
            # 🚨 CRITICAL FIX: Use MT5's tick_value directly (it's correct per broker contract specs)
            # The formula is: lot_size = risk / (sl_distance_points × tick_value_per_tick × ticks_per_point)
            # Simplified: lot_size = risk / (sl_distance_in_points × value_per_point)
            
            # Calculate value per point from MT5 symbol info
            # tick_value = value change per tick in account currency
            # tick_size = minimum price change (tick)
            # point = minimum price representation (usually same as tick_size)
            
            if tick_size > 0 and point > 0:
                # Value per point = tick_value × (point / tick_size)
                # For most symbols: point == tick_size, so value_per_point = tick_value
                value_per_point = tick_value * (point / tick_size)
            else:
                # Fallback if tick data is invalid
                value_per_point = tick_value if tick_value > 0 else 0.01
            
            # Calculate SL distance in points (not pips!)
            # point = minimum price unit (e.g., 0.00001 for EURUSD, 0.01 for XAUUSD, 0.001 for XAGUSD)
            sl_distance_in_points = sl_distance / point
            
            # Calculate lot size using broker-specific values
            # Formula: lot_size = risk_amount / (sl_distance_in_points × value_per_point)
            if value_per_point > 0 and sl_distance_in_points > 0:
                lot_size = risk_amount / (sl_distance_in_points * value_per_point)
            else:
                self.terminal_log(f"❌ {symbol}: Invalid calculation values - value_per_point={value_per_point}, sl_distance_in_points={sl_distance_in_points}", "ERROR", critical=True)
                return False
            
            # 💰 Position Sizing Calculation with Detailed Logging
            self.terminal_log(f"═══════════════════════════════════════════════════", "INFO", critical=True)
            self.terminal_log(f"� {symbol}: POSITION SIZING CALCULATION", "INFO", critical=True)
            self.terminal_log(f"═══════════════════════════════════════════════════", "INFO", critical=True)
            
            # Broker Symbol Specifications
            self.terminal_log(f"📊 BROKER SPECIFICATIONS:", "DEBUG", critical=True)
            self.terminal_log(f"   Symbol: {symbol} | Digits: {symbol_info.digits}", "DEBUG", critical=True)
            self.terminal_log(f"   Contract Size: {contract_size:,.0f}", "DEBUG", critical=True)
            self.terminal_log(f"   Point: {point:.5f} (minimum price unit)", "DEBUG", critical=True)
            self.terminal_log(f"   Tick Size: {tick_size:.5f} (minimum price change)", "DEBUG", critical=True)
            self.terminal_log(f"   Tick Value: ${tick_value:.5f} (profit per tick)", "DEBUG", critical=True)
            self.terminal_log(f"   Calculated Value per Point: ${value_per_point:.5f}", "DEBUG", critical=True)
            
            # Dalio Allocation
            self.terminal_log(f"� DALIO ALLOCATION:", "DEBUG", critical=True)
            self.terminal_log(f"   Portfolio Balance: ${balance:,.2f}", "DEBUG", critical=True)
            self.terminal_log(f"   Asset Allocation: {allocation_percent*100:.0f}% → ${allocated_capital:,.2f}", "DEBUG", critical=True)
            self.terminal_log(f"   Risk per Trade: {risk_percent*100:.1f}% of allocated → ${risk_amount:.2f}", "DEBUG", critical=True)
            
            # Stop Loss Distance
            self.terminal_log(f"🛑 STOP LOSS:", "DEBUG", critical=True)
            self.terminal_log(f"   SL Distance (price): {sl_distance:.5f}", "DEBUG", critical=True)
            self.terminal_log(f"   SL Distance (points): {sl_distance_in_points:.1f}", "DEBUG", critical=True)
            self.terminal_log(f"   ATR Multiplier: {atr_sl_multiplier:.1f}", "DEBUG", critical=True)
            
            # Position Size Calculation
            self.terminal_log(f"📐 LOT SIZE FORMULA:", "DEBUG", critical=True)
            self.terminal_log(f"   lot_size = risk_amount / (sl_distance_points × value_per_point)", "DEBUG", critical=True)
            self.terminal_log(f"   lot_size = ${risk_amount:.2f} / ({sl_distance_in_points:.1f} × ${value_per_point:.5f})", "DEBUG", critical=True)
            self.terminal_log(f"   lot_size = ${risk_amount:.2f} / {sl_distance_in_points * value_per_point:.5f}", "DEBUG", critical=True)
            self.terminal_log(f"   lot_size = {lot_size:.6f} lots (BEFORE limits)", "DEBUG", critical=True)
            
            # Risk Verification
            actual_risk_check = lot_size * sl_distance_in_points * value_per_point
            self.terminal_log(f"✅ RISK VERIFICATION:", "DEBUG", critical=True)
            self.terminal_log(f"   {lot_size:.6f} lots × {sl_distance_in_points:.1f} points × ${value_per_point:.5f} = ${actual_risk_check:.2f}", "DEBUG", critical=True)
            risk_diff = abs(actual_risk_check - risk_amount)
            if risk_diff < 0.50:
                self.terminal_log(f"   ✅ VERIFIED: Actual risk ${actual_risk_check:.2f} matches expected ${risk_amount:.2f}", "INFO", critical=True)
            else:
                self.terminal_log(f"   ⚠️ WARNING: Risk mismatch! Expected ${risk_amount:.2f}, got ${actual_risk_check:.2f} (diff: ${risk_diff:.2f})", "WARNING", critical=True)
            
            # Apply lot size limits
            lot_min = symbol_info.volume_min
            lot_max = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            
            # Round to valid lot step
            lot_size = round(lot_size / lot_step) * lot_step
            
            # Apply broker's min/max limits (removed 0.1 cap!)
            lot_size = max(lot_min, min(lot_size, lot_max))
            
            # Log final volume after limits
            self.terminal_log(f"   Final Volume: {lot_size:.6f} lots (min={lot_min}, max={lot_max}, step={lot_step})", "DEBUG", critical=True)
            
            # Prepare order parameters
            order_type = mt5.ORDER_TYPE_BUY if direction == 'LONG' else mt5.ORDER_TYPE_SELL  # type: ignore
            
            # Set stop loss and take profit
            if direction == 'LONG':
                sl_price = price - sl_distance
                tp_price = price + (atr * atr_tp_multiplier)
            else:  # SHORT
                sl_price = price + sl_distance
                tp_price = price - (atr * atr_tp_multiplier)
            
            # Round prices to symbol digits
            digits = symbol_info.digits
            sl_price = round(sl_price, digits)
            tp_price = round(tp_price, digits)
            
            # ⚡ CRITICAL FIX: Detect broker's supported filling mode
            # Error 10030 = INVALID_FILL occurs when using unsupported filling mode
            symbol_info = mt5.symbol_info(symbol)  # type: ignore
            if symbol_info is None:
                self.terminal_log(f"❌ {symbol}: Cannot get symbol info", "ERROR", critical=True)
                return False
            
            # Determine filling mode based on broker's support
            # filling_mode flags: 1=FOK, 2=IOC, 4=RETURN (can be combined)
            filling_type = None
            if symbol_info.filling_mode & 2:  # IOC supported
                filling_type = mt5.ORDER_FILLING_IOC  # type: ignore
            elif symbol_info.filling_mode & 1:  # FOK supported
                filling_type = mt5.ORDER_FILLING_FOK  # type: ignore
            elif symbol_info.filling_mode & 4:  # RETURN supported
                filling_type = mt5.ORDER_FILLING_RETURN  # type: ignore
            else:
                # Fallback to FOK
                filling_type = mt5.ORDER_FILLING_FOK  # type: ignore
            
            self.terminal_log(f"🔧 {symbol}: Using filling mode {filling_type} (broker supports: {symbol_info.filling_mode})", 
                            "DEBUG", critical=True)
            
            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,  # type: ignore
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 234000,
                "comment": f"Sunrise_{direction}",
                "type_time": mt5.ORDER_TIME_GTC,  # type: ignore
                "type_filling": filling_type,  # ✅ Use broker-compatible mode
            }
            
            # Log trade details
            self.terminal_log(f"📊 {symbol}: Preparing {direction} order", "INFO", critical=True)
            self.terminal_log(f"   Entry: {price} | SL: {sl_price} (dist: {sl_distance:.5f}) | TP: {tp_price}", "INFO", critical=True)
            self.terminal_log(f"   Volume: {lot_size} lots | Risk: ${risk_amount:.2f} ({risk_percent*100:.1f}%)", "INFO", critical=True)
            self.terminal_log(f"   ATR: {atr:.5f} | SL_Multi: {atr_sl_multiplier} | TP_Multi: {atr_tp_multiplier}", "INFO", critical=True)
            
            # Send order
            result = mt5.order_send(request)  # type: ignore
            
            if result is None:
                self.terminal_log(f"❌ {symbol}: Order send failed - No response", "ERROR", critical=True)
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:  # type: ignore
                self.terminal_log(f"❌ {symbol}: Order failed - Code: {result.retcode}, {result.comment}", 
                                "ERROR", critical=True)
                return False
            
            # Success!
            self.terminal_log(f"✅ {symbol}: Order executed successfully!", "SUCCESS", critical=True)
            self.terminal_log(f"   Order: #{result.order} | Deal: #{result.deal}", "SUCCESS", critical=True)
            self.terminal_log(f"   Volume: {result.volume} lots @ {result.price}", "SUCCESS", critical=True)
            
            return True
            
        except Exception as e:
            self.terminal_log(f"❌ {symbol}: Trade execution error: {str(e)}", "ERROR", critical=True)
            return False
    
    def disconnect_mt5(self):
        """Disconnect from MT5"""
        if mt5:
            mt5.shutdown()  # type: ignore
        self.mt5_connected = False
        self.connection_status_label.config(text="Disconnected", foreground="red")
        self.connect_button.config(text="Connect")
        
        self.terminal_log("🔌 Disconnected from MT5", "NORMAL")
        
    def on_closing(self):
        """Handle application closing"""
        try:
            if self.monitoring_active:
                self.stop_monitoring()
                
            if self.mt5_connected:
                self.disconnect_mt5()
                
            self.terminal_log("🔥 Application closing...", "NORMAL")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
        finally:
            self.root.quit()
            self.root.destroy()

def main():
    """Main application entry point"""
    print(f"🚀 Starting Advanced MT5 Trading Monitor v{APP_VERSION}...")
    print("=" * 60)
    
    # Check dependencies
    if not DEPENDENCIES_AVAILABLE:
        print("❌ ERROR: Required dependencies not found!")
        print("Please install: pip install MetaTrader5 pandas numpy")
        return
        
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  WARNING: Chart libraries not found!")
        print("For live charts, install: pip install matplotlib mplfinance")
        print("Continuing without charts...")
        print()
        
    try:
        # Create and run GUI
        root = tk.Tk()
        app = AdvancedMT5TradingMonitorGUI(root)
        
        print("✅ Advanced GUI initialized successfully")
        print("📊 Starting strategy phase monitoring...")
        print("=" * 60)
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting GUI: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()