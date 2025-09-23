#!/usr/bin/env python3
"""
Script to scrape all professor data and populate the database
"""

import sys
import os
import time
from typing import Dict, List

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import UndergraduateAssistantDatabase
from scraper.webscrapper import (
    get_html, get_professor_names, get_var_from_prof, 
    get_research_info, get_location_info, get_all_professor_names_with_pagination
)

def get_var_from_prof_optimized(name, total_research_info, total_location_info):
    """
    Optimized version that doesn't re-fetch research and location info
    """
    NEW_URL = f'https://www.khoury.northeastern.edu/people/{name}/'
    profile_soup = get_html(NEW_URL)
    
    if not profile_soup:
        return None
    
    prof_info = {}

    name_element = profile_soup.find(class_='single-people__header-title')
    prof_info['name'] = name_element.get_text(strip=True) if name_element else None
    if prof_info['name']:
        prof_info['name'] = prof_info['name'].replace('\xa0', ' ')
    
    title_element = profile_soup.find(class_='single-people__header-description')
    prof_info['title'] = title_element.get_text(strip=True) if title_element else None

    role_element = profile_soup.find(class_='single-people__aside-roles')
    prof_info['position'] = role_element.get_text(strip=True) if role_element else None

    contact_info = profile_soup.find_all(class_='single-people__aside-list-item')
    research_interests = []

    for item in contact_info:
        text = item.get_text(strip=True)
            
        if text in total_research_info:
            research_interests.append(text)

        if text in total_location_info:
            prof_info['location'] = text
        
        if "@" in text:
            prof_info['email'] = text

        if any(char.isdigit() for char in text) and any(sep in text for sep in ['.', '-', '(', ')']):
            prof_info['phone'] = text

    prof_info['research_interests'] = research_interests

    # Get personal website
    website_section = profile_soup.find('h3', string='Website')
    if website_section:
        website_link = website_section.find_next('a', href=True)
        if website_link:
            prof_info['personal_website'] = website_link['href']
    
    # Get Google Scholar
    if 'google_scholar' not in prof_info:
        all_links = profile_soup.find_all('a', href=True)
        for link in all_links:
            if 'scholar.google.com' in link['href']:
                prof_info['google_scholar'] = link['href']
                break
    
    return prof_info

def scrape_all_professor_data(base_url='https://www.khoury.northeastern.edu/people/', total_pages=56, verbose=True):
    """
    Scrape all professor data from Khoury website using pagination
    
    Args:
        base_url (str): Base URL for scraping
        total_pages (int): Total number of pages to scrape (default 56)
        verbose (bool): Whether to print progress updates
    
    Returns:
        List[Dict]: List of professor dictionaries with all information
    """
    try:
        if verbose:
            print("Starting comprehensive professor data scraping with pagination...")
            print(f"Will scrape {total_pages} pages from {base_url}")
        
        if verbose:
            print("Getting research areas and locations...")
        
        # Get research areas and locations for reference
        total_research_info = get_research_info(base_url)
        total_location_info = get_location_info(base_url)
        
        if verbose:
            print(f"Found {len(total_research_info)} research areas")
            print(f"Found {len(total_location_info)} locations")
        
        # Get all professor names using pagination
        if verbose:
            print(f"\nGetting all professor names from {total_pages} pages...")
        
        professor_names = get_all_professor_names_with_pagination(
            base_url=base_url, 
            total_pages=total_pages, 
            verbose=verbose
        )
        
        if not professor_names:
            raise Exception("No professor names found across all pages")
        
        if verbose:
            print(f"\nScraping individual profiles for {len(professor_names)} professors...")
        
        all_professors_data = []
        failed_scrapes = []
        
        for i, name in enumerate(professor_names, 1):
            try:
                if verbose and i % 20 == 0:
                    print(f"[{i:3d}/{len(professor_names)}] Progress update - scraped {i} professors...")
                elif verbose and i <= 5:
                    print(f"[{i:3d}/{len(professor_names)}] Scraping: {name}")
                
                # Get professor information using optimized function
                prof_info = get_var_from_prof_optimized(name, total_research_info, total_location_info)
                
                if prof_info and prof_info.get('name'):
                    all_professors_data.append(prof_info)
                    
                    # Show a preview for first few professors
                    if verbose and i <= 3:
                        print(f"    Success: {prof_info.get('name', 'Unknown')}")
                        print(f"      Title: {prof_info.get('title', 'N/A')}")
                        print(f"      Location: {prof_info.get('location', 'N/A')}")
                        print(f"      Research: {len(prof_info.get('research_interests', []))} areas")
                        print()
                else:
                    failed_scrapes.append(name)
                    if verbose and i <= 10:
                        print(f"    Failed to scrape {name}")
                
                # Be respectful to the server - more frequent pauses for large scraping
                if i % 25 == 0:
                    if verbose:
                        print("    Taking a brief pause...")
                    time.sleep(2)
                elif i % 10 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                failed_scrapes.append(name)
                if verbose and len(failed_scrapes) <= 10:
                    print(f"    Error scraping {name}: {str(e)[:50]}...")
        
        if verbose:
            print(f"\nComplete Scraping Summary:")
            print(f"   Pages scraped: {total_pages}")
            print(f"   Professor names found: {len(professor_names)}")
            print(f"   Successfully scraped: {len(all_professors_data)}")
            print(f"   Failed to scrape: {len(failed_scrapes)}")
            print(f"   Success rate: {(len(all_professors_data)/len(professor_names)*100):.1f}%")
            
            if failed_scrapes and len(failed_scrapes) <= 5:
                print(f"   Failed names: {', '.join(failed_scrapes)}")
            elif failed_scrapes:
                print(f"   First few failed: {', '.join(failed_scrapes[:3])}...")
        
        return all_professors_data
        
    except Exception as e:
        if verbose:
            print(f"Critical error during scraping: {e}")
        return []

def populate_database(clear_existing=False, verbose=True):
    """
    Populate the database with professor data by scraping all profiles
    
    Args:
        clear_existing (bool): Whether to clear existing data first
        verbose (bool): Whether to print detailed output
    
    Returns:
        dict: Results of the operation
    """
    try:
        if verbose:
            print("Starting complete professor data scraping and population...")
        
        # Initialize database
        db = UndergraduateAssistantDatabase()
        
        # Clear existing data if requested
        if clear_existing:
            db.clear_professors_table()
            if verbose:
                print("Cleared existing professor data.")
        
        # Scrape all professor data
        base_url = 'https://www.khoury.northeastern.edu/people/'
        all_professors = scrape_all_professor_data(base_url, total_pages=56, verbose=verbose)
        
        if not all_professors:
            return {
                'success': False, 
                'error': 'No professor data was scraped',
                'inserted_count': 0,
                'total_scraped': 0
            }
        
        if verbose:
            print(f"\nInserting {len(all_professors)} professors into database...")
            
            # Show sample of data to be inserted
            print("\nSample of scraped data:")
            for i, prof in enumerate(all_professors[:3], 1):
                print(f"{i}. {prof.get('name', 'Unknown')}")
                print(f"   Title: {prof.get('title', 'N/A')}")
                print(f"   Email: {prof.get('email', 'N/A')}")
                print(f"   Location: {prof.get('location', 'N/A')}")
                print(f"   Research interests: {len(prof.get('research_interests', []))} areas")
                print(f"   Website: {prof.get('personal_website', 'N/A')}")
                print(f"   Google Scholar: {prof.get('google_scholar', 'N/A')}")
                print()
            
            if len(all_professors) > 3:
                print(f"   ... and {len(all_professors) - 3} more professors")
        
        # Insert into database
        inserted_count = db.insert_all_professors(all_professors)
        
        if verbose:
            print(f"Successfully inserted {inserted_count} professors into database")
        
        return {
            'success': True,
            'inserted_count': inserted_count,
            'total_scraped': len(all_professors),
            'success_rate': (inserted_count / len(all_professors)) * 100 if all_professors else 0
        }
        
    except Exception as e:
        if verbose:
            print(f"Error during population: {e}")
        return {
            'success': False,
            'error': str(e),
            'inserted_count': 0,
            'total_scraped': 0
        }

def main():
    """Interactive script to populate professor data"""
    print("Undergraduate Assistant - Professor Data Population")
    print("=" * 55)
    
    # Get user preferences
    clear_existing = input("Clear existing professor data? (y/N): ").lower().strip() == 'y'
    
    # Run population
    result = populate_database(clear_existing=clear_existing, verbose=True)
    
    if result['success']:
        # Show statistics
        db = UndergraduateAssistantDatabase()
        stats = db.get_database_stats()
        
        print(f"\nDatabase Statistics:")
        print(f"- Total professors: {stats['total_professors']}")
        print(f"- Unique locations: {stats['unique_locations']}")
        print(f"- Locations: {', '.join(stats['locations']) if stats['locations'] else 'None'}")
        
        # Show popular research areas
        popular_areas = db.get_popular_research_areas('professors')
        if popular_areas:
            print(f"\nTop 5 Research Areas:")
            for i, area in enumerate(popular_areas[:5], 1):
                print(f"{i}. {area['research_area']}: {area['count']} professors")
        
        print(f"\nPopulation completed successfully!")
        print(f"Success rate: {result.get('success_rate', 0):.1f}%")
    else:
        print(f"Population failed: {result['error']}")

if __name__ == "__main__":
    main()