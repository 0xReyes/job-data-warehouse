import requests
import re
import json
import time
import os
from urllib.parse import quote_plus, urlparse, unquote
import csv
from datetime import datetime
import random
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedGoogleJobScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Load user agents from file or use defaults
        self.user_agents = self.load_user_agents()
        
        # Enhanced regex patterns for better extraction from deep pages
        self.regex_patterns = {
            'job_title': [
                r'<h3[^>]*>([^<]*(?:engineer|developer|software|programmer|architect|analyst|sre|devops|backend|frontend|fullstack|full.stack)[^<]*)</h3>',
                r'data-ved="[^"]*">([^<]*(?:engineer|developer|software|programmer|architect|sre|devops)[^<]*)</a>',
                r'<a[^>]*href="[^"]*job[^"]*"[^>]*>([^<]*(?:engineer|developer|software|programmer)[^<]*)</a>',
                r'aria-label="([^"]*(?:engineer|developer|software|programmer|architect)[^"]*)"',
                r'<span[^>]*>([^<]*(?:senior|junior|lead|principal|staff)?\s*(?:software|backend|frontend|full.?stack|devops|site reliability)?\s*(?:engineer|developer|programmer)[^<]*)</span>',
                r'<div[^>]*class="[^"]*BNeawe[^"]*"[^>]*>([^<]*(?:engineer|developer|software)[^<]*)</div>',
                r'<div[^>]*jsname="[^"]*"[^>]*>([^<]*(?:engineer|developer|software)[^<]*)</div>'
            ],
            'company_name': [
                r'<span[^>]*class="[^"]*VuuXrf[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*BNeawe[^"]*UPmit[^"]*"[^>]*>([^<]+)</div>',
                r'<cite[^>]*class="[^"]*"[^>]*>([^<]+)</cite>',
                r'<span[^>]*>([A-Z][a-zA-Z\s&.-]{2,40})\s*[-|·]\s*',
                r'<div[^>]*class="[^"]*company[^"]*"[^>]*>([^<]+)</div>',
                r'at\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s*[-|]|\s*<)',
                r'<cite[^>]*>([^/]+?)\.(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)',
                r'https?://([^./]+)\.[^/]+/(?:jobs?|careers?)',
                r'<span[^>]*class="[^"]*source[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*data-ved[^>]*>([A-Z][a-zA-Z\s&.-]{2,50})</div>',
                r'›\s*([A-Z][a-zA-Z\s&.-]{2,40})\s*›'
            ],
            'location': [
                r'<div[^>]*class="[^"]*BNeawe[^"]*"[^>]*>([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})</div>',
                r'<span[^>]*class="[^"]*"[^>]*>([A-Z][a-z]+,\s*[A-Z]{2})</span>',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*(?:CA|NY|TX|FL|WA|IL|PA|OH|GA|NC|MI|NJ|VA|AZ|MA|TN|IN|MD|MO|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|UT|NV|AR|MS|KS|NM|NE|ID|WV|HI|ME|MT|RI|DE|SD|ND|AK|VT|WY|DC))\b',
                r'(Remote|Work from home|Telecommute|Distributed|Anywhere|100% Remote|Fully Remote)',
                r'<span[^>]*>[^<]*([A-Z][a-z]+,\s*[A-Z]{2})[^<]*</span>',
                r'·\s*([A-Z][a-z]+,\s*[A-Z]{2})\s*·',
                r'<div[^>]*>([^<]*(?:Remote|Hybrid|On-site)[^<]*)</div>'
            ],
            'remote_type': [
                r'\b(remote|work\s+from\s+home|telecommute|distributed|anywhere|100%\s*remote|fully\s*remote|remote.first)\b',
                r'\b(hybrid|flexible|remote[-\s]friendly|partly\s+remote)\b',
                r'\b(on[-\s]?site|in[-\s]?office|in[-\s]?person|office.based)\b'
            ],
            'salary': [
                r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:to|[-–—])\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3})k?\s*(?:to|[-–—])\s*(\d{1,3})k',
                r'salary:?\s*\$?(\d{1,3}(?:,\d{3})*)',
                r'\$(\d{1,3}(?:,\d{3})*)\+?',
                r'(\d{2,3})k\+?',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:USD|dollars?)',
                r'compensation:?\s*\$?(\d{1,3}(?:,\d{3})*)',
                r'pay:?\s*\$?(\d{1,3}(?:,\d{3})*)',
                r'range:?\s*\$?(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*\$?(\d{1,3}(?:,\d{3})*)'
            ],
            'job_urls': [
                r'href="(https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable|bamboohr|smartrecruiters)[^"]*(?:job|career|position)[^"]*)"',
                r'href="(https?://[^"]*(?:job|career|position|apply)[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"]*)"',
                r'<a[^>]*href="([^"]*(?:job|career|position|apply)[^"]*)"[^>]*>',
                r'data-href="([^"]*(?:job|career)[^"]*)"',
                r'href="(/url\?q=https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"]*)"',
                r'ping="/url\?[^"]*&amp;url=([^"&]*(?:job|career)[^"&]*)"',
                r'href="(https?://[^"]*\.(?:myworkdayjobs|greenhouse|lever|workable)\.(?:com|io)/[^"]*)"',
                r'data-ved="[^"]*"[^>]*href="([^"]*(?:job|career|apply)[^"]*)"'
            ],
            'description_snippets': [
                r'<span[^>]*class="[^"]*st[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*snippet[^"]*"[^>]*>([^<]+)</div>',
                r'<span[^>]*class="[^"]*BNeawe[^"]*s3v9rd[^"]*"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="[^"]*BNeawe[^"]*"[^>]*>([^<]{50,300})</div>',
                r'<span[^>]*>([^<]*(?:requirements?|qualifications?|experience|skills?|responsibilities?|years?)[^<]{20,200})</span>',
                r'<div[^>]*data-content-feature="[^"]*"[^>]*>([^<]+)</div>',
                r'<span[^>]*style="[^"]*"[^>]*>([^<]{50,200})</span>'
            ],
            'date_posted': [
                r'(\d{1,2}\s+(?:days?|weeks?|months?)\s+ago)',
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'Posted\s*:?\s*([^<\n]+)',
                r'(\d{1,2}\s+(?:hour|hr)s?\s+ago)',
                r'<span[^>]*>(\d+\s+(?:days?|weeks?|months?)\s+ago)</span>'
            ]
        }
        
        # Enhanced domain patterns for job boards
        self.job_board_patterns = {
            'workday': r'([^.]+)\.myworkdayjobs\.com',
            'greenhouse': r'job-boards\.greenhouse\.io/([^/]+)',
            'ashby': r'jobs\.ashbyhq\.com/([^/]+)',
            'lever': r'jobs\.lever\.co/([^/]+)',
            'workable': r'([^.]+)\.workable\.com',
            'bamboohr': r'([^.]+)\.bamboohr\.com',
            'smartrecruiters': r'jobs\.smartrecruiters\.com/([^/]+)',
            'icims': r'([^.]+)\.icims\.com',
            'breezy': r'([^.]+)\.breezy\.hr'
        }

    def load_user_agents(self) -> List[str]:
        """Load user agents from file or return default list."""
        try:
            if os.path.exists('user_agent.json'):
                with open('user_agent.json', 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load user_agent.json: {e}, using default user agents")
        
        # Default user agents if file doesn't exist
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]

    def get_random_headers(self):
        """Generate random headers to avoid detection."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def search_google_pages(self, query: str, start_page: int = 1, end_page: int = 30) -> str:
        """Search Google with pagination support."""
        encoded_query = quote_plus(query)
        all_html = ""
        
        for page in range(start_page, end_page + 1):
            start = (page - 1) * 10
            
            # Build URL with additional parameters for better results
            url = f"https://www.google.com/search?q={encoded_query}&start={start}&num=10&tbs=qdr:d"
            
            logger.info(f"Searching page {page}/{end_page}: Start index {start}")
            
            try:
                headers = self.get_random_headers()
                response = self.session.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Check for blocking
                if any(term in response.text.lower() for term in ["unusual traffic", "captcha", "blocked", "robot"]):
                    logger.warning(f"Potential blocking detected on page {page}")
                    time.sleep(random.uniform(60, 120))
                    continue
                
                # Check if we've reached the end of results
                if "did not match any documents" in response.text or len(response.text) < 5000:
                    logger.info(f"Reached end of results at page {page}")
                    break
                
                all_html += f"\n\n<!-- PAGE {page} START -->\n\n"
                all_html += response.text
                all_html += f"\n\n<!-- PAGE {page} END -->\n\n"
                
                logger.info(f"Successfully fetched page {page} - {len(response.text):,} characters")
                
                # Longer delays for deep pagination
                if page > 10:
                    time.sleep(random.uniform(8, 15))
                elif page > 5:
                    time.sleep(random.uniform(5, 10))
                else:
                    time.sleep(random.uniform(3, 6))
                
            except requests.RequestException as e:
                logger.error(f"Error fetching page {page}: {e}")
                time.sleep(random.uniform(15, 30))
                continue
        
        return all_html

    def extract_with_regex(self, html: str, pattern_key: str) -> List[str]:
        """Extract data using regex patterns with enhanced cleaning."""
        matches = []
        patterns = self.regex_patterns.get(pattern_key, [])
        
        for pattern in patterns:
            try:
                found = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                if found:
                    for match in found:
                        if isinstance(match, tuple):
                            matches.extend([m for m in match if m and m.strip()])
                        else:
                            if match and match.strip():
                                matches.append(match)
            except re.error as e:
                logger.warning(f"Regex error for pattern {pattern}: {e}")
                continue
        
        # Enhanced cleaning and deduplication
        cleaned_matches = []
        seen = set()
        
        for match in matches:
            cleaned = self.clean_text(match)
            if self.is_valid_match(cleaned, pattern_key) and cleaned.lower() not in seen:
                cleaned_matches.append(cleaned)
                seen.add(cleaned.lower())
        
        return cleaned_matches

    def is_valid_match(self, text: str, pattern_key: str) -> bool:
        """Validate extracted matches based on pattern type."""
        if not text or len(text) < 2:
            return False
        
        # Specific validation rules
        if pattern_key == 'job_title':
            return len(text) > 5 and len(text) < 100 and not text.lower().startswith('http')
        elif pattern_key == 'company_name':
            return len(text) > 2 and len(text) < 50 and not any(char in text for char in ['/', '\\', '@'])
        elif pattern_key == 'location':
            return len(text) > 2 and len(text) < 50
        elif pattern_key == 'salary':
            return any(char.isdigit() for char in text)
        elif pattern_key == 'job_urls':
            return text.startswith('http') or text.startswith('/url')
        
        return True

    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning."""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&#39;': "'", '&nbsp;': ' ', '&ndash;': '–', '&mdash;': '—'
        }
        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)
        
        # Remove numeric HTML entities
        text = re.sub(r'&#\d+;', '', text)
        
        # Clean Google URL redirects
        if text.startswith('/url?q='):
            text = unquote(re.sub(r'/url\?q=([^&]+)&.*', r'\1', text))
        
        # Clean whitespace and special characters
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('...', '').replace('›', '').replace('»', '').replace('‹', '')
        
        # Remove common Google search artifacts
        artifacts = ['Cached', 'Similar pages', 'Translate this page', 'More results from']
        for artifact in artifacts:
            if artifact in text:
                text = text.replace(artifact, '').strip()
        
        return text

    def extract_company_from_url(self, url: str) -> Optional[str]:
        """Extract company name from job board URL."""
        for board, pattern in self.job_board_patterns.items():
            match = re.search(pattern, url)
            if match:
                company = match.group(1)
                # Clean up company name
                company = company.replace('-', ' ').replace('_', ' ')
                company = re.sub(r'\b\w+\b', lambda m: m.group().capitalize(), company)
                return company
        return None

    def categorize_remote_type(self, text: str) -> str:
        """Enhanced remote work categorization."""
        text_lower = text.lower()
        
        # Strong remote indicators
        strong_remote = ['100% remote', 'fully remote', 'remote-first', 'distributed team', 'work from anywhere']
        if any(indicator in text_lower for indicator in strong_remote):
            return 'Remote'
        
        # General remote indicators
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed', 'anywhere']
        if any(keyword in text_lower for keyword in remote_keywords):
            return 'Remote'
        
        # Hybrid indicators
        hybrid_keywords = ['hybrid', 'flexible', 'remote-friendly', 'partly remote', 'flexible location']
        if any(keyword in text_lower for keyword in hybrid_keywords):
            return 'Hybrid'
        
        # Onsite indicators
        onsite_keywords = ['on-site', 'onsite', 'in-office', 'in-person', 'office-based', 'relocate']
        if any(keyword in text_lower for keyword in onsite_keywords):
            return 'Onsite'
        
        return 'Unknown'

    def parse_salary(self, salary_text: str) -> Dict[str, Optional[int]]:
        """Enhanced salary parsing."""
        if not salary_text:
            return {'min': None, 'max': None}
        
        # Remove currency symbols and clean
        cleaned = re.sub(r'[^\d.k\s\-–—]', '', salary_text.lower())
        
        # Range patterns
        range_patterns = [
            r'(\d+(?:\.\d+)?k?)\s*[-–—]\s*(\d+(?:\.\d+)?k?)',
            r'(\d+(?:\.\d+)?k?)\s+to\s+(\d+(?:\.\d+)?k?)',
            r'from\s+(\d+(?:\.\d+)?k?)\s+to\s+(\d+(?:\.\d+)?k?)'
        ]
        
        for pattern in range_patterns:
            range_match = re.search(pattern, cleaned)
            if range_match:
                min_sal = self.convert_salary_to_int(range_match.group(1))
                max_sal = self.convert_salary_to_int(range_match.group(2))
                if min_sal and max_sal and min_sal <= max_sal:
                    return {'min': min_sal, 'max': max_sal}
        
        # Single salary
        single_match = re.search(r'(\d+(?:\.\d+)?k?)', cleaned)
        if single_match:
            salary = self.convert_salary_to_int(single_match.group(1))
            if salary and 20000 <= salary <= 500000:  # Reasonable salary range
                return {'min': salary, 'max': salary}
        
        return {'min': None, 'max': None}

    def convert_salary_to_int(self, salary_str: str) -> Optional[int]:
        """Convert salary string to integer with validation."""
        if not salary_str:
            return None
        
        try:
            if 'k' in salary_str.lower():
                number = float(salary_str.lower().replace('k', ''))
                result = int(number * 1000)
            else:
                result = int(float(salary_str))
            
            # Validate reasonable salary range
            if 20000 <= result <= 500000:
                return result
            
        except ValueError:
            pass
        
        return None

    def analyze_jobs(self, html: str) -> List[Dict]:
        """Enhanced job analysis with better data matching."""
        logger.info("Extracting job data using enhanced regex patterns...")
        
        # Extract all data types
        job_urls = self.extract_with_regex(html, 'job_urls')
        titles = self.extract_with_regex(html, 'job_title')
        companies = self.extract_with_regex(html, 'company_name')
        locations = self.extract_with_regex(html, 'location')
        salaries = self.extract_with_regex(html, 'salary')
        descriptions = self.extract_with_regex(html, 'description_snippets')
        dates = self.extract_with_regex(html, 'date_posted')
        
        logger.info(f"Extracted: {len(job_urls)} URLs, {len(titles)} titles, {len(companies)} companies, {len(locations)} locations, {len(salaries)} salaries")
        
        jobs = []
        
        # Process jobs based on URLs (most reliable)
        for i, url in enumerate(job_urls):
            job = self.create_job_entry(
                url=url,
                title=titles[i] if i < len(titles) else '',
                company=companies[i] if i < len(companies) else '',
                location=locations[i] if i < len(locations) else '',
                salary=salaries[i] if i < len(salaries) else '',
                description=descriptions[i] if i < len(descriptions) else '',
                date=dates[i] if i < len(dates) else ''
            )
            jobs.append(job)
        
        # Process remaining titles without URLs
        url_count = len(job_urls)
        for i in range(url_count, len(titles)):
            job = self.create_job_entry(
                url='',
                title=titles[i],
                company=companies[i] if i < len(companies) else '',
                location=locations[i] if i < len(locations) else '',
                salary=salaries[i] if i < len(salaries) else '',
                description=descriptions[i] if i < len(descriptions) else '',
                date=dates[i] if i < len(dates) else ''
            )
            jobs.append(job)
        
        # Filter and deduplicate
        filtered_jobs = self.filter_and_deduplicate_jobs(jobs)
        
        logger.info(f"Created {len(filtered_jobs)} unique job entries")
        return filtered_jobs

    def create_job_entry(self, url: str, title: str, company: str, location: str, 
                        salary: str, description: str, date: str) -> Dict:
        """Create a standardized job entry."""
        job = {
            'url': url,
            'title': title,
            'company': company,
            'location': location,
            'salary_text': salary,
            'description': description,
            'date_posted': date,
            'scraped_date': datetime.now().isoformat()
        }
        
        # Extract company from URL if missing
        if not job['company'] and job['url']:
            extracted_company = self.extract_company_from_url(job['url'])
            if extracted_company:
                job['company'] = extracted_company
        
        # Categorize remote type
        location_text = f"{job['location']} {job['description']} {job['title']}"
        job['remote_type'] = self.categorize_remote_type(location_text)
        
        # Parse salary
        salary_info = self.parse_salary(job['salary_text'])
        job['salary_min'] = salary_info['min']
        job['salary_max'] = salary_info['max']
        
        # Get domain
        if job['url']:
            job['source_domain'] = urlparse(job['url']).netloc
        else:
            job['source_domain'] = 'google_search_result'
        
        return job

    def filter_and_deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter out invalid jobs and remove duplicates."""
        filtered = []
        seen_urls = set()
        seen_titles = set()
        
        for job in jobs:
            # Skip if no meaningful data
            if not (job['url'] or job['title']):
                continue
            
            # Skip duplicates by URL
            if job['url'] and job['url'] in seen_urls:
                continue
            
            # Skip duplicates by title + company
            title_company_key = f"{job['title'].lower()}:{job['company'].lower()}"
            if title_company_key in seen_titles:
                continue
            
            # Add to seen sets
            if job['url']:
                seen_urls.add(job['url'])
            seen_titles.add(title_company_key)
            
            filtered.append(job)
        
        return filtered

    def get_statistics(self, jobs: List[Dict]) -> Dict:
        """Generate comprehensive statistics."""
        if not jobs:
            return {'total_jobs': 0}
        
        # Basic counts
        total_jobs = len(jobs)
        jobs_with_urls = sum(1 for job in jobs if job.get('url'))
        jobs_with_salaries = sum(1 for job in jobs if job.get('salary_min'))
        
        # Remote type distribution
        remote_counts = {}
        for job in jobs:
            remote_type = job.get('remote_type', 'Unknown')
            remote_counts[remote_type] = remote_counts.get(remote_type, 0) + 1
        
        # Company counts
        company_counts = {}
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company and company != 'Unknown' and len(company) > 2:
                company_counts[company] = company_counts.get(company, 0) + 1
        
        # Source domain counts
        domain_counts = {}
        for job in jobs:
            domain = job.get('source_domain', 'Unknown')
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Salary statistics
        salaries = [job.get('salary_min') for job in jobs if job.get('salary_min')]
        salary_stats = {}
        if salaries:
            salary_stats = {
                'min': min(salaries),
                'max': max(salaries),
                'avg': sum(salaries) / len(salaries),
                'median': sorted(salaries)[len(salaries) // 2],
                'count': len(salaries)
            }
        
        return {
            'total_jobs': total_jobs,
            'jobs_with_urls': jobs_with_urls,
            'jobs_with_salaries': jobs_with_salaries,
            'remote_distribution': remote_counts,
            'top_companies': sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:15],
            'source_distribution': domain_counts,
            'salary_stats': salary_stats
        }

    def save_to_csv(self, jobs: List[Dict], filename: str = 'deep_google_jobs.csv'):
        """Save jobs to CSV with enhanced fields."""
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        fieldnames = [
            'url', 'title', 'company', 'location', 'remote_type',
            'salary_min', 'salary_max', 'salary_text', 'description',
            'date_posted', 'scraped_date', 'source_domain'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for job in jobs:
                # Only write fields that exist in fieldnames
                filtered_job = {k: v for k, v in job.items() if k in fieldnames}
                writer.writerow(filtered_job)
        
        logger.info(f"Saved {len(jobs)} jobs to {filename}")

    def run_deep_search(self, query: str = None, start_page: int = 1, end_page: int = 30):
        """Run deep search across multiple pages."""
        if query is None:
            query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
                      site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com OR
                      site:careers-page.com) AND 
                      (inurl:jobs OR inurl:job OR inurl:application OR inurl:"/j/" OR inurl:apply) AND 
                      "Remote" AND -onsite -hybrid"""
        
        logger.info(f"Starting deep Google search from page {start_page} to {end_page}")
        logger.info(f"Query: {query}")
        
        # Search Google across multiple pages
        html_content = self.search_google_pages(query, start_page, end_page)
        
        if not html_content:
            logger.error("No HTML content retrieved from Google")
            return None
        
        logger.info(f"Total HTML content: {len(html_content):,} characters")
        
        # Analyze with enhanced regex
        jobs = self.analyze_jobs(html_content)
        
        # Generate statistics
        stats = self.get_statistics(jobs)
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f'deep_jobs_pages_{start_page}-{end_page}_{timestamp}.csv'
        self.save_to_csv(jobs, csv_filename)
        
        # Save raw HTML for debugging
        html_filename = f'google_search_pages_{start_page}-{end_page}_{timestamp}.html'
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save detailed analysis
        analysis_filename = f'analysis_pages_{start_page}-{end_page}_{timestamp}.json'
        with open(analysis_filename, 'w') as f:
            json.dump({
                'search_params': {
                    'query': query,
                    'start_page': start_page,
                    'end_page': end_page,
                    'timestamp': timestamp
                },
                'statistics': stats,
                'sample_jobs': jobs[:5]  # First 5 jobs as sample
            }, f, indent=2)
        
        return {
            'jobs': jobs,
            'statistics': stats,
            'html_length': len(html_content),
            'files_created': {
                'csv': csv_filename,
                'html': html_filename,
                'analysis': analysis_filename
            }
        }

    def search_specific_page_range(self, query: str, start_page: int, end_page: int):
        """Search a specific range of pages (like page 25-30)."""
        logger.info(f"Searching specific page range: {start_page} to {end_page}")
        return self.run_deep_search(query, start_page, end_page)


def main():
    scraper = AdvancedGoogleJobScraper()
    
    # Query from your URL (updated for better remote job filtering)
    query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
               site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com OR
               site:careers-page.com) AND 
               (inurl:jobs OR inurl:job OR inurl:application OR inurl:"/j/" OR inurl:apply) AND 
               "Remote" AND -onsite -hybrid"""
    
    # Example: Search pages 25-30 like your URL
    results = scraper.search_specific_page_range(query, start_page=25, end_page=30)
    
    if results:
        stats = results['statistics']
        files = results['files_created']
        
        print("\n" + "="*70)
        print("DEEP GOOGLE JOB SEARCH RESULTS - PAGES 25-30")
        print("="*70)
        
        print(f"\nSearch Summary:")
        print(f"  Total Jobs Found: {stats.get('total_jobs', 0)}")
        print(f"  Jobs with URLs: {stats.get('jobs_with_urls', 0)}")
        print(f"  Jobs with Salary Info: {stats.get('jobs_with_salaries', 0)}")
        print(f"  HTML Content: {results['html_length']:,} characters")
        
        if stats.get('remote_distribution'):
            print(f"\nRemote Work Distribution:")
            for remote_type, count in stats['remote_distribution'].items():
                percentage = (count / stats['total_jobs']) * 100
                print(f"  {remote_type}: {count} ({percentage:.1f}%)")
        
        if stats.get('top_companies'):
            print(f"\nTop Companies (Top 10):")
            for company, count in stats['top_companies'][:10]:
                print(f"  {company}: {count} jobs")
        
        if stats.get('source_distribution'):
            print(f"\nJob Board Sources:")
            for domain, count in sorted(stats['source_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {domain}: {count}")
        
        if stats.get('salary_stats') and stats['salary_stats']:
            salary = stats['salary_stats']
            print(f"\nSalary Statistics ({salary['count']} jobs with salary data):")
            print(f"  Average: ${salary['avg']:,.0f}")
            print(f"  Median: ${salary['median']:,.0f}")
            print(f"  Range: ${salary['min']:,} - ${salary['max']:,}")
        
        print(f"\nFiles Created:")
        print(f"  📊 CSV Data: {files['csv']}")
        print(f"  🌐 Raw HTML: {files['html']}")
        print(f"  📈 Analysis: {files['analysis']}")
        
        print(f"\n💡 Pro Tips:")
        print(f"  - Check the CSV file for detailed job data")
        print(f"  - Review the HTML file if you need to debug regex patterns")
        print(f"  - The analysis JSON contains search parameters and statistics")
        
        # Show sample jobs
        if results['jobs']:
            print(f"\nSample Jobs Found:")
            for i, job in enumerate(results['jobs'][:3], 1):
                print(f"\n  {i}. {job.get('title', 'No title')}")
                print(f"     Company: {job.get('company', 'Unknown')}")
                print(f"     Location: {job.get('location', 'Unknown')}")
                print(f"     Remote: {job.get('remote_type', 'Unknown')}")
                if job.get('salary_min'):
                    salary_range = f"${job['salary_min']:,}"
                    if job.get('salary_max') and job['salary_max'] != job['salary_min']:
                        salary_range += f" - ${job['salary_max']:,}"
                    print(f"     Salary: {salary_range}")
                if job.get('url'):
                    print(f"     URL: {job['url'][:80]}...")
    
    else:
        print("❌ No results found or error occurred during scraping")
        print("\nTroubleshooting tips:")
        print("  - Check your internet connection")
        print("  - Google might be rate-limiting requests")
        print("  - Try reducing the page range")
        print("  - Consider adding delays between requests")


def search_current_page_example():
    """Example function to search around page 25 like your URL."""
    scraper = AdvancedGoogleJobScraper()
    
    # Your exact query from the URL
    query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
               site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com OR
               site:careers-page.com) AND 
               (inurl:jobs OR inurl:job OR inurl:application OR inurl:"/j/" OR inurl:apply) AND 
               "Remote" AND -onsite -hybrid"""
    
    print("🔍 Searching pages 23-27 (around your current page 25)...")
    
    results = scraper.search_specific_page_range(query, start_page=23, end_page=27)
    
    if results and results['jobs']:
        print(f"\n✅ Found {len(results['jobs'])} jobs in pages 23-27")
        print(f"📁 Data saved to: {results['files_created']['csv']}")
        
        # Quick preview
        remote_jobs = [job for job in results['jobs'] if job.get('remote_type') == 'Remote']
        print(f"🏠 Remote jobs found: {len(remote_jobs)}")
        
        return results
    else:
        print("❌ No jobs found in this page range")
        return None


if __name__ == "__main__":
    main()
