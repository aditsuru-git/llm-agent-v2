import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from langchain_core.messages import HumanMessage

# Import our main application and config
from src.main import app
from src.persona import persona_name
from src.db.persistence import clear_history_from_mongodb
from src.config import (
    AI_COLOR,
    USER_COLOR,
    THEME_COLOR_PRIMARY,
    THEME_COLOR_SECONDARY,
    SUCCESS_COLOR,
    WARNING_COLOR,
    ERROR_COLOR,
    NEUTRAL_COLOR,
    SYSTEM_DIM_STYLE,
)

# Rich console for beautiful output
console = Console()


class AIAssistantCLI:
    def __init__(self):
        self.ai_name = persona_name

    def print_banner(self):
        """Display a beautiful startup banner"""
        banner_text = Text()
        banner_text.append("🤖 ", style=f"bold {THEME_COLOR_PRIMARY}")
        banner_text.append(f"{self.ai_name}", style=f"bold {AI_COLOR}")
        banner_text.append(" Assistant", style=f"bold {THEME_COLOR_PRIMARY}")

        banner_panel = Panel(
            Align.center(banner_text),
            border_style=THEME_COLOR_PRIMARY,
            title=f"[bold {NEUTRAL_COLOR}]Welcome[/bold {NEUTRAL_COLOR}]",
            title_align="center",
        )
        console.print()
        console.print(banner_panel)
        console.print()

    def print_help(self):
        """Display help information"""
        help_table = Table(
            show_header=True, header_style=f"bold {THEME_COLOR_SECONDARY}"
        )
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
        console.print(help_panel)

    def get_user_input(self) -> Optional[str]:
        """Get user input with beautiful styling"""
        try:
            user_text = Text()
            user_text.append("You", style=f"bold {USER_COLOR}")
            user_text.append(": ", style=NEUTRAL_COLOR)

            console.print()
            console.print(user_text, end="")

            user_input = input().strip()
            return user_input

        except EOFError:
            console.print(
                f"\n[{SYSTEM_DIM_STYLE}]Input stream ended. Goodbye![/{SYSTEM_DIM_STYLE}]"
            )
            return None
        except KeyboardInterrupt:
            console.print(f"\n[{WARNING_COLOR}]Interrupted by user[/{WARNING_COLOR}]")
            if Confirm.ask(
                f"[bold {ERROR_COLOR}]Are you sure you want to exit?[/bold {ERROR_COLOR}]"
            ):
                return None
            else:
                return ""  # Continue the loop

    def print_ai_response(self, content: str):
        """Print AI response with character name and styling"""
        ai_text = Text()
        ai_text.append(f"{self.ai_name}", style=f"bold {AI_COLOR}")
        ai_text.append(": ", style=NEUTRAL_COLOR)
        ai_text.append(content, style=NEUTRAL_COLOR)

        response_panel = Panel(ai_text, border_style=AI_COLOR, padding=(0, 1))
        console.print(response_panel)

    def handle_clear_command(self) -> bool:
        """Handle the /clear command with confirmation"""
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
                return True
            except Exception as e:
                console.print(
                    f"[bold {ERROR_COLOR}]❌ Error clearing history: {e}[/bold {ERROR_COLOR}]"
                )
                return False
        else:
            console.print(
                f"[{SYSTEM_DIM_STYLE}]History clearing cancelled.[/{SYSTEM_DIM_STYLE}]"
            )
            return False

    def print_system_message(self, message: str, style: str = THEME_COLOR_PRIMARY):
        """Print system messages with consistent styling"""
        system_text = Text()
        system_text.append("System", style=f"bold {style}")
        system_text.append(": ", style=NEUTRAL_COLOR)
        system_text.append(message, style=style)
        console.print(system_text)

    def print_error(self, error_msg: str):
        """Print error messages"""
        error_panel = Panel(
            f"[bold {ERROR_COLOR}]Error:[/{ERROR_COLOR}] {error_msg}",
            border_style=ERROR_COLOR,
        )
        console.print(error_panel)

    def run(self):
        """Main CLI loop"""
        try:
            # Show startup banner and help
            self.print_banner()
            self.print_help()

            console.print(
                f"[{SYSTEM_DIM_STYLE}]Type your message below or use commands. {self.ai_name} is ready to help![/{SYSTEM_DIM_STYLE}]"
            )

            while True:
                # Get user input
                user_input = self.get_user_input()

                # Handle special cases
                if user_input is None:  # EOF or exit confirmation
                    break

                if not user_input:  # Empty input or cancelled interrupt
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command == "/help":
                        console.print()
                        self.print_help()
                        continue

                    elif command == "/clear":
                        self.handle_clear_command()
                        continue

                    elif command in ["/exit", "/quit"]:
                        console.print(
                            f"[{SYSTEM_DIM_STYLE}]Goodbye! 👋[/{SYSTEM_DIM_STYLE}]"
                        )
                        break

                    else:
                        console.print(
                            f"[{WARNING_COLOR}]Unknown command: {user_input}[/{WARNING_COLOR}]"
                        )
                        console.print(
                            f"[{SYSTEM_DIM_STYLE}]Type /help to see available commands.[/{SYSTEM_DIM_STYLE}]"
                        )
                        continue

                # Process AI request
                try:
                    spinner_text = Text(
                        f" {self.ai_name} is thinking...", style=THEME_COLOR_PRIMARY
                    )
                    spinner = Spinner("dots", text=spinner_text)
                    with Live(
                        spinner, console=console, transient=True, refresh_per_second=20
                    ):
                        state = app.invoke(
                            {"messages": [HumanMessage(content=user_input)]}
                        )

                    # Display AI response
                    ai_response = state["messages"][-1].content
                    self.print_ai_response(ai_response)

                except KeyboardInterrupt:
                    console.print(
                        f"\n[{WARNING_COLOR}]Processing interrupted[/{WARNING_COLOR}]"
                    )
                    continue

                except Exception as e:
                    self.print_error(f"Failed to process request: {str(e)}")
                    continue

        except KeyboardInterrupt:
            console.print(
                f"\n[{WARNING_COLOR}]Final interrupt - shutting down...[/{WARNING_COLOR}]"
            )

        finally:
            console.print()
            console.print(
                f"[{SYSTEM_DIM_STYLE}]Thank you for using the AI Assistant! 🚀[/{SYSTEM_DIM_STYLE}]"
            )


def main():
    """Entry point for the CLI"""
    try:
        cli = AIAssistantCLI()
        cli.run()
    except Exception as e:
        console.print(f"[bold {ERROR_COLOR}]Fatal error: {e}[/bold {ERROR_COLOR}]")
        sys.exit(1)


if __name__ == "__main__":
    main()
