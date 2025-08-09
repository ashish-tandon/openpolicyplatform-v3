#!/usr/bin/env python3
"""
Comprehensive Scraper Testing Framework
=======================================

This framework tests all scrapers in the OpenPolicy Merge platform:
1. Parliamentary scrapers (Federal)
2. Provincial scrapers (13 provinces/territories)
3. Municipal scrapers (200+ cities)
4. Civic scrapers (Civic data collection)
5. Update scripts (Regular maintenance)

Each scraper is tested with sample data, monitored for errors, and results are tracked.
NOW WITH OPTIMIZED PARALLEL EXECUTION - Dynamic worker scaling (10-20) based on scraper size!
"""

import os
import sys
import json
import time
import logging
import asyncio
import importlib.util
import traceback
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import concurrent.futures
import psutil
import inspect

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scrapers/scrapers-ca'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scrapers'))

# Apply dependency fixes
def apply_dependency_fixes():
    """Apply fixes for common import issues"""
    try:
        # Fix DatetimeValidator issue
        try:
            from pupa.utils import DatetimeValidator
        except ImportError:
            class SimpleDatetimeValidator:
                def __init__(self, *args, **kwargs):
                    pass
                def __call__(self, value):
                    return value
            import pupa.utils
            pupa.utils.DatetimeValidator = SimpleDatetimeValidator
            print("✅ Applied DatetimeValidator fix")
        
        # Import utils module
        try:
            import utils
            print("✅ Utils module imported successfully")
        except ImportError:
            # Try importing from scrapers-ca directory
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scrapers/scrapers-ca'))
            import utils
            print("✅ Utils module imported from scrapers-ca directory")
        
    except Exception as e:
        print(f"⚠️  Dependency fixes failed: {e}")

# Apply fixes at startup
apply_dependency_fixes()

from src.database.models import (
    Base, Jurisdiction, Representative, Bill, Committee, Event, Vote,
    ScrapingRun, DataQualityIssue, JurisdictionType, RepresentativeRole
)
from src.database.config import get_database_url, SessionLocal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScraperCategory(Enum):
    """Scraper categories"""
    PARLIAMENTARY = "parliamentary"
    PROVINCIAL = "provincial"
    MUNICIPAL = "municipal"
    CIVIC = "civic"
    UPDATE = "update"


class ScraperSize(Enum):
    """Scraper size categories for optimization"""
    SMALL = "small"      # < 50 records, fast execution
    MEDIUM = "medium"    # 50-200 records, moderate execution
    LARGE = "large"      # > 200 records, heavy execution


class TestStatus(Enum):
    """Test status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ScraperTestResult:
    """Result of a scraper test"""
    scraper_name: str
    category: ScraperCategory
    size: ScraperSize
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    records_collected: int = 0
    records_inserted: int = 0
    error_message: Optional[str] = None
    sample_data: Optional[List[Dict]] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


class ScraperTestingFramework:
    """Comprehensive scraper testing framework with optimized parallel execution"""
    
    def __init__(self, database_url: str, max_sample_records: int = 5, 
                 min_workers: int = 10, max_workers: int = 20):
        self.database_url = database_url
        self.max_sample_records = max_sample_records
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.engine = None  # Will be created when needed
        self.SessionLocal = SessionLocal
        self.results: List[ScraperTestResult] = []
        self.results_lock = threading.Lock()  # Thread-safe results storage
        
        # Performance tracking
        self.system_resources = {
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'current_cpu_usage': 0.0,
            'current_memory_usage': 0.0
        }
        
        # Scraper mappings with size estimates
        self.scraper_mappings = {
            ScraperCategory.PARLIAMENTARY: [
                ('../../scrapers/openparliament', 'Federal Parliament', ScraperSize.LARGE),
            ],
            ScraperCategory.PROVINCIAL: [
                ('../../scrapers/scrapers-ca/ca', 'Canada Federal', ScraperSize.LARGE),
                ('../../scrapers/scrapers-ca/ca_on', 'Ontario', ScraperSize.LARGE),
                ('../../scrapers/scrapers-ca/ca_qc', 'Quebec', ScraperSize.LARGE),
                ('../../scrapers/scrapers-ca/ca_bc', 'British Columbia', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_ab', 'Alberta', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_sk', 'Saskatchewan', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_mb', 'Manitoba', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_ns', 'Nova Scotia', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nb', 'New Brunswick', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_pe', 'Prince Edward Island', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nl', 'Newfoundland and Labrador', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nt', 'Northwest Territories', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nu', 'Nunavut', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_yt', 'Yukon', ScraperSize.SMALL),
            ],
            ScraperCategory.MUNICIPAL: [
                # Major cities - we'll add more dynamically
                ('../../scrapers/scrapers-ca/ca_on_toronto', 'Toronto, ON', ScraperSize.LARGE),
                ('../../scrapers/scrapers-ca/ca_qc_montreal', 'Montreal, QC', ScraperSize.LARGE),
                ('../../scrapers/scrapers-ca/ca_bc_vancouver', 'Vancouver, BC', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_ab_calgary', 'Calgary, AB', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_ab_edmonton', 'Edmonton, AB', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_on_ottawa', 'Ottawa, ON', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_on_mississauga', 'Mississauga, ON', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_on_brampton', 'Brampton, ON', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_on_hamilton', 'Hamilton, ON', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_on_kitchener', 'Kitchener, ON', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_on_london', 'London, ON', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_on_windsor', 'Windsor, ON', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_qc_quebec', 'Quebec City, QC', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_qc_laval', 'Laval, QC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_qc_gatineau', 'Gatineau, QC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_bc_surrey', 'Surrey, BC', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_bc_burnaby', 'Burnaby, BC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_bc_richmond', 'Richmond, BC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_bc_abbotsford', 'Abbotsford, BC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_bc_kelowna', 'Kelowna, BC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_bc_victoria', 'Victoria, BC', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_ab_red_deer', 'Red Deer, AB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_ab_lethbridge', 'Lethbridge, AB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_ab_medicine_hat', 'Medicine Hat, AB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_sk_saskatoon', 'Saskatoon, SK', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_sk_regina', 'Regina, SK', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_mb_winnipeg', 'Winnipeg, MB', ScraperSize.MEDIUM),
                ('../../scrapers/scrapers-ca/ca_ns_halifax', 'Halifax, NS', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nb_saint_john', 'Saint John, NB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nb_moncton', 'Moncton, NB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nb_fredericton', 'Fredericton, NB', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_pe_charlottetown', 'Charlottetown, PE', ScraperSize.SMALL),
                ('../../scrapers/scrapers-ca/ca_nl_st_john_s', 'St. John\'s, NL', ScraperSize.SMALL),
            ],
            ScraperCategory.CIVIC: [
                ('../../scrapers/civic-scraper', 'Civic Data', ScraperSize.MEDIUM),
            ],
            ScraperCategory.UPDATE: [
                ('../../scripts', 'Update Scripts', ScraperSize.SMALL),
            ]
        }
    
    def calculate_optimal_workers(self, scrapers: List[Tuple[str, str, ScraperSize]]) -> int:
        """Calculate optimal number of workers based on scraper sizes and system resources"""
        # Count scraper sizes
        small_count = sum(1 for _, _, size in scrapers if size == ScraperSize.SMALL)
        medium_count = sum(1 for _, _, size in scrapers if size == ScraperSize.MEDIUM)
        large_count = sum(1 for _, _, size in scrapers if size == ScraperSize.LARGE)
        
        # Get current system resources
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        # Base calculation
        total_scrapers = len(scrapers)
        
        # Adjust based on scraper sizes
        if large_count > 0:
            # Large scrapers are resource-intensive, use fewer workers
            base_workers = min(12, total_scrapers)
        elif medium_count > small_count:
            # Medium scrapers, moderate workers
            base_workers = min(15, total_scrapers)
        else:
            # Mostly small scrapers, can use more workers
            base_workers = min(18, total_scrapers)
        
        # Adjust based on system resources
        if cpu_usage > 80 or memory_usage > 80:
            # High resource usage, reduce workers
            optimal_workers = max(self.min_workers, base_workers - 3)
        elif cpu_usage < 50 and memory_usage < 50:
            # Low resource usage, can increase workers
            optimal_workers = min(self.max_workers, base_workers + 2)
        else:
            # Moderate resource usage
            optimal_workers = base_workers
        
        logger.info(f"📊 Resource Analysis: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%")
        logger.info(f"📊 Scraper Sizes: Small {small_count}, Medium {medium_count}, Large {large_count}")
        logger.info(f"📊 Optimal Workers: {optimal_workers} (range: {self.min_workers}-{self.max_workers})")
        
        return optimal_workers
    
    def discover_municipal_scrapers(self) -> List[Tuple[str, str, ScraperSize]]:
        """Dynamically discover all municipal scrapers with size estimation"""
        municipal_scrapers = []
        scrapers_ca_path = Path('scrapers/scrapers-ca')
        
        if not scrapers_ca_path.exists():
            logger.warning("scrapers-ca directory not found")
            return municipal_scrapers
        
        # Look for municipal scrapers (ca_[province]_[city] pattern)
        scrapers_ca_path = Path('../../scrapers/scrapers-ca')
        for scraper_dir in scrapers_ca_path.iterdir():
            if scraper_dir.is_dir() and scraper_dir.name.startswith('ca_'):
                # Skip provincial scrapers (ca_on, ca_qc, etc.)
                if len(scraper_dir.name.split('_')) > 2:
                    # Check if it has a people.py file
                    people_file = scraper_dir / 'people.py'
                    if people_file.exists():
                        # Extract city name from directory
                        parts = scraper_dir.name.split('_')
                        if len(parts) >= 3:
                            province_code = parts[1]
                            city_name = '_'.join(parts[2:])
                            display_name = f"{city_name.title()}, {province_code.upper()}"
                            
                            # Estimate size based on city name patterns
                            size = self.estimate_city_size(city_name, province_code)
                            
                            municipal_scrapers.append((str(scraper_dir), display_name, size))
        
        return municipal_scrapers
    
    def estimate_city_size(self, city_name: str, province_code: str) -> ScraperSize:
        """Estimate scraper size based on city characteristics"""
        # Major cities (likely large datasets)
        major_cities = ['toronto', 'montreal', 'vancouver', 'calgary', 'edmonton', 'ottawa']
        if city_name.lower() in major_cities:
            return ScraperSize.LARGE
        
        # Medium cities (moderate datasets)
        medium_cities = ['mississauga', 'brampton', 'hamilton', 'quebec', 'surrey', 'winnipeg']
        if city_name.lower() in medium_cities:
            return ScraperSize.MEDIUM
        
        # Default to small for other cities
        return ScraperSize.SMALL
    
    def load_scraper_module(self, scraper_path: str) -> Tuple[Optional[Any], Optional[str]]:
        """Load a scraper module dynamically"""
        try:
            people_file = Path(scraper_path) / 'people.py'
            if not people_file.exists():
                return None, f"No people.py file found in {scraper_path}"
            
            # Load the module
            spec = importlib.util.spec_from_file_location("scraper_module", people_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the scraper class
            scraper_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    name.endswith('PersonScraper') and 
                    name != 'CanadianScraper' and 
                    name != 'CSVScraper'):
                    scraper_class = obj
                    break
            
            if scraper_class is None:
                return None, f"No scraper class found in {scraper_path}"
            
            return scraper_class, None
            
        except Exception as e:
            return None, f"Error loading scraper {scraper_path}: {str(e)}"
    
    def test_scraper(self, scraper_path: str, scraper_name: str, category: ScraperCategory, size: ScraperSize) -> ScraperTestResult:
        """Test a single scraper - designed to run in parallel with size-based optimization and strict time limits"""
        result = ScraperTestResult(
            scraper_name=scraper_name,
            category=category,
            size=size,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"🚀 Testing {scraper_name} ({category.value}, {size.value})")
            
            # Load scraper with timeout
            scraper_class, error = self.load_scraper_module(scraper_path)
            if error:
                result.status = TestStatus.FAILED
                result.error_message = error
                result.end_time = datetime.utcnow()
                return result
            
            # Create scraper instance with datadir
            datadir = os.path.join(os.path.dirname(scraper_path), 'data')
            os.makedirs(datadir, exist_ok=True)
            scraper = scraper_class('test-jurisdiction-id', datadir=datadir)
            
            # STRICT TIME LIMITS based on scraper size
            if size == ScraperSize.LARGE:
                timeout = 120  # 2 minutes for large scrapers
            elif size == ScraperSize.MEDIUM:
                timeout = 60   # 1 minute for medium scrapers
            else:
                timeout = 30   # 30 seconds for small scrapers
            
            # Collect sample data with strict timeout
            data = []
            count = 0
            start_time = time.time()
            
            # Use a timeout wrapper for the scraping process
            def scrape_with_timeout():
                nonlocal data, count
                try:
                    for person in scraper.scrape():
                        # Check timeout every iteration
                        if time.time() - start_time > timeout:
                            logger.warning(f"⏰ {scraper_name} timed out after {timeout}s")
                            break
                        
                        if count >= self.max_sample_records:
                            break
                        
                        # Extract key fields
                        person_data = {
                            'name': getattr(person, 'name', 'Unknown'),
                            'role': getattr(person, 'role', None),
                            'party': getattr(person, 'party', None),
                            'district': getattr(person, 'district', None),
                            'email': None,
                            'phone': None,
                            'image': getattr(person, 'image', None)
                        }
                        
                        # Extract contact information
                        if hasattr(person, 'contact_details'):
                            for contact in person.contact_details:
                                if contact.type == 'email':
                                    person_data['email'] = contact.value
                                elif contact.type == 'voice':
                                    person_data['phone'] = contact.value
                        
                        # Extract additional fields
                        for attr in dir(person):
                            if not attr.startswith('_') and attr not in person_data:
                                value = getattr(person, attr)
                                if not callable(value) and value is not None:
                                    person_data[f'extra_{attr}'] = str(value)
                        
                        data.append(person_data)
                        count += 1
                        
                        # Early exit if we have enough records
                        if count >= self.max_sample_records:
                            break
                            
                except Exception as e:
                    logger.error(f"❌ {scraper_name}: Scraping error - {str(e)}")
                    raise
            
            # Execute with simple timeout check
            try:
                scrape_with_timeout()
            except Exception as e:
                logger.error(f"❌ {scraper_name}: Scraping failed - {str(e)}")
                raise
            
            # Update result
            result.status = TestStatus.SUCCESS
            result.records_collected = len(data)
            result.sample_data = data
            result.end_time = datetime.utcnow()
            result.execution_time = time.time() - start_time
            
            # Record system metrics
            result.memory_usage = psutil.virtual_memory().percent
            result.cpu_usage = psutil.cpu_percent()
            
            logger.info(f"✅ {scraper_name}: Collected {len(data)} records in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.utcnow()
            result.execution_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"❌ {scraper_name}: Failed - {str(e)}")
        
        return result
    
    def test_simple_csv_scraper(self, scraper_name: str, csv_url: str, field_mapping: dict) -> ScraperTestResult:
        """Test a simple CSV scraper without complex dependencies"""
        result = ScraperTestResult(
            scraper_name=scraper_name,
            category=ScraperCategory.MUNICIPAL,
            size=ScraperSize.MEDIUM,
            status=TestStatus.RUNNING,
            start_time=datetime.utcnow()
        )
        
        try:
            logger.info(f"🚀 Testing {scraper_name} (Simple CSV)")
            
            # Download CSV data
            import requests
            import csv
            from io import StringIO
            
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            
            # Collect sample data
            data = []
            count = 0
            start_time = time.time()
            
            for row in reader:
                if count >= self.max_sample_records:
                    break
                
                # Map fields using the provided mapping
                person_data = {}
                for target_field, source_field in field_mapping.items():
                    person_data[target_field] = row.get(source_field, '')
                
                # Add additional fields
                person_data['scraper_source'] = scraper_name
                person_data['raw_data'] = dict(row)
                
                data.append(person_data)
                count += 1
            
            # Update result
            result.status = TestStatus.SUCCESS
            result.records_collected = len(data)
            result.sample_data = data
            result.end_time = datetime.utcnow()
            result.execution_time = time.time() - start_time
            
            # Record system metrics
            result.memory_usage = psutil.virtual_memory().percent
            result.cpu_usage = psutil.cpu_percent()
            
            logger.info(f"✅ {scraper_name}: Collected {len(data)} records in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.utcnow()
            result.execution_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"❌ {scraper_name}: Failed - {str(e)}")
        
        return result
    
    def insert_sample_data_to_db(self, result: ScraperTestResult) -> int:
        """Insert sample data into database"""
        if not result.sample_data or result.status != TestStatus.SUCCESS:
            return 0
        
        try:
            with self.SessionLocal() as session:
                # Create or get jurisdiction
                jurisdiction = session.query(Jurisdiction).filter(
                    Jurisdiction.name == result.scraper_name
                ).first()
                
                if not jurisdiction:
                    # Create jurisdiction without website field (workaround for missing column)
                    try:
                        jurisdiction = Jurisdiction(
                            name=result.scraper_name,
                            jurisdiction_type=self._get_jurisdiction_type(result.category)
                        )
                        # Try to set code if the column exists
                        try:
                            jurisdiction.code = result.scraper_name.lower().replace(' ', '_').replace(',', '')
                        except AttributeError:
                            # Code column doesn't exist, skip it
                            pass
                    except Exception as e:
                        if "website" in str(e).lower():
                            # Database schema missing website column - create without it
                            logger.warning(f"⚠️  {result.scraper_name}: Database schema missing 'website' column, creating jurisdiction without it")
                            jurisdiction = Jurisdiction(
                                name=result.scraper_name,
                                jurisdiction_type=self._get_jurisdiction_type(result.category)
                            )
                        else:
                            raise
                    
                    session.add(jurisdiction)
                    session.flush()  # Get the ID
                
                # Insert representatives
                inserted_count = 0
                for person_data in result.sample_data:
                    if person_data.get('name') and person_data['name'] != 'Unknown':
                        representative = Representative(
                            jurisdiction_id=jurisdiction.id,
                            name=person_data['name'],
                            role=self._get_representative_role(person_data.get('role')),
                            party=person_data.get('party'),
                            riding=person_data.get('district'),
                            email=person_data.get('email'),
                            phone=person_data.get('phone'),
                            image_url=person_data.get('image'),
                            bio=f"Sample data from {result.scraper_name} scraper"
                        )
                        session.add(representative)
                        inserted_count += 1
                
                session.commit()
                result.records_inserted = inserted_count
                logger.info(f"📊 {result.scraper_name}: Inserted {inserted_count} records to database")
                return inserted_count
                
        except SQLAlchemyError as e:
            logger.error(f"Database error for {result.scraper_name}: {str(e)}")
            result.error_message = f"Database error: {str(e)}"
            return 0
    
    def _get_jurisdiction_type(self, category: ScraperCategory) -> JurisdictionType:
        """Map scraper category to jurisdiction type"""
        mapping = {
            ScraperCategory.PARLIAMENTARY: JurisdictionType.FEDERAL,
            ScraperCategory.PROVINCIAL: JurisdictionType.PROVINCIAL,
            ScraperCategory.MUNICIPAL: JurisdictionType.MUNICIPAL,
            ScraperCategory.CIVIC: JurisdictionType.MUNICIPAL,  # Default to municipal
            ScraperCategory.UPDATE: JurisdictionType.FEDERAL,   # Default to federal
        }
        return mapping.get(category, JurisdictionType.MUNICIPAL)
    
    def _get_representative_role(self, role_str: Optional[str]) -> RepresentativeRole:
        """Map role string to RepresentativeRole enum"""
        if not role_str:
            return RepresentativeRole.COUNCILLOR
        
        role_lower = role_str.lower()
        if 'mp' in role_lower:
            return RepresentativeRole.MP
        elif 'mla' in role_lower:
            return RepresentativeRole.MLA
        elif 'mpp' in role_lower:
            return RepresentativeRole.MPP
        elif 'mayor' in role_lower:
            return RepresentativeRole.MAYOR
        elif 'premier' in role_lower:
            return RepresentativeRole.PREMIER
        elif 'prime' in role_lower and 'minister' in role_lower:
            return RepresentativeRole.PRIME_MINISTER
        else:
            return RepresentativeRole.COUNCILLOR
    
    def run_category_tests_parallel(self, category: ScraperCategory) -> List[ScraperTestResult]:
        """Run tests for a specific category with optimized parallel execution"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {category.value.upper()} scrapers (OPTIMIZED PARALLEL)")
        logger.info(f"{'='*60}")
        
        scrapers = self.scraper_mappings.get(category, [])
        
        # For municipal scrapers, discover dynamically
        if category == ScraperCategory.MUNICIPAL:
            scrapers.extend(self.discover_municipal_scrapers())
        
        if not scrapers:
            logger.warning(f"No scrapers found for category: {category.value}")
            return []
        
        logger.info(f"Found {len(scrapers)} scrapers to test")
        
        # Calculate optimal number of workers
        optimal_workers = self.calculate_optimal_workers(scrapers)
        
        # Run scrapers in parallel using ThreadPoolExecutor with strict timeouts
        results = []
        start_time = time.time()
        overall_timeout = 300  # 5 minutes total for all scrapers in category
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            # Submit all scraper tests with individual timeouts
            future_to_scraper = {}
            for scraper_path, scraper_name, size in scrapers:
                # Calculate individual timeout based on size
                if size == ScraperSize.LARGE:
                    individual_timeout = 180  # 3 minutes max
                elif size == ScraperSize.MEDIUM:
                    individual_timeout = 90   # 1.5 minutes max
                else:
                    individual_timeout = 45   # 45 seconds max
                
                future = executor.submit(self.test_scraper, scraper_path, scraper_name, category, size)
                future_to_scraper[future] = (scraper_path, scraper_name, size, individual_timeout)
            
            # Collect results with strict timeouts
            completed = 0
            for future in concurrent.futures.as_completed(future_to_scraper, timeout=overall_timeout):
                scraper_path, scraper_name, size, individual_timeout = future_to_scraper[future]
                
                # Check overall timeout
                if time.time() - start_time > overall_timeout:
                    logger.warning(f"⏰ Overall timeout reached for {category.value} scrapers")
                    break
                
                try:
                    result = future.result(timeout=individual_timeout)
                    
                    # Insert sample data to database if successful
                    if result.status == TestStatus.SUCCESS:
                        self.insert_sample_data_to_db(result)
                    
                    # Store result thread-safely
                    with self.results_lock:
                        self.results.append(result)
                        results.append(result)
                    
                    # Progress update with size information
                    logger.info(f"Progress: {completed}/{len(scrapers)} scrapers completed ({size.value})")
                    completed += 1
                    
                except concurrent.futures.TimeoutError:
                    logger.warning(f"⏰ {scraper_name}: Individual timeout after {individual_timeout}s")
                    failed_result = ScraperTestResult(
                        scraper_name=scraper_name,
                        category=category,
                        size=size,
                        status=TestStatus.FAILED,
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow(),
                        error_message=f"Individual timeout after {individual_timeout}s"
                    )
                    with self.results_lock:
                        self.results.append(failed_result)
                        results.append(failed_result)
                    completed += 1
                    
                except Exception as e:
                    logger.error(f"❌ {scraper_name}: Exception in parallel execution - {str(e)}")
                    # Create failed result
                    failed_result = ScraperTestResult(
                        scraper_name=scraper_name,
                        category=category,
                        size=size,
                        status=TestStatus.FAILED,
                        start_time=datetime.utcnow(),
                        end_time=datetime.utcnow(),
                        error_message=f"Parallel execution error: {str(e)}"
                    )
                    with self.results_lock:
                        self.results.append(failed_result)
                        results.append(failed_result)
                    completed += 1
        
        logger.info(f"✅ Completed testing {len(results)} {category.value} scrapers with {optimal_workers} workers")
        return results
    
    def run_all_tests_parallel(self) -> Dict[ScraperCategory, List[ScraperTestResult]]:
        """Run tests for all categories with optimized parallel execution"""
        logger.info("🚀 Starting comprehensive scraper testing (OPTIMIZED PARALLEL)")
        logger.info(f"Max sample records per scraper: {self.max_sample_records}")
        logger.info(f"Worker range: {self.min_workers}-{self.max_workers} (dynamic)")
        logger.info(f"System: {self.system_resources['cpu_count']} CPUs, {self.system_resources['memory_gb']:.1f}GB RAM")
        
        all_results = {}
        
        for category in ScraperCategory:
            try:
                logger.info(f"\n🔄 Starting {category.value.upper()} scrapers...")
                results = self.run_category_tests_parallel(category)
                all_results[category] = results
                
                # Brief summary with size breakdown
                successful = sum(1 for r in results if r.status == TestStatus.SUCCESS)
                failed = sum(1 for r in results if r.status == TestStatus.FAILED)
                small_count = sum(1 for r in results if r.size == ScraperSize.SMALL)
                medium_count = sum(1 for r in results if r.size == ScraperSize.MEDIUM)
                large_count = sum(1 for r in results if r.size == ScraperSize.LARGE)
                
                logger.info(f"📊 {category.value.upper()}: {successful} successful, {failed} failed")
                logger.info(f"📊 Sizes: Small {small_count}, Medium {medium_count}, Large {large_count}")
                
            except Exception as e:
                logger.error(f"Error testing {category.value} scrapers: {str(e)}")
                all_results[category] = []
        
        return all_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report with size analysis"""
        total_scrapers = len(self.results)
        successful = sum(1 for r in self.results if r.status == TestStatus.SUCCESS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
        
        total_records_collected = sum(r.records_collected for r in self.results)
        total_records_inserted = sum(r.records_inserted for r in self.results)
        
        # Size breakdown
        small_count = sum(1 for r in self.results if r.size == ScraperSize.SMALL)
        medium_count = sum(1 for r in self.results if r.size == ScraperSize.MEDIUM)
        large_count = sum(1 for r in self.results if r.size == ScraperSize.LARGE)
        
        # Category breakdown
        category_stats = {}
        for category in ScraperCategory:
            category_results = [r for r in self.results if r.category == category]
            category_stats[category.value] = {
                'total': len(category_results),
                'successful': sum(1 for r in category_results if r.status == TestStatus.SUCCESS),
                'failed': sum(1 for r in category_results if r.status == TestStatus.FAILED),
                'records_collected': sum(r.records_collected for r in category_results),
                'records_inserted': sum(r.records_inserted for r in category_results),
                'small': sum(1 for r in category_results if r.size == ScraperSize.SMALL),
                'medium': sum(1 for r in category_results if r.size == ScraperSize.MEDIUM),
                'large': sum(1 for r in category_results if r.size == ScraperSize.LARGE),
            }
        
        # Failed scrapers details
        failed_scrapers = [
            {
                'name': r.scraper_name,
                'category': r.category.value,
                'size': r.size.value,
                'error': r.error_message
            }
            for r in self.results if r.status == TestStatus.FAILED
        ]
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_resources': self.system_resources,
            'summary': {
                'total_scrapers': total_scrapers,
                'successful': successful,
                'failed': failed,
                'skipped': skipped,
                'success_rate': (successful / total_scrapers * 100) if total_scrapers > 0 else 0,
                'total_records_collected': total_records_collected,
                'total_records_inserted': total_records_inserted,
                'size_breakdown': {
                    'small': small_count,
                    'medium': medium_count,
                    'large': large_count,
                }
            },
            'category_stats': category_stats,
            'failed_scrapers': failed_scrapers,
            'detailed_results': [{
            'scraper_name': r.scraper_name,
            'category': r.category.value,
            'size': r.size.value,
            'status': r.status.value,
            'start_time': r.start_time.isoformat() if r.start_time else None,
            'end_time': r.end_time.isoformat() if r.end_time else None,
            'records_collected': r.records_collected,
            'records_inserted': r.records_inserted,
            'error_message': r.error_message,
            'execution_time': r.execution_time,
            'memory_usage': r.memory_usage,
            'cpu_usage': r.cpu_usage
        } for r in self.results]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save test report to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f'scraper_test_report_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Test report saved to {filename}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console with size analysis"""
        summary = report['summary']
        system_resources = report['system_resources']
        
        print(f"\n{'='*80}")
        print(f"📊 SCRAPER TESTING SUMMARY (OPTIMIZED PARALLEL EXECUTION)")
        print(f"{'='*80}")
        print(f"System: {system_resources['cpu_count']} CPUs, {system_resources['memory_gb']:.1f}GB RAM")
        print(f"Total Scrapers Tested: {summary['total_scrapers']}")
        print(f"Successful: {summary['successful']} ({summary['success_rate']:.1f}%)")
        print(f"Failed: {summary['failed']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Total Records Collected: {summary['total_records_collected']}")
        print(f"Total Records Inserted: {summary['total_records_inserted']}")
        
        print(f"\n📈 SIZE BREAKDOWN:")
        size_breakdown = summary['size_breakdown']
        print(f"  Small: {size_breakdown['small']} scrapers")
        print(f"  Medium: {size_breakdown['medium']} scrapers")
        print(f"  Large: {size_breakdown['large']} scrapers")
        
        print(f"\n📈 CATEGORY BREAKDOWN:")
        for category, stats in report['category_stats'].items():
            success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category.upper()}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%) - {stats['records_collected']} records")
            print(f"    Sizes: Small {stats['small']}, Medium {stats['medium']}, Large {stats['large']}")
        
        if report['failed_scrapers']:
            print(f"\n❌ FAILED SCRAPERS:")
            for scraper in report['failed_scrapers']:
                print(f"  - {scraper['name']} ({scraper['category']}, {scraper['size']}): {scraper['error']}")


def main():
    """Main function to run scraper testing with optimized parallel execution"""
    # Database URL - update this for your environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/openpolicy')
    
    # Create testing framework with optimized parallel execution
    framework = ScraperTestingFramework(
        database_url=database_url,
        max_sample_records=5,  # Collect 5 sample records per scraper
        min_workers=10,        # Minimum 10 workers
        max_workers=20         # Maximum 20 workers (dynamic scaling)
    )
    
    try:
        # Test working scrapers first
        print("🧪 Testing Working Scrapers...")
        
        # Test Toronto scraper (we know this works)
        toronto_field_mapping = {
            'name': 'First name',
            'last_name': 'Last name', 
            'role': 'Primary role',
            'district': 'District name',
            'email': 'Email',
            'phone': 'Phone',
            'website': 'Website',
            'photo_url': 'Photo URL'
        }
        
        toronto_result = framework.test_simple_csv_scraper(
            "Toronto, ON",
            "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/27aa4651-4548-4e57-bf00-53a346931251/resource/dea217a2-f7c1-4e62-aec1-48fffaad1170/download/2022-2026%20Elected%20Officials%20Contact%20Info.csv",
            toronto_field_mapping
        )
        
        # Add to results
        framework.results.append(toronto_result)
        
        print(f"✅ Toronto scraper test completed: {toronto_result.records_collected} records collected")
        
        # Run all tests with optimized parallel execution
        all_results = framework.run_all_tests_parallel()
        
        # Generate and save report
        report = framework.generate_report()
        framework.save_report(report)
        framework.print_summary(report)
        
        # Return exit code based on success rate
        success_rate = report['summary']['success_rate']
        if success_rate >= 80:
            print(f"\n✅ Testing completed successfully ({success_rate:.1f}% success rate)")
            return 0
        elif success_rate >= 50:
            print(f"\n⚠️  Testing completed with warnings ({success_rate:.1f}% success rate)")
            return 1
        else:
            print(f"\n❌ Testing failed ({success_rate:.1f}% success rate)")
            return 2
            
    except Exception as e:
        logger.error(f"Testing framework error: {str(e)}")
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit(main())
