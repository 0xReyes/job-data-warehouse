import requests
import re
import json
import time
import csv
from datetime import datetime
import random
from urllib.parse import quote_plus, urlparse

class SimpleJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }

    def fetch_all_pages(self, query):
        """Fetch ALL pages until no more results"""
        print(f"🚀 Starting to fetch ALL pages for query...")
        
        encoded_query = quote_plus(query)
        all_html = ""
        page = 0
        
        while True:
            start = page * 10
            url = f"https://www.google.com/search?q={encoded_query}&start={start}&num=10"
            
            print(f"📄 Fetching page {page + 1} (start={start})...")
            
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=15)
                html = response.text
                print(html)
                
                # Check if we've reached the end
                if ("did not match any documents" in html or 
                    "No results found" in html or
                    len(html) < 5000 or
                    start > 1000):  # Google typically stops around 100 pages
                    print(f"✅ Reached end of results at page {page + 1}")
                    break
                
                all_html += f"\n<!-- PAGE {page + 1} -->\n" + html
                print(f"   ✓ Got {len(html):,} characters")
                
                page += 1
                time.sleep(random.uniform(2, 4))  # Be nice to Google
                
            except Exception as e:
                print(f"❌ Error on page {page + 1}: {e}")
                break
        
        print(f"🎯 Total pages fetched: {page}")
        print(f"📊 Total HTML size: {len(all_html):,} characters")
        return all_html

    def extract_jobs(self, html):
        """Extract jobs using simple regex patterns"""
        print("🔍 Extracting job data...")
        
        # Simple but effective patterns
        urls = re.findall(r'href="(https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"]*)"', html)
        titles = re.findall(r'<h3[^>]*>([^<]*(?:engineer|developer|software)[^<]*)</h3>', html, re.I)
        companies = re.findall(r'<cite[^>]*>([^<]+)</cite>', html)
        
        # Clean extracted data
        urls = [self.clean_url(url) for url in urls]
        titles = [self.clean_text(title) for title in titles]
        companies = [self.clean_text(comp) for comp in companies]
        
        # Remove duplicates
        urls = list(dict.fromkeys(urls))  # Preserves order
        titles = list(dict.fromkeys(titles))
        companies = list(dict.fromkeys(companies))
        
        print(f"📋 Found: {len(urls)} URLs, {len(titles)} titles, {len(companies)} companies")
        
        jobs = []
        max_items = max(len(urls), len(titles))
        
        for i in range(max_items):
            job = {
                'url': urls[i] if i < len(urls) else '',
                'title': titles[i] if i < len(titles) else '',
                'company': companies[i] if i < len(companies) else '',
                'remote_type': self.get_remote_type(titles[i] if i < len(titles) else ''),
                'scraped_date': datetime.now().isoformat()
            }
            
            # Extract company from URL if missing
            if not job['company'] and job['url']:
                job['company'] = self.extract_company_from_url(job['url'])
            
            if job['url'] or job['title']:  # Only keep jobs with some data
                jobs.append(job)
        
        print(f"✅ Created {len(jobs)} job entries")
        return jobs

    def clean_text(self, text):
        """Clean text"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML
        text = text.replace('&amp;', '&').replace('&quot;', '"')
        return text.strip()

    def clean_url(self, url):
        """Clean Google redirect URLs"""
        if '/url?q=' in url:
            url = re.sub(r'/url\?q=([^&]+).*', r'\1', url)
        return url

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
        text_lower = text.lower()
        if any(word in text_lower for word in ['remote', 'telecommute', 'work from home']):
            return 'Remote'
        elif 'hybrid' in text_lower:
            return 'Hybrid'
        else:
            return 'Unknown'

    def save_jobs(self, jobs, filename='all_jobs.csv'):
        """Save jobs to CSV"""
        if not jobs:
            print("❌ No jobs to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'title', 'company', 'remote_type', 'scraped_date'])
            writer.writeheader()
            writer.writerows(jobs)
        
        print(f"💾 Saved {len(jobs)} jobs to {filename}")

    def run(self, query=None):
        """Run the complete scraping process"""
        if query is None:
            query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
                      site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com) AND 
                      (inurl:jobs OR inurl:job OR inurl:application) AND 
                      engineer AND remote AND -onsite"""
        
        print("🎯 SIMPLE JOB SCRAPER - FETCH ALL PAGES")
        print("=" * 50)
        
        # Fetch all pages
        html = self.fetch_all_pages(query)
        print(html)
        
        if not html:
            print("❌ No HTML content fetched")
            return
        
        # Extract jobs
        jobs = self.extract_jobs(html)
        print(jobs)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f'all_jobs_{timestamp}.csv'
        html_file = f'all_pages_{timestamp}.html'
        
        self.save_jobs(jobs, csv_file)
        
        # Save HTML for debugging
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Print summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total Jobs: {len(jobs)}")
        
        # Count by remote type
        remote_counts = {}
        for job in jobs:
            remote_type = job['remote_type']
            remote_counts[remote_type] = remote_counts.get(remote_type, 0) + 1
        
        print(f"   Remote Distribution:")
        for remote_type, count in remote_counts.items():
            print(f"     {remote_type}: {count}")
        
        # Count by company
        company_counts = {}
        for job in jobs:
            if job['company']:
                company_counts[job['company']] = company_counts.get(job['company'], 0) + 1
        
        if company_counts:
            print(f"   Top Companies:")
            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"     {company}: {count}")
        
        print(f"\n📁 Files created:")
        print(f"   📊 {csv_file}")
        print(f"   🌐 {html_file}")
        
        # Show sample jobs
        print(f"\n🔍 Sample Jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"   {i}. {job['title']}")
            print(f"      Company: {job['company'] or 'Unknown'}")
            print(f"      Remote: {job['remote_type']}")
            if job['url']:
                print(f"      URL: {job['url'][:60]}...")
            print()
        
        return {
            'jobs': jobs,
            'files': {'csv': csv_file, 'html': html_file}
        }


def main():
    scraper = SimpleJobScraper()
    
    # Your query - simplified
    query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
               site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com) AND 
               engineer AND remote AND -onsite"""
    
    results = scraper.run(query)
    
    if results:
        print("🎉 Scraping completed successfully!")
        print(f"📈 Found {len(results['jobs'])} total jobs across ALL pages")
    else:
        print("❌ Scraping failed")


if __name__ == "__main__":
    main()