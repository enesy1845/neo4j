import threading
import sys
import platform

class InputHandler:
    def __init__(self, allowed_chars):
        self.allowed_chars = allowed_chars
        self._input_buffer = []
        self._enter_pressed = threading.Event()

    def get_input(self):
        # Buffer ve event resetlenir
        self._input_buffer.clear()
        self._enter_pressed.clear()

        # Enter tuşuna basılana kadar bekleyen bir thread başlatılır
        threading.Thread(target=self._listen_input).start()

        # Enter tuşuna basılana kadar bekler
        self._enter_pressed.wait()

        # Girdiği birleştir ve döndür
        result = ''.join(self._input_buffer)
        print()  # Yeni satıra geçiş
        return result

    def get_char(self):
        """Kullanıcıdan non-blocking şekilde karakter okur."""
        if platform.system() == 'Windows':
            import msvcrt
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                return char
        else:
            # Unix tabanlı sistemler için
            import sys, select, tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(sys.stdin.fileno())
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    char = sys.stdin.read(1)
                    return char
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    def _listen_input(self):
        while not self._enter_pressed.is_set():
            char = self.get_char()
            if char:
                if char == '\r' or char == '\n':  # Enter tuşuna basıldığında
                    self._enter_pressed.set()
                elif char == '\x08':  # Backspace tuşu
                    if self._input_buffer:
                        self._input_buffer.pop()
                        self._display_input()
                elif char in self.allowed_chars:  # İzin verilen karakterler
                    self._input_buffer.append(char)
                    self._display_input()

    def _display_input(self):
        # İmleci satır başına getirip buffer'ı ekrana yazdırır
        sys.stdout.write('\r' + ''.join(self._input_buffer) + " ")
        sys.stdout.flush()
        sys.stdout.write('\r' + ''.join(self._input_buffer))
        sys.stdout.flush()
