class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def parse(self):
        return self.expression()

    def expression(self):
        node = self.term()
        while self.current_token() in ("PLUS", "MINUS"):
            token = self.current_token()
            self.eat(token)
            node = (token, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token() in ("MULTIPLY", "DIVIDE"):
            token = self.current_token()
            self.eat(token)
            node = (token, node, self.factor())
        return node

    def factor(self):
        token = self.current_token()
        if token == "NUMBER":
            self.eat("NUMBER")
            return ("NUMBER", token[1])
        elif token == "LPAREN":
            self.eat("LPAREN")
            node = self.expression()
            self.eat("RPAREN")
            return node
        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def current_token(self):
        return self.tokens[self.current_token_index][0]

    def eat(self, token_type):
        if self.current_token() == token_type:
            self.current_token_index += 1
        else:
            raise SyntaxError(
                f"Expected token: {token_type}, got: {self.current_token()}"
            )
