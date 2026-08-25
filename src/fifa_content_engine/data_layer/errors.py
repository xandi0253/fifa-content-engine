"""Exceções específicas do Data Layer."""


class DataLayerError(Exception):
    """Erro base para qualquer falha no Data Layer."""


class RecordNotFoundError(DataLayerError):
    """O registro solicitado não foi encontrado no armazenamento."""
