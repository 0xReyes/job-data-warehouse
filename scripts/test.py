import requests
import re
import json
import time
import csv
from datetime import datetime
import random
from urllib.parse import quote_plus, urlparse
import os
import string
import uuid

class JobScraperWithDebug:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = self.load_user_agents()

    def load_user_agents(self):
        """Load user agents from file or use defaults"""
        try:
            if os.path.exists('user_agent.json'):
                with open('user_agent.json', 'r') as f:
                    agents = json.load(f)
                    print(f"✅ Loaded {len(agents)} user agents from file")
                    return agents
        except Exception as e:
            print(f"⚠️ Could not load user_agent.json: {e}")
        
        # Default user agents
        default_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Create file for future use
        try:
            with open('user_agent.json', 'w') as f:
                json.dump(default_agents, f, indent=2)
            print("📄 Created user_agent.json with default agents")
        except:
            pass
        
        return default_agents

    def get_headers(self):
        """Generate ultra-randomized HTTP headers with varied configurations."""
        def random_ip(): return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        def random_string(length): return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        def random_domain(): return f"{random_string(3+random.randint(0,7))}.{random.choice(['com', 'org', 'net', 'io', 'co', 'xyz'])}"
        
        headers = {
            'User-Agent': random.choice(self.user_agents + [f"CustomBot/{random_string(5)}", f"Mozilla/5.0 (Compatible; {random_string(8)}/{random.randint(1,10)}.0)"]),
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'application/json,text/plain,*/*;q=0.7',
                'text/*;q=0.9,image/*;q=0.6,*/*;q=0.5',
                '*/*;q={:.1f}'.format(random.uniform(0.1, 1.0))
            ]),
            'Accept-Language': random.choice([
                f"{lang},{lang[:2]};q={random.uniform(0.3, 1.0):.2f}" 
                for lang in ['en-US', 'en-GB', 'fr-FR', 'de-DE', 'es-ES', 'it-IT', 'ja-JP', 'zh-CN', 'ru-RU', 'pt-BR']
            ] + ['*', f"{random_string(2)}-{random_string(2)},*;q=0.{random.randint(1,9)}"]),
            'Accept-Encoding': random.choice([
                'gzip, deflate, br', 'br, zstd', 'gzip', 'deflate', 'identity', 
                ','.join(random.sample(['gzip', 'deflate', 'br', 'zstd'], random.randint(1,4)))
            ]),
            'Connection': random.choice(['keep-alive', 'close', 'upgrade', None]),
            'Upgrade-Insecure-Requests': random.choice(['1', '0', None]),
            'DNT': random.choice(['1', '0', None]),
            'Sec-Fetch-Dest': random.choice(['document', 'navigate', 'iframe', 'object', 'script', 'style', None]),
            'Sec-Fetch-Mode': random.choice(['navigate', 'same-origin', 'no-cors', 'cors', 'websocket', None]),
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site', 'cross-site', None]),
            'Sec-Fetch-User': random.choice(['?1', '?0', None]),
            'Cache-Control': random.choice(['no-cache', 'max-age={}'.format(random.randint(0,3600)), 'no-store', 'must-revalidate', 'private', None]),
            'Referrer': random.choice([
                f'https://{random_domain()}/{random_string(random.randint(3,15))}',
                f'https://www.google.com/search?q={random_string(random.randint(4,12))}',
                f'https://www.{random.choice(["bing", "yahoo", "duckduckgo"])}.com/{random_string(5)}',
                f'http://{random_domain()}',
                None
            ]) if random.random() > 0.15 else None,
            'X-Forwarded-For': random_ip() if random.random() > 0.35 else None,
            'X-Requested-With': random.choice(['XMLHttpRequest', random_string(8), None]) if random.random() > 0.55 else None,
            'Pragma': random.choice(['no-cache', None]) if random.random() > 0.65 else None,
            'Cookie': f'{random_string(5)}={random_string(8+random.randint(0,12))}; id={str(uuid.uuid4())[:8]}' if random.random() > 0.45 else None,
            'If-Modified-Since': time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                time.gmtime(time.time() - random.randint(0, 86400*14))) if random.random() > 0.75 else None,
            'X-Custom-Header': random_string(random.randint(5,15)) if random.random() > 0.8 else None,
            'TE': random.choice(['trailers', 'compress', None]) if random.random() > 0.85 else None,
            'Via': f'1.1 {random_string(6+random.randint(0,4))}' if random.random() > 0.9 else None
        }
        return {k: v for k, v in headers.items() if v is not None}

    def debug_response(self, response, page_num):
        """Debug every response to see what's happening"""
        print(f"\n🔍 DEBUG RESPONSE - Page {page_num}")
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        print(f"Response Length: {len(response.text):,} characters")
        
        # Check for blocking indicators
        blocking_signs = [
            'unusual traffic',
            'captcha', 
            'blocked',
            'httpservice/retry/enablejs',
            'Please click here if you are not redirected',
            'noscript'
        ]
        
        found_blocks = []
        for sign in blocking_signs:
            if sign.lower() in response.text.lower():
                found_blocks.append(sign)
        
        if found_blocks:
            print(f"🚨 BLOCKING DETECTED: {found_blocks}")
            print(f"First 500 chars of response:")
            print(response.text[:500])
            print("...")
            return False
        else:
            print("✅ No blocking detected")
        
        # Show first few lines to verify content
        lines = response.text.split('\n')[:5]
        print(f"Response preview:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"  {i}: {line[:100]}...")
        
        print("-" * 60)
        return True

    def fetch_all_pages(self, query):
        """Fetch ALL pages until no more results"""
        print(f"🚀 Starting to fetch ALL pages for query...")
        
        encoded_query = quote_plus(query)
        all_html = ""
        page = 0
        consecutive_failures = 0
        
        while page < 50 and consecutive_failures < 3:  # Max 50 pages or 3 consecutive failures
            start = page * 10
            url = f"https://www.google.com/search?q={encoded_query}&start={start}&num=10"
            
            print(f"📄 Fetching page {page + 1} (start={start})...")
            
            try:
                headers = self.get_headers()
                response = self.session.get(url, headers=headers, timeout=15)
                print(response)
                print(response.text)
                
                # DEBUG EVERY RESPONSE
                is_success = self.debug_response(response, page + 1)
                
                html = response.text
                
                if not is_success:
                    print(f"❌ Page {page + 1} blocked - backing off")
                    consecutive_failures += 1
                    time.sleep(random.uniform(30, 60))
                    continue
                
                # Check if we've reached the end
                if ("did not match any documents" in html or 
                    "No results found" in html or
                    len(html) < 5000):
                    print(f"✅ Reached end of results at page {page + 1}")
                    break
                
                all_html += f"\n<!-- PAGE {page + 1} -->\n" + html
                print(f"   ✓ Successfully added page {page + 1}")
                
                consecutive_failures = 0  # Reset on success
                page += 1
                
                # Smart delay
                delay = random.uniform(3, 8) + (page * 0.5)  # Progressive delays
                print(f"⏱️  Waiting {delay:.1f}s before next request...")
                time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Error on page {page + 1}: {e}")
                consecutive_failures += 1
                time.sleep(random.uniform(10, 20))
        
        print(f"🎯 Total pages fetched: {page}")
        print(f"📊 Total HTML size: {len(all_html):,} characters")
        return all_html

    def extract_jobs(self, html):
        """Extract jobs using simple regex patterns"""
        print("🔍 Extracting job data...")
        
        # Simple but effective patterns
        patterns = {
            'urls': r'href="(https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"]*)"',
            'titles': r'<h3[^>]*>([^<]*(?:engineer|developer|software|architect|sre)[^<]*)</h3>',
            'companies': r'<cite[^>]*>([^<]+)</cite>'
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            cleaned = [self.clean_text(match) for match in matches if match]
            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for item in cleaned:
                if item not in seen:
                    seen.add(item)
                    unique_matches.append(item)
            extracted[key] = unique_matches
            print(f"   {key}: {len(extracted[key])}")
        
        # Create job objects
        jobs = []
        max_items = max(len(v) for v in extracted.values()) if extracted else 0
        
        for i in range(max_items):
            job = {
                'url': extracted['urls'][i] if i < len(extracted['urls']) else '',
                'title': extracted['titles'][i] if i < len(extracted['titles']) else '',
                'company': extracted['companies'][i] if i < len(extracted['companies']) else '',
                'remote_type': self.get_remote_type(extracted['titles'][i] if i < len(extracted['titles']) else ''),
                'scraped_date': datetime.now().isoformat()
            }
            
            # Extract company from URL if missing
            if not job['company'] and job['url']:
                job['company'] = self.extract_company_from_url(job['url'])
            
            # Clean company name
            if job['company']:
                job['company'] = self.clean_company_name(job['company'])
            
            if job['url'] or job['title']:  # Only keep jobs with some data
                jobs.append(job)
        
        print(f"✅ Created {len(jobs)} job entries")
        return jobs

    def clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML
        text = text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
        return text.strip()

    def clean_company_name(self, company):
        """Clean company names"""
        # Remove domain extensions
        company = re.sub(r'\.(com|io|co|org).*', '', company)
        company = company.replace('www.', '').replace('jobs.', '').replace('careers.', '')
        return company.title()

    def extract_company_from_url(self, url):
        """Extract company from job board URL"""
        patterns = {
            r'([^.]+)\.myworkdayjobs\.com': 'workday',
            r'job-boards\.greenhouse\.io/([^/]+)': 'greenhouse',
            r'jobs\.ashbyhq\.com/([^/]+)': 'ashby',
            r'jobs\.lever\.co/([^/]+)': 'lever',
            r'([^.]+)\.workable\.com': 'workable'
        }
        
        for pattern, board in patterns.items():
            match = re.search(pattern, url)
            if match:
                return match.group(1).replace('-', ' ').title()
        return ''

    def get_remote_type(self, text):
        """Simple remote type detection"""
        if not text:
            return 'Unknown'
        text_lower = text.lower()
        if any(word in text_lower for word in ['remote', 'telecommute', 'work from home']):
            return 'Remote'
        elif 'hybrid' in text_lower:
            return 'Hybrid'
        else:
            return 'Unknown'

    def save_jobs(self, jobs, filename='debug_jobs.csv'):
        """Save jobs to CSV"""
        if not jobs:
            print("❌ No jobs to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title', 'company', 'remote_type', 'scraped_date'])
            writer.writeheader()
            writer.writerows(jobs)
        
        print(f"💾 Saved {len(jobs)} jobs to {filename}")

    def get_statistics(self, jobs):
        """Generate statistics"""
        if not jobs:
            return {}
        
        # Remote type counts
        remote_counts = {}
        for job in jobs:
            remote_type = job['remote_type']
            remote_counts[remote_type] = remote_counts.get(remote_type, 0) + 1
        
        # Company counts
        company_counts = {}
        for job in jobs:
            if job['company']:
                company_counts[job['company']] = company_counts.get(job['company'], 0) + 1
        
        return {
            'total_jobs': len(jobs),
            'remote_distribution': remote_counts,
            'top_companies': sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def run(self, query=None):
        """Run the complete scraping process with full debugging"""
        if query is None:
            query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
                      site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com) AND 
                      engineer AND remote AND -onsite"""
        
        print("🎯 JOB SCRAPER WITH FULL DEBUG MODE")
        print("=" * 50)
        print(f"Query: {query}")
        print("=" * 50)
        
        # Fetch all pages with debugging
        html = self.fetch_all_pages(query)
        
        if not html:
            print("❌ No HTML content fetched")
            return
        
        # Extract jobs
        jobs = self.extract_jobs(html)
        
        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f'debug_jobs_{timestamp}.csv'
        html_file = f'debug_html_{timestamp}.html'
        
        self.save_jobs(jobs, csv_file)
        
        # Save HTML for manual inspection
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Saved raw HTML to {html_file}")
        
        # Generate and display statistics
        stats = self.get_statistics(jobs)
        
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Total Jobs: {stats.get('total_jobs', 0)}")
        
        if stats.get('remote_distribution'):
            print(f"   Remote Distribution:")
            for remote_type, count in stats['remote_distribution'].items():
                print(f"     {remote_type}: {count}")
        
        if stats.get('top_companies'):
            print(f"   Top Companies:")
            for company, count in stats['top_companies'][:5]:
                print(f"     {company}: {count}")
        
        print(f"\n📁 Files created:")
        print(f"   📊 {csv_file}")
        print(f"   🌐 {html_file}")
        
        # Show sample jobs
        if jobs:
            print(f"\n🔍 Sample Jobs Found:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"   {i}. {job['title']}")
                print(f"      Company: {job['company'] or 'Unknown'}")
                print(f"      Remote: {job['remote_type']}")
                if job['url']:
                    print(f"      URL: {job['url'][:70]}...")
                print()
        
        return {
            'jobs': jobs,
            'stats': stats,
            'files': {'csv': csv_file, 'html': html_file}
        }


def main():
    scraper = JobScraperWithDebug()
    
    # Simple query
    query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
               site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com) AND 
               engineer AND remote AND -onsite"""
    
    results = scraper.run(query)
    
    if results:
        print("🎉 Scraping completed!")
        print(f"📈 Found {len(results['jobs'])} total jobs")
    else:
        print("❌ Scraping failed")


if __name__ == "__main__":
    main()