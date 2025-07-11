import requests
import re
import time
import csv
from datetime import datetime
import random
from urllib.parse import quote_plus
import json

class StealthJobScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Load user agents from file or use defaults
        self.user_agents = self.load_user_agents()
        self.accept_headers = [
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        ]
        
    def load_user_agents(self):
        """Load user agents from user_agent.json or return defaults"""
        try:
            with open('scripts/user_agent.json', 'r') as f:
                agents = json.load(f)
                print(f"✅ Loaded {len(agents)} user agents from file")
                return agents

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Could not load user_agent.json: {e}")
            print("📝 Using default user agents")
            
            # Create the file for future use
            default_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0"
            ]
            
            try:
                with open('user_agent.json', 'w') as f:
                    json.dump(default_agents, f, indent=2)
                print("📄 Created user_agent.json with default agents")
            except Exception as e:
                print(f"⚠️  Could not create user_agent.json: {e}")
            
            return default_agents
        

    def get_stealth_headers(self):
        """Ultra-realistic browser headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': random.choice(self.accept_headers),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def check_for_blocking(self, html):
        """Detect if Google is blocking us"""
        blocking_indicators = [
            'httpservice/retry/enablejs',
            'unusual traffic',
            'captcha',
            'blocked',
            'Please click here if you are not redirected',
            'having trouble accessing Google Search'
        ]
        
        for indicator in blocking_indicators:
            if indicator.lower() in html.lower():
                return True, indicator
        
        return False, None

    def wait_and_retry(self, attempt):
        """Progressive backoff when blocked"""
        wait_times = [30, 60, 120, 300, 600]  # 30s, 1m, 2m, 5m, 10m
        wait_time = wait_times[min(attempt, len(wait_times)-1)]
        
        print(f"⏰ Waiting {wait_time}s before retry (attempt {attempt + 1})...")
        time.sleep(wait_time)

    def try_alternative_search(self, query):
        """Try different search approaches when blocked"""
        alternatives = [
            # Different Google domains
            ("www.google.com", "q"),
            ("www.google.ca", "q"), 
            ("www.google.co.uk", "q"),
            ("www.google.com.au", "q"),
            
            # Try different search engines
            ("duckduckgo.com", "q"),
            ("www.bing.com", "q"),
        ]
        
        for domain, param in alternatives:
            try:
                print(f"🔄 Trying alternative: {domain}")
                
                if "duckduckgo" in domain:
                    # DuckDuckGo format
                    url = f"https://{domain}/?{param}={quote_plus(query)}"
                elif "bing" in domain:
                    # Bing format  
                    url = f"https://{domain}/search?{param}={quote_plus(query)}"
                else:
                    # Google format
                    url = f"https://{domain}/search?{param}={quote_plus(query)}"
                
                headers = self.get_stealth_headers()
                response = self.session.get(url, headers=headers, timeout=15)
                
                is_blocked, reason = self.check_for_blocking(response.text)
                
                if not is_blocked and len(response.text) > 10000:
                    print(f"✅ Success with {domain}")
                    return response.text
                else:
                    print(f"❌ {domain} also blocked or no results")
                    
            except Exception as e:
                print(f"❌ Error with {domain}: {e}")
                continue
        
        return None

    def fetch_with_stealth(self, query, max_pages=10):
        """Fetch pages with advanced anti-blocking"""
        print("🥷 Starting STEALTH mode...")
        
        encoded_query = quote_plus(query)
        all_html = ""
        page = 0
        consecutive_blocks = 0
        
        while page < max_pages and consecutive_blocks < 3:
            start = page * 10
            url = f"https://www.google.com/search?q={encoded_query}&start={start}&num=10"
            
            print(f"📄 Stealth page {page + 1} (start={start})")
            
            try:
                headers = self.get_stealth_headers()
                response = self.session.get(url, headers=headers, timeout=20)
                html = response.text
                
                # Check for blocking
                is_blocked, block_reason = self.check_for_blocking(html)
                
                if is_blocked:
                    print(f"🚨 BLOCKED: {block_reason}")
                    consecutive_blocks += 1
                    
                    if consecutive_blocks >= 2:
                        print("🔄 Trying alternative search engines...")
                        alt_html = self.try_alternative_search(query)
                        if alt_html:
                            all_html += f"\n<!-- ALT PAGE {page + 1} -->\n{alt_html}"
                            consecutive_blocks = 0
                        else:
                            print("❌ All alternatives blocked")
                            break
                    else:
                        self.wait_and_retry(consecutive_blocks - 1)
                        continue
                
                else:
                    # Success!
                    consecutive_blocks = 0
                    
                    # Check for end of results
                    if ("did not match any documents" in html or 
                        "No results found" in html or
                        len(html) < 5000):
                        print(f"✅ End of results at page {page + 1}")
                        break
                    
                    all_html += f"\n<!-- PAGE {page + 1} -->\n{html}"
                    print(f"   ✅ Success: {len(html):,} chars")
                    
                    page += 1
                    
                    # Human-like delays
                    delay = random.uniform(5, 12)
                    print(f"   ⏱️  Human delay: {delay:.1f}s")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"❌ Network error: {e}")
                consecutive_blocks += 1
                time.sleep(random.uniform(10, 20))
        
        print(f"🎯 Stealth complete: {page} pages, {len(all_html):,} chars")
        return all_html

    def extract_jobs_safely(self, html):
        """Extract jobs with better error handling"""
        print("🔍 Safe extraction...")
        
        if not html or len(html) < 1000:
            print("❌ No valid HTML to process")
            return []
        
        # Robust patterns that work across search engines
        patterns = {
            'urls': [
                r'href="(https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"]*)"',
                r'href="(/url\?q=https?://[^"]*(?:myworkdayjobs|greenhouse|ashbyhq|lever|workable)[^"&]*)',
            ],
            'titles': [
                r'<h3[^>]*>([^<]*(?:engineer|developer|software|architect)[^<]*)</h3>',
                r'<a[^>]*><h3[^>]*>([^<]*(?:engineer|developer|software)[^<]*)</h3></a>',
                r'data-ved="[^"]*">([^<]*(?:engineer|developer|software)[^<]*)</a>'
            ],
            'companies': [
                r'<cite[^>]*>([^<]+\.(?:com|io|co|org))[^<]*</cite>',
                r'<span[^>]*class="[^"]*source[^"]*"[^>]*>([^<]+)</span>'
            ]
        }
        
        extracted = {}
        for key, pattern_list in patterns.items():
            matches = []
            for pattern in pattern_list:
                try:
                    found = re.findall(pattern, html, re.IGNORECASE)
                    matches.extend(found)
                except Exception as e:
                    print(f"⚠️  Pattern error for {key}: {e}")
            
            # Clean and dedupe
            cleaned = []
            for match in matches:
                if match and isinstance(match, str):
                    clean_match = self.clean_text(match)
                    if clean_match and clean_match not in cleaned:
                        cleaned.append(clean_match)
            
            extracted[key] = cleaned
            print(f"   {key}: {len(extracted[key])}")
        
        # Build jobs
        jobs = []
        max_items = max(len(v) for v in extracted.values()) if extracted else 0
        
        for i in range(max_items):
            url = extracted['urls'][i] if i < len(extracted['urls']) else ''
            title = extracted['titles'][i] if i < len(extracted['titles']) else ''
            company_raw = extracted['companies'][i] if i < len(extracted['companies']) else ''
            
            # Clean URL if it's a Google redirect
            if url.startswith('/url?q='):
                url = re.sub(r'/url\?q=([^&]+).*', r'\1', url)
            
            job = {
                'url': url,
                'title': title,
                'company': self.extract_company_name(company_raw, url),
                'remote_type': self.detect_remote_type(title),
                'scraped_date': datetime.now().isoformat()
            }
            
            if job['url'] or job['title']:
                jobs.append(job)
        
        print(f"✅ Extracted {len(jobs)} jobs safely")
        return jobs

    def clean_text(self, text):
        """Enhanced text cleaning"""
        if not text:
            return ""
        
        # Remove HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode entities
        text = text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_company_name(self, company_text, url):
        """Smart company extraction"""
        if company_text:
            # Clean domain to company name
            company = re.sub(r'\.(com|io|co|org).*', '', company_text)
            company = company.replace('www.', '').replace('jobs.', '').replace('careers.', '')
            return company.title()
        
        if url:
            # Extract from job board URLs
            board_patterns = [
                (r'([^.]+)\.myworkdayjobs\.com', 'Workday'),
                (r'job-boards\.greenhouse\.io/([^/]+)', 'Greenhouse'),
                (r'jobs\.ashbyhq\.com/([^/]+)', 'Ashby'),
                (r'jobs\.lever\.co/([^/]+)', 'Lever')
            ]
            
            for pattern, board in board_patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1).replace('-', ' ').title()
        
        return 'Unknown'

    def detect_remote_type(self, title):
        """Simple remote detection"""
        if not title:
            return 'Unknown'
        
        title_lower = title.lower()
        if any(word in title_lower for word in ['remote', 'work from home', 'telecommute']):
            return 'Remote'
        elif 'hybrid' in title_lower:
            return 'Hybrid'
        return 'Unknown'

    def save_results(self, jobs):
        """Save with backup formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save CSV
        csv_file = f'stealth_jobs_{timestamp}.csv'
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if jobs:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
        
        # Save JSON backup
        json_file = f'stealth_jobs_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2)
        
        print(f"💾 Saved {len(jobs)} jobs to {csv_file} and {json_file}")
        return csv_file, json_file

    def run_stealth_mode(self):
        """Complete stealth operation"""
        query = """(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io OR 
                   site:jobs.ashbyhq.com OR site:jobs.lever.co OR site:*.workable.com) AND 
                   engineer AND remote AND -onsite"""
        
        print("🥷 STEALTH JOB SCRAPER - ANTI-BLOCK MODE")
        print("=" * 50)
        print("Features:")
        print("✓ Real browser fingerprinting")
        print("✓ Block detection & recovery")
        print("✓ Alternative search engines")
        print("✓ Progressive backoff")
        print("✓ Human-like delays")
        print("=" * 50)
        
        # Fetch with stealth
        html = self.fetch_with_stealth(query, max_pages=20)
        
        if not html:
            print("❌ No data retrieved - all sources blocked")
            return None
        
        # Extract jobs safely
        jobs = self.extract_jobs_safely(html)
        
        if not jobs:
            print("❌ No jobs extracted")
            return None
        
        # Save results
        csv_file, json_file = self.save_results(jobs)
        
        # Show summary
        print(f"\n📊 STEALTH SUMMARY:")
        print(f"   Total Jobs: {len(jobs)}")
        
        # Remote breakdown
        remote_counts = {}
        for job in jobs:
            remote_type = job['remote_type']
            remote_counts[remote_type] = remote_counts.get(remote_type, 0) + 1
        
        print(f"   Remote Distribution:")
        for remote_type, count in remote_counts.items():
            print(f"     {remote_type}: {count}")
        
        # Company breakdown
        companies = [j['company'] for j in jobs if j['company'] != 'Unknown']
        if companies:
            company_counts = {}
            for comp in companies:
                company_counts[comp] = company_counts.get(comp, 0) + 1
            
            print(f"   Top Companies:")
            for comp, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     {comp}: {count}")
        
        print(f"\n📁 Files: {csv_file}, {json_file}")
        return {'jobs': jobs, 'files': [csv_file, json_file]}


def main():
    scraper = StealthJobScraper()
    results = scraper.run_stealth_mode()
    
    if results:
        print("🎉 Stealth scraping completed!")
        print(f"📈 Total jobs found: {len(results['jobs'])}")
    else:
        print("❌ Stealth scraping failed - Google defenses too strong")
        print("\n💡 Try these:")
        print("   - Wait a few hours and try again")
        print("   - Use a different internet connection")
        print("   - Try running from a different location")


if __name__ == "__main__":
    main()