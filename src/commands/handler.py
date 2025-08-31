from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from src.db.persistence import clear_history_from_mongodb
from src.config import (
    THEME_COLOR_PRIMARY,
    THEME_COLOR_SECONDARY,
    NEUTRAL_COLOR,
    WARNING_COLOR,
    SUCCESS_COLOR,
    ERROR_COLOR,
    SYSTEM_DIM_STYLE,
)


def _print_help(console: Console):
    """Displays the help panel."""
    help_table = Table(show_header=True, header_style=f"bold {THEME_COLOR_SECONDARY}")
    help_table.add_column("Command", style=THEME_COLOR_PRIMARY, min_width=12)
    help_table.add_column("Description", style=NEUTRAL_COLOR)

    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/clear", "Clear conversation history")
    help_table.add_row("/exit, /quit", "Exit the assistant")
    help_table.add_row("Ctrl+C", "Force exit")
    help_table.add_row("Ctrl+D", "Graceful exit")

    help_panel = Panel(
        help_table,
        title=f"[bold {THEME_COLOR_PRIMARY}]Available Commands[/bold {THEME_COLOR_PRIMARY}]",
        border_style=THEME_COLOR_PRIMARY,
    )
    console.print()
    console.print(help_panel)


def _handle_clear(console: Console):
    """Handles the /clear command with confirmation."""
    console.print()
    if Confirm.ask(
        f"[bold {WARNING_COLOR}]Are you sure you want to clear the conversation history?[/bold {WARNING_COLOR}]",
        default=False,
    ):
        try:
            clear_history_from_mongodb()
            console.print(
                f"[bold {SUCCESS_COLOR}]✅ History cleared successfully![/bold {SUCCESS_COLOR}]"
            )
        except Exception as e:
            console.print(
                f"[bold {ERROR_COLOR}]❌ Error clearing history: {e}[/bold {ERROR_COLOR}]"
            )
    else:
        console.print(
            f"[{SYSTEM_DIM_STYLE}]History clearing cancelled.[/{SYSTEM_DIM_STYLE}]"
        )


class CommandHandler:
    def __init__(self, console: Console):
        self.console = console
        self.commands = {
            "/help": self._execute_help,
            "/clear": self._execute_clear,
            "/exit": self._execute_exit,
            "/quit": self._execute_exit,
        }

    def _execute_help(self):
        _print_help(self.console)
        return True  # Continue running

    def _execute_clear(self):
        _handle_clear(self.console)
        return True  # Continue running

    def _execute_exit(self):
        self.console.print(f"[{SYSTEM_DIM_STYLE}]Goodbye! 👋[/{SYSTEM_DIM_STYLE}]")
        return False  # Stop running

    def handle(self, command: str) -> bool:
        """
        Handles a user command.
        Returns:
            bool: True if the CLI loop should continue, False if it should exit.
        """
        if command in self.commands:
            return self.commands[command]()
        else:
            self.console.print(
                f"[{WARNING_COLOR}]Unknown command: {command}[/{WARNING_COLOR}]"
            )
            self.console.print(
                f"[{SYSTEM_DIM_STYLE}]Type /help to see available commands.[/{SYSTEM_DIM_STYLE}]"
            )
            return True  # Continue running
