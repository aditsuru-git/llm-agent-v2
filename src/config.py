# src/config.py

# --- UI Color Configuration ---
# Customize the look and feel of the CLI.
# You can use standard color names (e.g., "red", "cyan") or hexcodes (e.g., "#FF5733").
# For a full list of names: https://rich.readthedocs.io/en/latest/appendix/colors.html

# --- Core Theme ---
# The primary color is used for banners, panel borders, and major UI highlights.
THEME_COLOR_PRIMARY = "cyan"
# The secondary color is used for less prominent elements, like table headers.
THEME_COLOR_SECONDARY = "magenta"


# --- Actor Colors ---
# Color for the AI's name and its response panel border.
AI_COLOR = "#FF5733"
# Color for the user's "You" prompt.
USER_COLOR = "cyan"


# --- Semantic Colors ---
# Color for success messages (e.g., "History cleared successfully!").
SUCCESS_COLOR = "green"
# Color for warnings and confirmation prompts.
WARNING_COLOR = "yellow"
# Color for error messages.
ERROR_COLOR = "red"


# --- Text Colors ---
# Default color for most text content.
NEUTRAL_COLOR = "white"
# Style for subtle system messages (e.g., "Goodbye!", "Ready to help!").
# Can be a color name like "grey50" or a style like "dim".
SYSTEM_DIM_STYLE = "dim"
