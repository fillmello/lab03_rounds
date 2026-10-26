class ServiceError(Exception):
    """Erro de regra de negócio; o controller o converte em resposta HTTP."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
