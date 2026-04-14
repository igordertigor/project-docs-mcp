import os
import json
import itertools
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from sentence_transformers import SentenceTransformer
from mcp.server.fastmcp import FastMCP
from hnswlib import Index
from typer import Typer

app = Typer()


@app.command("index")
def index():
    path = get_knowledge_path()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    with vector_index() as (idx, toc):
        for batch in itertools.batched(path.rglob("*.md"), 10):
            files = list(batch)
            texts = [f.read_text() for f in files]
            embeddings = model.encode(texts)
            for fname, emb in zip(files, embeddings):
                i = toc.setdefault(str(fname), len(toc))
                idx.add_items(emb, i)


@app.command("mcp")
def mcp():
    server = FastMCP("know", json_response=True)
    model = SentenceTransformer("all-MiniLM-L6-v2")


    @server.tool()
    def search_project_knowledge(
        topic: str, limit: int = 5, threshold: float = 0.5
    ) -> list[str]:
        """Search the project's knowledge base for content related to "topic".

        Args;
            topic: Brief description of what to search for
            limit: maximum number of items to retrieve
            threshold: suppress items with cosine distance larger than this threshold

        Returns:
            list of filenames (ordered by relevance)
        """
        with vector_index() as (idx, toc):
            inv_toc = {v: k for k, v in toc.items()}
            query = model.encode(topic)
            neighbors, distances = idx.knn_query(query, k=min(limit, len(toc)))
            return [
                inv_toc[n] for n, d in zip(neighbors[0], distances[0]) if d < threshold
            ]

    @server.tool()
    def store_project_knowledge(title: str, text: str) -> Path:
        """Store new project knowledge in the project's knowledge base

        Args:
            title: Title of the note
            text: descriptive text of the note

        Returns:
            Path of the stored model
        """
        with vector_index() as (idx, toc):
            path = get_knowledge_path() / f"{title}.md"
            i = 0
            while path.exists():
                path = get_knowledge_path() / f"{title}-{i}.md"
                i += 1
            text = f"# {title}\n\n{text}"
            path.write_text(text)
            emb = model.encode(text)
            i = toc.setdefault(str(path), len(toc))
            idx.add_items(emb, i)
            return path

    server.run(transport="stdio")


def get_knowledge_path() -> Path:
    return Path(os.environ.get("KNOWLEDGE_PATH", "docs"))


def get_index_file() -> Path:
    return Path(os.environ.get("KNOWLEDGE_INDEX_FILE", ".knowledge"))


def get_toc_file() -> Path:
    return Path(os.environ.get("KNOWLEDGE_TOC", ".knowledge-toc"))


@contextmanager
def vector_index() -> Generator[tuple[Index, dict[str, int]], None, None]:
    idx = Index("cosine", 384)
    index_file = get_index_file()
    toc_file = get_toc_file()
    if toc_file.exists():
        toc = json.loads(toc_file.read_text())
    else:
        toc = {}
    if index_file.exists():
        idx.load_index(str(index_file))
    else:
        idx.init_index(1000)
    idx.set_ef(10)  # Set search quality parameter
    try:
        yield idx, toc
    finally:
        idx.save_index(str(index_file))
        toc_file.write_text(json.dumps(toc))
