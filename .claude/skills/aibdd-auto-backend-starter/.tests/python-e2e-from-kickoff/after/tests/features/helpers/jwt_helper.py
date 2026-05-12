import jwt


class JwtHelper:
    SECRET = "test-secret-key"
    ALGORITHM = "HS256"

    def generate_token(self, player_name: str) -> str:
        payload = {"player_name": player_name}
        return jwt.encode(payload, self.SECRET, algorithm=self.ALGORITHM)
