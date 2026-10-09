"""
Enigma M3 Cipher Machine Implementation (Historical Wehrmacht / Luftwaffe Standard).
Features:
- Rotors I, II, III, IV, V with authentic wiring and turnover notches.
- Double-stepping anomaly simulation.
- Reflectors UKW-B and UKW-C.
- Ring settings (Ringstellung) and Ground settings (Grundstellung / Rotor starting positions).
- Plugboard (Steckerbrett) letter pair swapping.
- Reciprocal operation: Encryption and Decryption are identical given the same initial settings.
"""

from .base import clean_alphabet

ROTOR_WIRINGS = {
    "I":   {"wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
    "II":  {"wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
    "III": {"wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"},
    "IV":  {"wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB", "notch": "J"},
    "V":   {"wiring": "VZBRGITYUPSDNHLXAWMJQOFECK", "notch": "Z"},
}

REFLECTORS = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

class Rotor:
    def __init__(self, rotor_type: str, ring_setting: int = 1, initial_pos: str = 'A'):
        data = ROTOR_WIRINGS.get(rotor_type, ROTOR_WIRINGS["I"])
        self.wiring = data["wiring"]
        self.notch = data["notch"]
        self.ring_setting = (ring_setting - 1) % 26
        self.position = (ord(initial_pos.upper()) - ord('A')) % 26

    @property
    def current_char(self) -> str:
        return chr(self.position + ord('A'))

    def is_at_notch(self) -> bool:
        return chr(self.position + ord('A')) == self.notch

    def step(self):
        self.position = (self.position + 1) % 26

    def forward(self, c_val: int) -> int:
        shift = (self.position - self.ring_setting + 26) % 26
        contact_in = (c_val + shift) % 26
        wire_out = ord(self.wiring[contact_in]) - ord('A')
        return (wire_out - shift + 26) % 26

    def backward(self, c_val: int) -> int:
        shift = (self.position - self.ring_setting + 26) % 26
        contact_in = (c_val + shift) % 26
        wire_out = self.wiring.index(chr(contact_in + ord('A')))
        return (wire_out - shift + 26) % 26

class EnigmaMachine:
    def __init__(
        self,
        rotors: list[str] = None,          # e.g. ["I", "II", "III"] (Left, Middle, Right)
        reflector: str = "B",
        ring_settings: list[int] = None,   # [1, 1, 1]
        initial_positions: str = "AAA",    # "AAA"
        plugboard_pairs: str = ""          # e.g. "AB CD EF"
    ):
        if rotors is None:
            rotors = ["I", "II", "III"]
        if ring_settings is None:
            ring_settings = [1, 1, 1]

        self.reflector_wiring = REFLECTORS.get(reflector, REFLECTORS["B"])
        self.rotors_config = list(rotors)
        self.ring_settings = list(ring_settings)
        self.initial_positions = initial_positions.upper()
        self.plugboard_str = plugboard_pairs

        self._init_rotors()
        self._init_plugboard(plugboard_pairs)

    def _init_rotors(self):
        init_pos = (self.initial_positions + "AAA")[:3]
        self.left_rotor = Rotor(self.rotors_config[0], self.ring_settings[0], init_pos[0])
        self.middle_rotor = Rotor(self.rotors_config[1], self.ring_settings[1], init_pos[1])
        self.right_rotor = Rotor(self.rotors_config[2], self.ring_settings[2], init_pos[2])

    def _init_plugboard(self, pairs_str: str):
        self.plugboard = {chr(i): chr(i) for i in range(ord('A'), ord('Z') + 1)}
        if not pairs_str:
            return
        tokens = pairs_str.upper().split()
        for token in tokens:
            if len(token) == 2 and token[0].isalpha() and token[1].isalpha():
                a, b = token[0], token[1]
                self.plugboard[a] = b
                self.plugboard[b] = a

    def step(self):
        """
        Enigma stepping mechanism, including historical double-stepping anomaly:
        - If the middle rotor is on its notch, it steps AND the left rotor steps.
        - Else if the right rotor is on its notch, the middle rotor steps.
        - The right rotor always steps.
        """
        middle_at_notch = self.middle_rotor.is_at_notch()
        right_at_notch = self.right_rotor.is_at_notch()

        if middle_at_notch:
            self.middle_rotor.step()
            self.left_rotor.step()
        elif right_at_notch:
            self.middle_rotor.step()

        self.right_rotor.step()

    def process_char(self, char: str) -> tuple[str, dict]:
        """
        Processes a single character through the Enigma machine.
        Returns the output character and an inspection trace of rotor positions.
        """
        c = char.upper()
        if not ('A' <= c <= 'Z'):
            return c, {}

        # 1. Step rotors
        self.step()

        # Capture rotor positions after step
        step_state = {
            "left": self.left_rotor.current_char,
            "middle": self.middle_rotor.current_char,
            "right": self.right_rotor.current_char,
        }

        # 2. Pass through plugboard
        val = ord(self.plugboard[c]) - ord('A')

        # 3. Forward through rotors (Right -> Middle -> Left)
        val = self.right_rotor.forward(val)
        val = self.middle_rotor.forward(val)
        val = self.left_rotor.forward(val)

        # 4. Reflector
        val = ord(self.reflector_wiring[val]) - ord('A')

        # 5. Backward through rotors (Left -> Middle -> Right)
        val = self.left_rotor.backward(val)
        val = self.middle_rotor.backward(val)
        val = self.right_rotor.backward(val)

        # 6. Pass through plugboard
        out_char = self.plugboard[chr(val + ord('A'))]
        return out_char, step_state

    def process_text(self, text: str) -> tuple[str, list[dict]]:
        clean_t = clean_alphabet(text)
        result = []
        traces = []
        for ch in clean_t:
            out_ch, trace = self.process_char(ch)
            result.append(out_ch)
            traces.append(trace)
        return "".join(result), traces

def process(
    text: str,
    rotors: list[str] = None,
    reflector: str = "B",
    ring_settings: list[int] = None,
    initial_positions: str = "AAA",
    plugboard_pairs: str = ""
) -> str:
    """Helper function to run Enigma on text."""
    machine = EnigmaMachine(
        rotors=rotors,
        reflector=reflector,
        ring_settings=ring_settings,
        initial_positions=initial_positions,
        plugboard_pairs=plugboard_pairs
    )
    res, _ = machine.process_text(text)
    return res
