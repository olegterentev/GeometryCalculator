class Parser:

    def __init__(self):
        self.command = ""
        self.tokens = []
        self.error = ""

    def tokenizer(self):
        i = 0
        while i < len(self.command):
            char = self.command[i]

            if char.isspace():
                i += 1
                continue

            if char == '(':
                self.tokens.append(("LPAREN", char))
                i += 1
                continue

            if char == ')':
                self.tokens.append(("RPAREN", char))
                i += 1
                continue

            if char == '=':
                self.tokens.append(("EQUAL", char))
                i += 1
                continue

            if char == ',':
                self.tokens.append(("COMMA", char))
                i += 1
                continue

            if char.isdigit() or char == '-':
                start = i
                fl = 0
                if char == '-':
                    i += 1
                    if i >= len(self.command) or not self.command[i].isdigit():
                        self.error = "ошибка ввода числа"
                        return
                while i < len(self.command) and (self.command[i].isdigit() or self.command[i] == '.'):
                    if self.command[i] == '.':
                        fl += 1
                    i += 1
                if fl > 1:
                    self.error = "ошибка ввода числа"
                    return
                self.tokens.append(("NUM", float(self.command[start:i])))
                continue

            if char.isalpha():
                start = i
                while i < len(self.command) and self.command[i].isalnum():
                    i += 1
                self.tokens.append(("IDENT", self.command[start:i]))
                continue

            self.error = f"Неизвестный символ: {char}"
            return
        self.tokens.append(("EOF", None))

    def expect(self):
        past_token_id = ""
        com_obj = {}
        arg = []

        for token in self.tokens:
            token_type = token[0]

            if past_token_id == "" and token_type == "IDENT":
                com_obj["label"] = token[1]
                past_token_id = "LABEL"
                continue

            if past_token_id == "LABEL":
                if token_type == "EQUAL":
                    past_token_id = "EQUAL"
                    continue
                if token_type == "LPAREN":
                    com_obj["operand"] = com_obj["label"]
                    com_obj["label"] = None
                    past_token_id = "LPAREN"
                    continue

            if past_token_id == "EQUAL" and token_type == "IDENT":
                com_obj["operand"] = token[1]
                past_token_id = "OPERAND"
                continue

            if past_token_id == "OPERAND" and token_type == "LPAREN":
                past_token_id = "LPAREN"
                continue

            if past_token_id == "LPAREN" and token_type == "RPAREN":
                past_token_id = "RPAREN"
                continue

            if past_token_id in ("LPAREN", "COMMA"):
                if token_type == "NUM":
                    arg.append(token[1])
                    past_token_id = "ARG"
                    continue
                if token_type == "IDENT":
                    arg.append(token[1])
                    past_token_id = "ARG"
                    continue

            if past_token_id == "ARG" and token_type == "COMMA":
                past_token_id = "COMMA"
                continue

            if past_token_id == "ARG" and token_type == "RPAREN":
                past_token_id = "RPAREN"
                continue

            if past_token_id == "RPAREN" and token_type == "EOF":
                com_obj["arg"] = arg
                return com_obj

            self.error = "Ошибка ввода, неправильная запись команды"
            return None

    def parse(self):
        self.tokens = []
        self.error = ""
        self.tokenizer()
        if self.error != "":
            return self.error
        obj = self.expect()
        if self.error != "":
            return self.error
        return obj
