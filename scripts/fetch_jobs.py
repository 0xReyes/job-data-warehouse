import asyncio
import json
import logging
import os
import re
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import aiohttp
import psycopg2
from bs4 import BeautifulSoup, NavigableString
from psycopg2.extras import RealDictCursor
from pydantic import (BaseModel, Field, HttpUrl, ValidationError,
                    field_validator)
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                    wait_exponential)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Utility Functions ---

def parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parse various date string formats into a standard date object.
    Returns None if parsing fails.
    """
    if not date_str:
        return None
    try:
        # Handle ISO 8601 format (e.g., "2025-07-12T09:13:31.531Z")
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except (ValueError, TypeError):
        pass

    patterns = [
        r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})',
        r'(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})',
        r'(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                parts = match.groupdict()
                return date(int(parts['year']), int(parts['month']), int(parts['day']))
            except (ValueError, KeyError):
                continue
    
    if "today" in date_str.lower() or "posted just" in date_str.lower():
        return datetime.now(timezone.utc).date()
    
    logging.debug(f"Could not parse date from string: '{date_str}'")
    return None

# --- Data Validation Models ---

class Job(BaseModel):
    title: str
    company: Optional[str] = None
    description: str
    source_url: HttpUrl
    ats_platform: str
    # Changed to Optional[Any] to handle multiple location formats gracefully.
    # Validation is now handled by the _format_location function.
    location_raw: Optional[Any] = None
    employment_type: Optional[str] = None
    date_posted_raw: Optional[str] = None

    @field_validator('source_url', mode='before')
    @classmethod
    def pre_validate_url(cls, v):
        return str(v)

class DBJob(BaseModel):
    title: str
    link: HttpUrl
    company_name: Optional[str]
    location: Optional[str]
    description: Optional[str]
    employment_type: Optional[str]
    date_posted: Optional[date]

    @field_validator('link', mode='before')
    @classmethod
    def pre_validate_db_url(cls, v):
        return str(v)

# --- Database Management ---

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_config = {
            'host': os.getenv('DB_HOST', 'ep-rapid-pine-ae2hgxrj-pooler.c-2.us-east-2.aws.neon.tech'),
            'database': os.getenv('DB_NAME', 'neondb'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'sslmode': "require"
        }
        if not self.db_config['user'] or not self.db_config['password']:
            raise ValueError("Database credentials not found in environment variables.")

    def connect(self):
        try:
            logging.info(f"Connecting to database host {self.db_config['host']}...")
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logging.info("Database connection successful.")
        except psycopg2.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def _format_location(self, location_data: Optional[Any]) -> Optional[str]:
        if not location_data: return None
        
        # If it's a list (e.g., from Lever), process the first valid item.
        if isinstance(location_data, list):
            if not location_data: return None
            location_data = location_data[0]

        if isinstance(location_data, str): return location_data
        
        if isinstance(location_data, dict):
            # Handle standard LD+JSON 'Place' schema
            if location_data.get('@type') == 'Place':
                address = location_data.get('address', {})
                if isinstance(address, dict):
                    parts = [address.get('addressLocality'), address.get('addressRegion'), address.get('addressCountry')]
                    return ", ".join(filter(None, parts)) if any(parts) else "Remote"
            return str(location_data)
            
        return str(location_data)

    def _clean_job_for_db(self, job: Job) -> DBJob:
        return DBJob(
            title=job.title[:255],
            link=job.source_url,
            company_name=job.company[:255] if job.company else None,
            location=self._format_location(job.location_raw),
            description=job.description,
            employment_type=job.employment_type[:50] if job.employment_type else None,
            date_posted=parse_date(job.date_posted_raw)
        )

    def sync_jobs(self, jobs: List[Job]):
        if not self.conn or not self.cursor:
            logging.error("Cannot sync jobs. No active database connection.")
            return

        # Corrected INSERT query: Removed dateupdated from INSERT, uses 'dateupdated' on UPDATE.
        insert_query = """
        INSERT INTO job_postings (
            title, link, company_name, location, description, employment_type, date_posted
        ) VALUES (
            %(title)s, %(link)s, %(company_name)s, %(location)s, %(description)s, %(employment_type)s, %(date_posted)s
        ) ON CONFLICT (link) DO UPDATE SET
            title = EXCLUDED.title,
            company_name = EXCLUDED.company_name,
            location = EXCLUDED.location,
            description = EXCLUDED.description,
            employment_type = EXCLUDED.employment_type,
            date_posted = EXCLUDED.date_posted,
            dateupdated = NOW();
        """
        inserted, updated, errors = 0, 0, 0
        for job in jobs:
            try:
                self.cursor.execute("SELECT id FROM job_postings WHERE link = %s", (str(job.source_url),))
                exists = self.cursor.fetchone()
                cleaned_job_dict = self._clean_job_for_db(job).model_dump(mode='json')
                self.cursor.execute(insert_query, cleaned_job_dict)
                if exists: updated += 1
                else: inserted += 1
                self.conn.commit()
            except (psycopg2.Error, ValidationError) as e:
                errors += 1
                logging.error(f"Error processing job '{job.title}'", exc_info=True)
                self.conn.rollback()
        print(jobs)
        logging.info(f"--- Database Sync Summary ---")
        logging.info(f"New jobs: {inserted}, Updated jobs: {updated}, Errors: {errors}")

    def close(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        logging.info("Database connection closed.")

# --- Core Scraper Class ---
class JobScraper:
    def __init__(self, config_path="scripts/config.json"):
        self.serp_api_key = os.getenv("SERPER_API_KEY")
        if not self.serp_api_key:
            raise ValueError("SERPER_API_KEY environment variable not set.")

        self.config = self._load_config(config_path)
        self.ats_config = self.config.get("ATS_CONFIG", {})
        self.job_title_keywords = self.config.get("JOB_TITLE_KEYWORDS", [])
        self.remote_keywords = self.config.get("REMOTE_KEYWORDS", [])
        self.excluded_keywords = self.config.get("EXCLUDED_KEYWORDS", [])
        self.time_filter = self.config.get("SEARCH_SETTINGS", {}).get("time_filter", "qdr:d")

    def _load_config(self, filename: str) -> Dict[str, Any]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error with '{filename}': {e}")
            exit(1)

    def _build_search_query(self, job_title: str) -> str:
        remote_terms = " OR ".join(f'"{kw}"' for kw in self.remote_keywords)
        excluded_terms = " ".join(f'-"{kw}"' for kw in self.excluded_keywords)
        site_terms = " OR ".join(f"site:{conf['domain']}" for conf in self.ats_config.values())
        return f'"{job_title}" ({remote_terms}) {excluded_terms} ({site_terms})'

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
    async def _get_serp_results(self, session: aiohttp.ClientSession, query: str) -> List[str]:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "tbs": self.time_filter, "num": 100})
        headers = {'X-API-KEY': self.serp_api_key, 'Content-Type': 'application/json'}
        async with session.post(url, headers=headers, data=payload, timeout=20) as response:
            response.raise_for_status()
            data = await response.json()
            logging.info(f"Found {len(data.get('organic', []))} potential links for query: {query[:75]}...")
            return [item['link'] for item in data.get('organic', []) if 'link' in item]

    def _extract_text(self, soup: BeautifulSoup, selector: Optional[str]) -> Optional[str]:
        if not selector: return None
        element = soup.select_one(selector)
        return element.get_text(separator='\n', strip=True) if element else None
    
    def _find_config_for_url(self, url: str) -> Optional[Tuple[str, Dict]]:
        """Finds the best-matching ATS configuration for a given URL."""
        best_match = None
        max_len = -1
        for name, config in self.ats_config.items():
            domain = config['domain']
            if domain in url and len(domain) > max_len:
                max_len = len(domain)
                best_match = (name, config)
        return best_match

    async def _scrape_from_ld_json(self, soup: BeautifulSoup, url: str, ats_name: str) -> Optional[Job]:
        ld_json_script = soup.find('script', type='application/ld+json')
        if not ld_json_script: return None
        try:
            data = json.loads(ld_json_script.string)
            if isinstance(data, list):
                data = next((item for item in data if item.get('@type') == 'JobPosting'), data[0])
            if data.get('@type') != 'JobPosting': return None
            
            desc_html = data.get("description", "")
            desc_soup = BeautifulSoup(desc_html, 'html.parser')

            return Job(
                title=data.get("title"),
                company=data.get("hiringOrganization", {}).get("name"),
                description=desc_soup.get_text(separator='\n', strip=True),
                source_url=url,
                ats_platform=ats_name,
                location_raw=data.get("jobLocation"),
                employment_type=data.get("employmentType"),
                date_posted_raw=data.get("datePosted")
            )
        except (json.JSONDecodeError, ValidationError, TypeError, StopIteration) as e:
            logging.warning(f"LD+JSON parsing failed for {url}: {e}")
            return None

    async def _scrape_from_remix_context(self, soup: BeautifulSoup, url: str, ats_name: str) -> Optional[Job]:
        script_tag = soup.find('script', string=re.compile(r"window\.__remixContext"))
        if not script_tag or not isinstance(script_tag.string, NavigableString): return None
        
        match = re.search(r'window\.__remixContext\s*=\s*({.*?});', script_tag.string)
        if not match: return None

        try:
            remix_context = json.loads(match.group(1))
            job_post_data = next(
                (v['jobPost'] for k, v in remix_context.get('state', {}).get('loaderData', {}).items() if 'jobPost' in v),
                None
            )
            if not job_post_data: return None

            desc_html = job_post_data.get("content", "")
            desc_soup = BeautifulSoup(desc_html, 'html.parser')

            return Job(
                title=job_post_data.get("title"),
                company=job_post_data.get("company_name"),
                description=desc_soup.get_text(separator='\n', strip=True),
                source_url=url,
                ats_platform=ats_name,
                location_raw=job_post_data.get("job_post_location"),
                employment_type=job_post_data.get("employment"),
                date_posted_raw=job_post_data.get("published_at")
            )
        except (json.JSONDecodeError, ValidationError, StopIteration) as e:
            logging.warning(f"RemixContext parsing failed for {url}: {e}")
            return None

    async def _scrape_from_selectors(self, soup: BeautifulSoup, url: str, ats_name: str, config: Dict) -> Optional[Job]:
        if 'selector' not in config:
            logging.warning(f"Selector strategy for {ats_name} skipped: 'selector' key missing.")
            return None

        title = self._extract_text(soup, config.get('title_selector'))
        description = self._extract_text(soup, config.get('selector'))
        if not title or not description:
            logging.warning(f"Could not extract title or description using selectors for {url}")
            return None

        return Job(
            title=title,
            company=self._extract_text(soup, config.get('company_selector')),
            description=description,
            source_url=url,
            ats_platform=ats_name,
            location_raw=self._extract_text(soup, config.get('location_selector')),
            date_posted_raw=self._extract_text(soup, config.get('date_selector'))
        )

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
    async def _scrape_job_url(self, session: aiohttp.ClientSession, url: str) -> Optional[Job]:
        try:
            async with session.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                if response.status >= 300:
                    logging.warning(f"Failed to fetch {url}. Status: {response.status}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                match = self._find_config_for_url(str(response.url))
                if not match:
                    logging.debug(f"No matching ATS configuration found for URL: {url}")
                    return None
                
                ats_name, config = match
                strategy = config.get("parsing_strategy", "selectors")
                logging.debug(f"Using strategy '{strategy}' for {url}")

                job = None
                if strategy == "ld+json":
                    job = await self._scrape_from_ld_json(soup, url, ats_name)
                elif strategy == "remix_context":
                    job = await self._scrape_from_remix_context(soup, url, ats_name)
                
                # If the primary strategy failed, or if the strategy was 'selectors' from the start
                if not job:
                     logging.debug(f"Primary strategy '{strategy}' failed or was not set for {url}. Trying fallback to selectors.")
                     job = await self._scrape_from_selectors(soup, url, ats_name, config)
                
                return job

        except Exception:
            logging.error(f"An unexpected error occurred while scraping {url}", exc_info=True)
            return None

    async def run(self):
        all_links: Set[str] = set()
        async with aiohttp.ClientSession() as session:
            logging.info("--- Starting Discovery Phase ---")
            discovery_tasks = [self._get_serp_results(session, self._build_search_query(kw)) for kw in self.job_title_keywords]
            link_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            
            for result in link_results:
                if isinstance(result, list): all_links.update(result)
                elif isinstance(result, Exception): logging.error(f"A discovery task failed", exc_info=result)

            if not all_links:
                logging.info("No job links found. Exiting.")
                return
            logging.info(f"Total unique job links to scrape: {len(all_links)}")

            logging.info("--- Starting Extraction Phase ---")
            scraping_tasks = [self._scrape_job_url(session, url) for url in all_links]
            job_results = await asyncio.gather(*scraping_tasks)
            
            successful_jobs = [job for job in job_results if job]
            logging.info(f"Successfully scraped {len(successful_jobs)} jobs.")
            
        if successful_jobs:
            logging.info("--- Starting Database Sync Phase ---")
            db_manager = None
            try:
                db_manager = DatabaseManager()
                db_manager.connect()
                db_manager.sync_jobs(successful_jobs)
            except Exception as e:
                logging.error(f"An error occurred during the database phase", exc_info=e)
            finally:
                if db_manager:
                    db_manager.close()
        else:
            logging.info("No new jobs to save to the database.")

async def main():
    scraper = JobScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
