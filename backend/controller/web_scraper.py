from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Dict, Optional
import logging

from backend.tools.web_scraper import web_scraper
from backend.schemas.rules import RulesSchema
from backend.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["web-scraper"])


class WebScraperRequest(BaseModel):
    """Request model for web scraper endpoint."""

    urls: Optional[List[str]] = None

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that all URLs are properly formatted."""
        if v is None or len(v) == 0:
            return None

        if len(v) > 10:
            raise ValueError("Maximum 10 URLs allowed per request")

        validated_urls = []
        for url in v:
            url = url.strip()
            if not url:
                continue

            # Basic URL validation
            if not url.startswith(("http://", "https://")):
                raise ValueError(
                    f"Invalid URL scheme: {url}. Must start with http:// or https://"
                )

            try:
                HttpUrl(url)
                validated_urls.append(url)
            except Exception:
                raise ValueError(f"Invalid URL format: {url}")

        if not validated_urls:
            return None

        return validated_urls


@router.post(
    "/scrape",
    response_model=Dict[str, RulesSchema],
    status_code=status.HTTP_200_OK,
    summary="Scrape web content and extract rules",
    description="Scrapes provided URLs and extracts regulatory rules and guidelines using AI. Returns a dictionary with domains as keys and RulesSchema as values.",
)
async def scrape_web_content(
    request: Optional[WebScraperRequest] = None,
) -> Dict[str, RulesSchema]:
    """
    Endpoint to scrape web content and extract rules.

    Args:
        request: WebScraperRequest containing optional list of URLs to scrape

    Returns:
        Dict[str, RulesSchema]: Dictionary mapping domain URLs to their extracted rules

    Raises:
        HTTPException: If scraping fails or validation errors occur
    """
    try:
        # Run the web scraper with optional URLs
        rules_data = web_scraper(extra_links=request.urls)

        if not rules_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No rules extracted from the provided URLs",
            )

        # Convert dict values to RulesSchema objects for validation and return
        validated_data = {}
        for domain, rules_dict in rules_data.items():
            try:
                validated_data[domain] = RulesSchema(**rules_dict)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error validating rules for {domain}: {str(e)}",
                )

        # Store all extracted rules in the database
        try:
            db_service = DatabaseService()
            stored_count = 0

            for domain, rules_schema in validated_data.items():
                # Iterate through all rules in the schema
                for rule_key, rule in rules_schema.rules.items():
                    try:
                        db_service.store_rule(rule)
                        stored_count += 1
                        logger.info(f"Stored rule {rule.rule_id} from {domain}")
                    except Exception as rule_error:
                        # Log error but continue with other rules
                        logger.error(
                            f"Failed to store rule {rule.rule_id} from {domain}: {rule_error}"
                        )

            logger.info(f"Successfully stored {stored_count} rules in database")

        except Exception as db_error:
            # Log database error but don't fail the request - rules are still returned
            logger.error(f"Database storage error (rules still returned): {db_error}")

        return validated_data

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while scraping: {str(e)}",
        )
