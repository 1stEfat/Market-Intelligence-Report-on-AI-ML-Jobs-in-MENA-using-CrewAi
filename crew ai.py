# Real MENA AI/ML Job Scraper - Enhanced Version
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import time
import random
from typing import List, Dict, Optional
import json
from urllib.parse import urljoin
import warnings
import logging
from fake_useragent import UserAgent
import sys
import io

# Fix Windows console encoding issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

warnings.filterwarnings('ignore')

# Define the full path for results directory
RESULTS_DIR = r"C:\Users\PC\Desktop\crewAi\results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Setup logging without emojis for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(RESULTS_DIR, "scraper.log"), 
        encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealMenaJobScraper:
    def __init__(self):
        self.mena_countries = [
            "United Arab Emirates", "UAE", "Saudi Arabia", "Egypt", "Qatar", "Jordan",
            "Kuwait", "Bahrain", "Oman", "Lebanon", "Morocco", "Algeria", "Tunisia"
        ]
        
        # Enhanced headers with fake user agent
        self.ua = UserAgent()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Configure job sources (LinkedIn removed)
        self.job_sources = {
            "wuzzuf": {
                "base_url": "https://wuzzuf.net",
                "search_urls": [
                    "https://wuzzuf.net/search/jobs/?q=artificial+intelligence",
                    "https://wuzzuf.net/search/jobs/?q=machine+learning",
                    "https://wuzzuf.net/search/jobs/?q=data+scientist"
                ],
                "selectors": {
                    "card": "div.css-1gatmva",
                    "title": "h2.css-m604qf",
                    "company": "div.css-d7j1kk",
                    "location": "span.css-5wys0k",
                    "link": "a.css-o171kl"
                }
            },
            "naukrigulf": {
                "base_url": "https://www.naukrigulf.com",
                "search_urls": [
                    "https://www.naukrigulf.com/artificial-intelligence-jobs",
                    "https://www.naukrigulf.com/machine-learning-jobs"
                ],
                "selectors": {
                    "card": "div.row",
                    "title": "a.title",
                    "company": "div.orgName",
                    "location": "span.loc",
                    "link": "a.title"
                }
            },
            "gulftalent": {
                "base_url": "https://www.gulftalent.com",
                "search_urls": [
                    "https://www.gulftalent.com/jobs/artificial-intelligence",
                    "https://www.gulftalent.com/jobs/machine-learning"
                ],
                "selectors": {
                    "card": "div.job-item",
                    "title": "a.job-title",
                    "company": "div.company",
                    "location": "div.location",
                    "link": "a.job-title"
                }
            }
        }
        
        self.session = requests.Session()
        self.all_jobs = []
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape jobs from all configured sources"""
        logger.info("Starting comprehensive job search...")
        
        # Scrape all platforms
        for source in self.job_sources.keys():
            self._scrape_platform(source)
        
        logger.info(f"Total jobs collected: {len(self.all_jobs)}")
        return self.all_jobs

    def _scrape_platform(self, source_name: str):
        """Scrape a specific platform"""
        config = self.job_sources[source_name]
        logger.info(f"\nScraping {source_name.upper()}")
        
        try:
            jobs = []
            for url in config["search_urls"]:
                try:
                    # Rotate user agents and add random delays
                    headers = {
                        **self.headers,
                        "User-Agent": self.ua.random
                    }
                    
                    logger.info(f"  Fetching: {url}")
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 403:
                        logger.warning(f"Access denied to {source_name}")
                        continue
                        
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        cards = soup.select(config["selectors"]["card"])
                        
                        for card in cards[:25]:  # Limit results
                            job = self._extract_job_data(card, source_name)
                            if job and self._is_ai_ml_job(job["Title"]):
                                jobs.append(job)
                                
                        logger.info(f"  Found {len(jobs)} jobs on {url}")
                        
                    # Random delay between requests
                    delay = random.uniform(2, 5)
                    logger.debug(f"  Sleeping for {delay:.2f} seconds...")
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}", exc_info=True)
            
            if jobs:
                self.all_jobs.extend(jobs)
                logger.info(f"Added {len(jobs)} jobs from {source_name}")
            else:
                logger.warning(f"No jobs found from {source_name}")
                
        except Exception as e:
            logger.error(f"Failed to scrape {source_name}: {str(e)}", exc_info=True)

    def _extract_job_data(self, card, source_name: str) -> Optional[Dict]:
        """Extract job data using platform-specific selectors"""
        config = self.job_sources[source_name]["selectors"]
        try:
            title_elem = card.select_one(config["title"])
            title = title_elem.text.strip() if title_elem else None
            if not title:
                return None
                
            company = card.select_one(config["company"]).text.strip() if card.select_one(config["company"]) else "Unknown"
            location = card.select_one(config["location"]).text.strip() if card.select_one(config["location"]) else "Middle East"
            link = card.select_one(config["link"]).get("href", "") if card.select_one(config["link"]) else ""
            
            return {
                "Title": title,
                "Company": company,
                "Location": location,
                "Link": urljoin(self.job_sources[source_name]["base_url"], link),
                "Country": self._extract_country(location),
                "Source": source_name.title()
            }
        except Exception as e:
            logger.debug(f"Error extracting job: {str(e)}")
            return None

    def _extract_country(self, location: str) -> str:
        """Extract country from location string"""
        location_lower = location.lower()
        country_mapping = {
            "uae": "United Arab Emirates",
            "dubai": "United Arab Emirates",
            "saudi": "Saudi Arabia",
            "riyadh": "Saudi Arabia",
            "cairo": "Egypt",
            "qatar": "Qatar",
            "kuwait": "Kuwait",
            "bahrain": "Bahrain",
            "oman": "Oman"
        }
        for key, country in country_mapping.items():
            if key in location_lower:
                return country
        return "Middle East"

    def _is_ai_ml_job(self, title: str) -> bool:
        """Determine if job is AI/ML related"""
        keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 
            'data scientist', 'deep learning', 'neural network',
            'nlp', 'computer vision', 'data engineer'
        ]
        return any(kw in title.lower() for kw in keywords)

    def analyze_jobs(self, jobs: List[Dict]) -> tuple:
        """Analyze collected job data"""
        if not jobs:
            logger.warning("No jobs found to analyze")
            return pd.Series(), pd.Series(), pd.Series(), pd.DataFrame()
        
        df = pd.DataFrame(jobs)
        logger.info("Analyzing job data...")
        
        # Clean and categorize
        df['Title_Clean'] = df['Title'].str.lower().str.strip()
        
        def categorize_job(title):
            title = title.lower()
            if 'data scientist' in title or 'data science' in title:
                return 'Data Scientist'
            elif 'machine learning' in title or 'ml engineer' in title:
                return 'ML Engineer'
            elif 'ai engineer' in title or 'artificial intelligence' in title:
                return 'AI Engineer'
            elif 'computer vision' in title:
                return 'Computer Vision Engineer'
            elif 'nlp' in title or 'natural language' in title:
                return 'NLP Engineer'
            elif 'data engineer' in title:
                return 'Data Engineer'
            elif 'research' in title and ('scientist' in title or 'researcher' in title):
                return 'Research Scientist'
            elif 'manager' in title or 'lead' in title:
                return 'AI/ML Manager'
            elif 'analyst' in title:
                return 'Data Analyst'
            else:
                return 'Other AI/ML Role'
        
        df['Job_Category'] = df['Title'].apply(categorize_job)
        
        # Analysis
        top_roles = df['Job_Category'].value_counts().head(10)
        location_dist = df['Country'].value_counts().head(10)
        source_dist = df['Source'].value_counts()
        
        logger.info(f"Analyzed {len(df)} jobs across {df['Job_Category'].nunique()} categories")
        logger.info(f"Jobs from {df['Country'].nunique()} countries")
        logger.info(f"Data from {df['Source'].nunique()} sources")
        
        return top_roles, location_dist, source_dist, df
    
    def create_comprehensive_report(self, top_roles: pd.Series, location_dist: pd.Series, 
                                  source_dist: pd.Series, df: pd.DataFrame):
        """Create comprehensive PDF and other reports"""
        logger.info("Creating comprehensive reports...")
        
        # Create PDF report
        self._create_pdf_report(top_roles, location_dist, source_dist, df)
        
        # Create other formats
        self._create_data_exports(df)
        self._create_markdown_report(top_roles, location_dist, source_dist, df)
        
        logger.info("All reports created successfully in 'results' folder!")
    
    def _create_pdf_report(self, top_roles, location_dist, source_dist, df):
        """Create comprehensive PDF report"""
        pdf_path = os.path.join(RESULTS_DIR, "mena_ai_ml_jobs_report.pdf")
        
        try:
            with PdfPages(pdf_path) as pdf:
                # Title page
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.text(0.5, 0.8, 'MENA AI/ML Jobs Market Analysis', 
                       fontsize=24, fontweight='bold', ha='center', transform=ax.transAxes)
                ax.text(0.5, 0.7, f'Real-time Job Market Research', 
                       fontsize=16, ha='center', transform=ax.transAxes)
                ax.text(0.5, 0.6, f'Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}', 
                       fontsize=12, ha='center', transform=ax.transAxes)
                ax.text(0.5, 0.5, f'Total Jobs Analyzed: {len(df)}', 
                       fontsize=14, fontweight='bold', ha='center', transform=ax.transAxes)
                ax.text(0.5, 0.4, f'Countries Covered: {df["Country"].nunique()}', 
                       fontsize=12, ha='center', transform=ax.transAxes)
                ax.text(0.5, 0.3, f'Data Sources: {df["Source"].nunique()}', 
                       fontsize=12, ha='center', transform=ax.transAxes)
                ax.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                
                if not top_roles.empty:
                    # Job categories chart
                    fig, ax = plt.subplots(figsize=(10, 8))
                    colors = plt.cm.Set3(range(len(top_roles)))
                    bars = ax.barh(range(len(top_roles)), top_roles.values, color=colors)
                    ax.set_yticks(range(len(top_roles)))
                    ax.set_yticklabels(top_roles.index)
                    ax.set_xlabel('Number of Jobs')
                    ax.set_title('AI/ML Job Categories Distribution', fontsize=16, fontweight='bold')
                    ax.invert_yaxis()
                    
                    # Add value labels
                    for i, (bar, value) in enumerate(zip(bars, top_roles.values)):
                        ax.text(value + 0.1, i, str(value), va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
                
                if not location_dist.empty:
                    # Geographic distribution
                    fig, ax = plt.subplots(figsize=(10, 8))
                    colors = plt.cm.Pastel1(range(len(location_dist)))
                    
                    # Create pie chart
                    wedges, texts, autotexts = ax.pie(location_dist.values, labels=location_dist.index, 
                                                     colors=colors, autopct='%1.1f%%', startangle=90)
                    ax.set_title('Job Distribution by Country/Region', fontsize=16, fontweight='bold')
                    
                    # Improve text readability
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
                
                if not source_dist.empty:
                    # Data sources chart
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = plt.cm.Set2(range(len(source_dist)))
                    bars = ax.bar(range(len(source_dist)), source_dist.values, color=colors)
                    ax.set_xticks(range(len(source_dist)))
                    ax.set_xticklabels(source_dist.index, rotation=45, ha='right')
                    ax.set_ylabel('Number of Jobs')
                    ax.set_title('Job Distribution by Source Platform', fontsize=16, fontweight='bold')
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, source_dist.values):
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                               str(value), ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()
                
                # Summary statistics page
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.text(0.5, 0.9, 'Market Insights & Statistics', 
                       fontsize=20, fontweight='bold', ha='center', transform=ax.transAxes)
                
                y_pos = 0.8
                insights = self._generate_market_insights(df, top_roles, location_dist)
                
                for insight in insights:
                    ax.text(0.1, y_pos, f"• {insight}", fontsize=12, ha='left', 
                           transform=ax.transAxes, wrap=True)
                    y_pos -= 0.08
                
                ax.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
            
            logger.info(f"PDF report saved to {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to create PDF report: {str(e)}")
            raise
    
    def _generate_market_insights(self, df: pd.DataFrame, top_roles: pd.Series, 
                                location_dist: pd.Series) -> List[str]:
        """Generate market insights from the data"""
        insights = []
        
        if not df.empty:
            # Role insights
            if not top_roles.empty:
                most_common_role = top_roles.index[0]
                role_percentage = (top_roles.iloc[0] / len(df)) * 100
                insights.append(f"'{most_common_role}' is the most in-demand AI/ML role, representing {role_percentage:.1f}% of all positions")
            
            # Location insights
            if not location_dist.empty:
                top_country = location_dist.index[0]
                country_percentage = (location_dist.iloc[0] / len(df)) * 100
                insights.append(f"{top_country} leads the MENA AI/ML job market with {country_percentage:.1f}% of all positions")
            
            # Diversity insights
            unique_companies = df['Company'].nunique()
            insights.append(f"Jobs are distributed across {unique_companies} different companies, showing market diversity")
            
            # Technical role analysis
            technical_roles = ['Data Scientist', 'ML Engineer', 'AI Engineer', 'Data Engineer']
            tech_count = sum(top_roles.get(role, 0) for role in technical_roles)
            tech_percentage = (tech_count / len(df)) * 100 if len(df) > 0 else 0
            insights.append(f"Technical roles (Data Scientists, ML/AI Engineers) represent {tech_percentage:.1f}% of the market")
            
            # Emerging trends
            cv_nlp_roles = df['Job_Category'].str.contains('Computer Vision|NLP', case=False, na=False).sum()
            if cv_nlp_roles > 0:
                cv_nlp_percentage = (cv_nlp_roles / len(df)) * 100
                insights.append(f"Specialized AI roles (Computer Vision, NLP) account for {cv_nlp_percentage:.1f}% of positions")
        
        # Add general market observations
        insights.extend([
            "The MENA region shows strong demand for AI/ML talent across multiple countries",
            "Job opportunities span from entry-level to senior positions across various industries",
            "Both local and international companies are actively hiring AI/ML professionals"
        ])
        
        return insights
    
    def _create_data_exports(self, df: pd.DataFrame):
        """Create various data export formats"""
        if df.empty:
            logger.warning("No data to export")
            return
        
        try:
            # CSV export
            csv_path = os.path.join(RESULTS_DIR, "mena_ai_ml_jobs_data.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"CSV data exported to {csv_path}")
            
            # Verify CSV was created
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV file not created at {csv_path}")
            
            # JSON export
            json_path = os.path.join(RESULTS_DIR, "mena_ai_ml_jobs_data.json")
            df.to_json(json_path, orient='records', indent=2)
            logger.info(f"JSON data exported to {json_path}")
            
            # Verify JSON was created
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"JSON file not created at {json_path}")
            
            # Excel export with multiple sheets
            excel_path = os.path.join(RESULTS_DIR, "mena_ai_ml_jobs_analysis.xlsx")
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Raw data
                df.to_excel(writer, sheet_name='Job_Listings', index=False)
                
                # Summary statistics
                summary_data = {
                    'Metric': ['Total Jobs', 'Unique Companies', 'Countries Covered', 'Job Categories', 'Data Sources'],
                    'Value': [len(df), df['Company'].nunique(), df['Country'].nunique(), 
                             df['Job_Category'].nunique(), df['Source'].nunique()]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Role distribution
                df['Job_Category'].value_counts().to_excel(writer, sheet_name='Role_Distribution')
                
                # Location distribution
                df['Country'].value_counts().to_excel(writer, sheet_name='Location_Distribution')
            
            logger.info(f"Excel analysis exported to {excel_path}")
            
            # Verify Excel was created
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"Excel file not created at {excel_path}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            raise
    
    def _create_markdown_report(self, top_roles: pd.Series, location_dist: pd.Series, 
                              source_dist: pd.Series, df: pd.DataFrame):
        """Create markdown summary report"""
        md_path = os.path.join(RESULTS_DIR, "mena_ai_ml_jobs_report.md")
        
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("# MENA AI/ML Jobs Market Analysis Report\n\n")
                f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if not df.empty:
                    f.write("## Executive Summary\n\n")
                    f.write(f"- **Total Jobs Analyzed:** {len(df)}\n")
                    f.write(f"- **Unique Companies:** {df['Company'].nunique()}\n")
                    f.write(f"- **Countries Covered:** {df['Country'].nunique()}\n")
                    f.write(f"- **Job Categories:** {df['Job_Category'].nunique()}\n")
                    f.write(f"- **Data Sources:** {df['Source'].nunique()}\n\n")
                    
                    if not top_roles.empty:
                        f.write("## Top AI/ML Job Categories\n\n")
                        for role, count in top_roles.head(10).items():
                            percentage = (count / len(df)) * 100
                            f.write(f"- **{role}:** {count} positions ({percentage:.1f}%)\n")
                        f.write("\n")
                    
                    if not location_dist.empty:
                        f.write("## Geographic Distribution\n\n")
                        for country, count in location_dist.head(10).items():
                            percentage = (count / len(df)) * 100
                            f.write(f"- **{country}:** {count} positions ({percentage:.1f}%)\n")
                        f.write("\n")
                    
                    if not source_dist.empty:
                        f.write("## Data Sources\n\n")
                        for source, count in source_dist.items():
                            percentage = (count / len(df)) * 100
                            f.write(f"- **{source}:** {count} positions ({percentage:.1f}%)\n")
                        f.write("\n")
                    
                    # Market insights
                    f.write("## Market Insights\n\n")
                    insights = self._generate_market_insights(df, top_roles, location_dist)
                    for insight in insights:
                        f.write(f"- {insight}\n")
                    f.write("\n")
                    
                    # Sample job listings
                    f.write("## Sample Job Listings\n\n")
                    sample_jobs = df.head(10)
                    for _, job in sample_jobs.iterrows():
                        f.write(f"### {job['Title']}\n")
                        f.write(f"- **Company:** {job['Company']}\n")
                        f.write(f"- **Location:** {job['Location']}\n")
                        f.write(f"- **Country:** {job['Country']}\n")
                        f.write(f"- **Source:** {job['Source']}\n")
                        if job['Link'] != 'N/A':
                            f.write(f"- **Link:** {job['Link']}\n")
                        f.write("\n")
                
                f.write("## Methodology\n\n")
                f.write("This analysis was conducted by scraping multiple job platforms including:\n")
                f.write("- Wuzzuf\n- NaukriGulf\n- GulfTalent\n\n")
                f.write("Data collection focused on AI/ML related positions across MENA countries.\n")
                f.write("Results were filtered and categorized to provide comprehensive market insights.\n")
            
            logger.info(f"Markdown report exported to {md_path}")
            
            # Verify markdown was created
            if not os.path.exists(md_path):
                raise FileNotFoundError(f"Markdown file not created at {md_path}")
            
        except Exception as e:
            logger.error(f"Failed to create markdown report: {str(e)}")
            raise
    
    def run_complete_analysis(self):
        """Run the complete job scraping and analysis pipeline"""
        logger.info("Starting complete MENA AI/ML job market analysis...")
        
        try:
            # Step 1: Scrape all job sources
            jobs = self.scrape_all_sources()
            
            if not jobs:
                logger.error("No jobs were collected. Please check your internet connection and try again.")
                return
            
            # Step 2: Analyze the data
            top_roles, location_dist, source_dist, df = self.analyze_jobs(jobs)
            
            # Step 3: Create comprehensive reports
            self.create_comprehensive_report(top_roles, location_dist, source_dist, df)
            
            # Step 4: Display summary
            self._print_summary(df, top_roles, location_dist, source_dist)
            
            logger.info("Analysis completed successfully!")
            logger.info(f"Check the '{RESULTS_DIR}' folder for all generated reports and data files.")
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def _print_summary(self, df: pd.DataFrame, top_roles: pd.Series, 
                      location_dist: pd.Series, source_dist: pd.Series):
        """Print analysis summary to console"""
        print("\n" + "="*60)
        print("MENA AI/ML JOB MARKET ANALYSIS SUMMARY")
        print("="*60)
        
        if not df.empty:
            print(f"\nOVERVIEW")
            print(f"   Total Jobs Found: {len(df)}")
            print(f"   Unique Companies: {df['Company'].nunique()}")
            print(f"   Countries Covered: {df['Country'].nunique()}")
            print(f"   Job Categories: {df['Job_Category'].nunique()}")
            print(f"   Data Sources: {df['Source'].nunique()}")
            
            if not top_roles.empty:
                print(f"\nTOP JOB CATEGORIES")
                for i, (role, count) in enumerate(top_roles.head(5).items(), 1):
                    percentage = (count / len(df)) * 100
                    print(f"   {i}. {role}: {count} jobs ({percentage:.1f}%)")
            
            if not location_dist.empty:
                print(f"\nTOP LOCATIONS")
                for i, (country, count) in enumerate(location_dist.head(5).items(), 1):
                    percentage = (count / len(df)) * 100
                    print(f"   {i}. {country}: {count} jobs ({percentage:.1f}%)")
            
            if not source_dist.empty:
                print(f"\nDATA SOURCES")
                for source, count in source_dist.items():
                    percentage = (count / len(df)) * 100
                    print(f"   {source}: {count} jobs ({percentage:.1f}%)")
        
        print(f"\nGENERATED FILES:")
        print(f"   • PDF Report: {os.path.join(RESULTS_DIR, 'mena_ai_ml_jobs_report.pdf')}")
        print(f"   • Excel Analysis: {os.path.join(RESULTS_DIR, 'mena_ai_ml_jobs_analysis.xlsx')}")
        print(f"   • CSV Data: {os.path.join(RESULTS_DIR, 'mena_ai_ml_jobs_data.csv')}")
        print(f"   • JSON Data: {os.path.join(RESULTS_DIR, 'mena_ai_ml_jobs_data.json')}")
        print(f"   • Markdown Report: {os.path.join(RESULTS_DIR, 'mena_ai_ml_jobs_report.md')}")
        print(f"   • Log File: {os.path.join(RESULTS_DIR, 'scraper.log')}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    scraper = RealMenaJobScraper()
    scraper.run_complete_analysis()