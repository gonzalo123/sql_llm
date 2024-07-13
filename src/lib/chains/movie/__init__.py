from .chain import MovieChain


def get_chain(llm) -> MovieChain:
    return MovieChain(llm)


__all__ = ['get_chain']
