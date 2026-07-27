import reflex as rx


class State(rx.State):
    input_text: str = ""

    def set_input_text(self, value: str):
        self.input_text = value
