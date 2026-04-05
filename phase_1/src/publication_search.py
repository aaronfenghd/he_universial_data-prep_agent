"""Publication search layer with explicit PubMed-first, web-fallback behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests

from .task_models import TaskInput


@dataclass
class PublicationRecord:
    title: str
    authors: str
    journal: str
    year: str
    pmid: str = ""
    doi: str = ""
    source_link: str = ""
    source: str = "pubmed"  # pubmed or web_fallback


class PublicationSearcher:
    """Searches publications with PubMed primary and generic web fallback."""

    PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    PUBMED_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    CROSSREF_WORKS = "https://api.crossref.org/works"

    def search(
        self,
        task: TaskInput,
        prep_direction: dict[str, Any],
        min_results: int = 5,
    ) -> tuple[list[PublicationRecord], dict[str, Any]]:
        query = self._build_query(task, prep_direction)

        pubmed_results = self._search_pubmed(query, retmax=max(min_results, 8))
        used_web_fallback = len(pubmed_results) < min_results

        all_results = pubmed_results[:]
        web_results: list[PublicationRecord] = []

        if used_web_fallback:
            web_results = self._search_web_fallback(query, limit=min_results - len(pubmed_results) + 4)
            all_results.extend(web_results)

        meta = {
            "query": query,
            "pubmed_count": len(pubmed_results),
            "web_fallback_count": len(web_results),
            "used_web_fallback": used_web_fallback,
        }
        return all_results, meta

    def _build_query(self, task: TaskInput, prep_direction: dict[str, Any]) -> str:
        base = task.to_query_text()
        prep_hint = (prep_direction.get("full_text", "") or "")[:300]
        return " ".join([base, prep_hint]).strip()

    def _search_pubmed(self, query: str, retmax: int = 10) -> list[PublicationRecord]:
        records: list[PublicationRecord] = []

        esearch_resp = requests.get(
            self.PUBMED_ESEARCH,
            params={
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": retmax,
                "sort": "relevance",
            },
            timeout=20,
        )
        esearch_resp.raise_for_status()
        id_list = esearch_resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return records

        summary_resp = requests.get(
            self.PUBMED_ESUMMARY,
            params={
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
            },
            timeout=20,
        )
        summary_resp.raise_for_status()
        summary_json = summary_resp.json()

        for pmid in id_list:
            item = summary_json.get("result", {}).get(pmid, {})
            title = item.get("title", "").strip()
            if not title:
                continue
            authors = ", ".join(a.get("name", "") for a in item.get("authors", [])[:5] if a.get("name"))
            journal = item.get("fulljournalname", "") or item.get("source", "")
            year = str(item.get("pubdate", "")).split(" ")[0]
            article_ids = item.get("articleids", [])
            doi = ""
            for aid in article_ids:
                if aid.get("idtype") == "doi":
                    doi = aid.get("value", "")
                    break

            records.append(
                PublicationRecord(
                    title=title,
                    authors=authors,
                    journal=journal,
                    year=year,
                    pmid=pmid,
                    doi=doi,
                    source_link=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    source="pubmed",
                )
            )
        return records

    def _search_web_fallback(self, query: str, limit: int = 5) -> list[PublicationRecord]:
        """Generic web fallback via Crossref metadata search."""
        resp = requests.get(
            self.CROSSREF_WORKS,
            params={"query": query, "rows": max(limit, 1)},
            timeout=20,
        )
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])

        results: list[PublicationRecord] = []
        for item in items[:limit]:
            title_list = item.get("title", [])
            title = title_list[0].strip() if title_list else ""
            if not title:
                continue

            author_list = item.get("author", [])
            authors = ", ".join(
                f"{a.get('given', '').strip()} {a.get('family', '').strip()}".strip()
                for a in author_list[:5]
            )
            journal = ""
            container = item.get("container-title", [])
            if container:
                journal = container[0]

            year = ""
            issued = item.get("issued", {}).get("date-parts", [])
            if issued and issued[0]:
                year = str(issued[0][0])

            doi = item.get("DOI", "")
            source_link = f"https://doi.org/{doi}" if doi else item.get("URL", "")

            results.append(
                PublicationRecord(
                    title=title,
                    authors=authors,
                    journal=journal,
                    year=year,
                    pmid="",
                    doi=doi,
                    source_link=source_link,
                    source="web_fallback",
                )
            )
        return results
