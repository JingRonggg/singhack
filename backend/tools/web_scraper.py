import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Set
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from collections import defaultdict

from backend.util.config import load_config
from backend.schemas.rules import RulesSchema, RulesExtractionSchema
from datetime import datetime


def get_web_content(website_urls: list[str], max_pages: int = 10) -> dict[str, str]:
    """
    Fetches and returns the markdown content of the specified website URLs.
    Also crawls linked pages on the same domain.
    Args:
    website_urls (list[str]): The URLs of the websites to scrape.
    max_pages (int): Maximum number of pages to crawl per domain (default: 10).
    Returns:
    dict[str, str]: A dictionary mapping each URL to its content.
    """
    content_dict = {}
    visited_urls: Set[str] = set()

    def get_domain(url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def get_links(soup, base_url: str, base_domain: str) -> Set[str]:
        """Extract all links from the page that belong to the same domain."""
        links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(base_url, link["href"])
            if get_domain(full_url) == base_domain and full_url not in visited_urls:
                full_url = full_url.split("#")[0]
                links.add(full_url)
        return links

    def crawl_page(url: str, base_domain: str, remaining_pages: int) -> None:
        """Recursively crawl pages from the same domain."""
        if remaining_pages <= 0 or url in visited_urls:
            return

        visited_urls.add(url)

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            links = get_links(soup, url, base_domain)

            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()

            markdown_content = md(str(soup), heading_style="ATX")
            content_dict[url] = markdown_content

            for link in links:
                crawl_page(link, base_domain, remaining_pages - 1)
                if len(visited_urls) >= max_pages:
                    break

        except requests.exceptions.RequestException as e:
            content_dict[url] = f"Error fetching content: {str(e)}"

    for url in website_urls:
        base_domain = get_domain(url)
        crawl_page(url, base_domain, max_pages)

    return content_dict


def parsing_web_content_to_rules(
    web_content: dict[str, str],
) -> dict[str, dict[str, str]]:
    """
    Parses the web content and extracts relevant rules or information.
    Extraction is done with AI with a set format to parse it into a structured format.
    Combines all pages from the same domain into a single entry.
    Args:
    web_content (dict[str, str]): A dictionary mapping each URL to its content.
    Returns:
    dict[str, dict[str, str]]: The extracted rules or information grouped by domain.
    """
    configs = load_config()
    api_key = configs.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0.3,
    )
    structured_llm = llm.with_structured_output(RulesExtractionSchema)

    domain_content = defaultdict(list)
    for url, content in web_content.items():
        if not content.startswith("Error fetching content"):
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            domain_content[domain].append({"url": url, "content": content})

    result = {}

    for domain, pages in domain_content.items():
        combined_content = "\n\n---PAGE SEPARATOR---\n\n".join(
            [f"URL: {page['url']}\n\n{page['content'][:6000]}" for page in pages]
        )

        source_urls = list(set([page["url"] for page in pages]))

        system_message = SystemMessage(
            content="""You are a regulatory compliance expert.
Extract and consolidate rules and regulations from web content across multiple pages.
Extract clear, concise regulatory rules, guidelines, and requirements.
Number the rules sequentially starting from "1" as strings.
ONLY extract the rules field - other metadata will be added automatically."""
        )

        human_message = HumanMessage(
            content=f"""
Analyze the following web content from {len(pages)} page(s) on the same domain and extract regulatory rules and guidelines.

Important:
- Combine and consolidate rules from all pages provided
- Extract ONLY actual rules, regulations, guidelines, or requirements
- Remove duplicates and redundant information
- Number the rules sequentially starting from "1" as string keys
- Each rule should be a clear, concise statement
- Prioritize the most important and comprehensive rules

Web Content:
{combined_content[:15000]}

Extract at least 5 key rules if available.
"""
        )

        try:
            response = structured_llm.invoke([system_message, human_message])

            rules_schema = RulesSchema(
                created_at=int(datetime.now().timestamp()),
                rules=response.rules,
                source_urls=[domain],
            )

            # Convert to dict for result
            parsed_data = rules_schema.model_dump()

            print(f"Successfully parsed {len(pages)} pages from {domain}")
            print(f"Extracted {len(parsed_data['rules'])} rules")
            print(f"Ruleset ID: {parsed_data['ruleset_id']}")

            result[domain] = parsed_data

        except Exception as e:
            print(f"Error parsing content from {domain}: {str(e)}")
            # Create error schema with proper metadata
            error_schema = RulesSchema(
                created_at=int(datetime.now().timestamp()),
                rules={"error": f"Failed to parse: {str(e)}"},
                source_urls=source_urls,
            )
            result[domain] = error_schema.model_dump()

    return result


def web_scraper(extra_links: Optional[List[str]]) -> dict[str, dict[str, str]]:
    """
    A tool that scrapes web content from the provided URLs and extracts relevant rules or information.
    Args:
    None
    Returns:
    dict: The extracted rules or information from the websites.
    """
    LINKS = ["https://www.mas.gov.sg/regulation"]
    if extra_links:
        LINKS.extend(extra_links)

    web_content = get_web_content(LINKS)
    rules = parsing_web_content_to_rules(web_content)
    return rules
