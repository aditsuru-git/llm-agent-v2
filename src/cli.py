import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from langchain_core.messages import HumanMessage

# Import our main application and config
from src.main import app
from src.persona import persona_name

# --- Import the CommandHandler ---
from src.commands.handler import CommandHandler
from src.config import (
    AI_COLOR,
    USER_COLOR,
    THEME_COLOR_PRIMARY,
    NEUTRAL_COLOR,
    SYSTEM_DIM_STYLE,
    WARNING_COLOR,
    ERROR_COLOR,
)

# Rich console for beautiful output
console = Console()


class AIAssistantCLI:
    def __init__(self):
        self.ai_name = persona_name
        # --- CHANGE: Initialize the command handler ---
        self.command_handler = CommandHandler(console)

    def print_banner(self):
        """Display a beautiful startup banner"""
        banner_text = Text()
        banner_text.append(f"{self.ai_name}", style=f"bold {AI_COLOR}")

        banner_panel = Panel(
            Align.center(banner_text),
            border_style=THEME_COLOR_PRIMARY,
            title=f"[bold {NEUTRAL_COLOR}]Welcome[/bold {NEUTRAL_COLOR}]",
            title_align="center",
        )
        console.print()
        console.print(banner_panel)
        console.print()

    # --- CHANGE: The print_help and handle_clear methods are now moved ---
    # to the command handler. They can be removed from this class.

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
            self.print_banner()
            # --- CHANGE: Use the command handler to show initial help ---
            self.command_handler.handle("/help")

            console.print(
                f"[{SYSTEM_DIM_STYLE}]Type your message below or use commands. {self.ai_name} is ready to help![/{SYSTEM_DIM_STYLE}]"
            )

            while True:
                user_input = self.get_user_input()

                if user_input is None:
                    break
                if not user_input:
                    continue

                # --- CHANGE: Refactored command handling ---
                if user_input.startswith("/"):
                    should_continue = self.command_handler.handle(user_input.lower())
                    if not should_continue:
                        break
                    continue

                # Process AI request (this logic is unchanged)
                try:
                    spinner_text = Text(
                        f" {self.ai_name} is typing...", style=THEME_COLOR_PRIMARY
                    )
                    spinner = Spinner("dots", text=spinner_text)
                    with Live(
                        spinner, console=console, transient=True, refresh_per_second=20
                    ):
                        state = app.invoke(
                            {"messages": [HumanMessage(content=user_input)]}
                        )

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
                f"[{SYSTEM_DIM_STYLE}]Thank you for using V2! 🚀[/{SYSTEM_DIM_STYLE}]"
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
