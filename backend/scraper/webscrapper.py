from bs4 import BeautifulSoup
import requests
import time


# Scrape website to find all professors
url = 'https://www.khoury.northeastern.edu/people/'

def get_all_professor_names_with_pagination(base_url='https://www.khoury.northeastern.edu/people/', total_pages=56, verbose=True):
    """
    Get all professor names by iterating through all pages
    
    ARGS:
        base_url: string - base URL for the people page
        total_pages: int - total number of pages to scrape (default 56)
        verbose: bool - whether to print progress
    RETURNS:
        names: list of strings - all professor names across all pages
    """
    all_names = []
    failed_pages = []
    
    for page in range(1, total_pages + 1):
        try:
            if verbose:
                print(f"Scraping page {page}/{total_pages}...")
            
            # Construct URL for current page
            if page == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}page/{page}/"
            
            # Get HTML for current page
            soup = get_html(page_url)
            if not soup:
                failed_pages.append(page)
                if verbose:
                    print(f"  Failed to fetch page {page}")
                continue
            
            # Get professor names from current page
            page_names = get_professor_names(soup)
            
            if not page_names:
                if verbose:
                    print(f"  No professors found on page {page}")
                # If we hit an empty page, we might have reached the end
                if page > 10:  # Only break if we're past the first 10 pages
                    break
            else:
                all_names.extend(page_names)
                if verbose:
                    print(f"  Found {len(page_names)} professors on page {page}")
            
            # Be respectful to the server - small delay between pages
            time.sleep(0.5)
            
        except Exception as e:
            failed_pages.append(page)
            if verbose:
                print(f"  Error scraping page {page}: {str(e)[:50]}...")
    
    if verbose:
        print(f"\nPagination Summary:")
        print(f"  Total professors found: {len(all_names)}")
        print(f"  Pages scraped successfully: {total_pages - len(failed_pages)}")
        if failed_pages:
            print(f"  Failed pages: {failed_pages}")
    
    return all_names

# Step 1: Get html file based on URL.
def get_html(base_url):
    """ This function returns the soup object given a base url.
    ARGS:
        base_url: string
    RETURNS:
        soup: BeautifulSoup object
    """
    str_html = requests.get(base_url).text
    soup = BeautifulSoup(str_html, 'html.parser')
    return soup

# Step 2: Get professor names and put in array of strings.
def get_professor_names(soup):
    """ This function returns a list of professor names given a soup object.
    ARGS:
        soup: BeautifulSoup object
    RETURNS:
        names: list of strings
    """  
    # Uses class name to find each persons name and profile link
    name_element = soup.find_all(class_='standard-card__title')
    names = []

    for element in name_element:
        if(element.get_text().strip() == "Dean’s Welcome To Our Community"):
            continue

        name = element.get_text().strip()
        name = name.replace('\xa0', ' ')
        name = name.lower()
        name = name.replace(" ", "-")
        names.append(name)

    return names

def get_var_from_prof(name):
    """ This function returns name, email, position, research interests, campus location, personal website, Google Scholar citations from a name
    ARGS:
        name: string
    RETURNS:
        name, email, position, research interests, campus location, personal website, Google Scholar citations
    """
    
    NEW_URL = f'https://www.khoury.northeastern.edu/people/{name}/'

    profile_soup = get_html(NEW_URL)
    total_location_info = get_location_info(url)
    total_research_info = get_research_info(url)

    prof_info = {}

    name_element = profile_soup.find(class_='single-people__header-title')
    prof_info['name'] = name_element.get_text(strip=True) if name_element else None
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

    website_section = profile_soup.find('h3', string='Website')
    if website_section:
        # Find the next sibling that contains the link
        website_link = website_section.find_next('a', href=True)
        if website_link:
            prof_info['personal_website'] = website_link['href']
    
    if 'google_scholar' not in prof_info:
        all_links = profile_soup.find_all('a', href=True)
        for link in all_links:
            if 'scholar.google.com' in link['href']:
                prof_info['google_scholar'] = link['href']
                break
    return prof_info



def get_research_info(base_url):
    """ This function returns a list of all research interests given a base url.
    ARGS:
        base_url: string
    RETURNS:
        research_interests: list of strings
    """
    profile_soup = get_html(base_url)

    research_div = profile_soup.find("div", id="filter-dropdown-content-research_areas")

    research_interests = []
    
    if research_div:
        # Find all label elements within the research div
        labels = research_div.find_all("label")
        
        for label in labels:
            # Get the text content of the label (which is the research area name)
            research_area = label.get_text(strip=True)
            if research_area:
                research_interests.append(research_area)
    
    return research_interests

def get_location_info(base_url):
    """ This function returns a list of all campus locations given a base url.
    ARGS:
        base_url: string
    RETURNS:
        locations: list of strings
    """
    profile_soup = get_html(base_url)

    location_div = profile_soup.find("div", id="filter-dropdown-content-locations")
    locations = []

    if location_div:
        # Find all label elements within the location div
        labels = location_div.find_all("label")

        for label in labels:
            # Get the text content of the label (which is the location name)
            location = label.get_text(strip=True)
            if location:
                locations.append(location)
    return locations

# Step 3: Scrape all profiles with pagination support
def scrape_all_profiles(base_url='https://www.khoury.northeastern.edu/people/', use_pagination=True, total_pages=56):
    """ This function scrapes all profiles from the base url and returns a list of dictionaries containing professor information.
    ARGS:
        base_url: string
        use_pagination: bool - whether to use pagination (recommended)
        total_pages: int - number of pages to scrape if using pagination
    RETURNS:
        all_professors_info: list of dictionaries
    """
    if use_pagination:
        # Use pagination to get all professor names
        names = get_all_professor_names_with_pagination(base_url, total_pages, verbose=True)
    else:
        # Old method - just scrape first page
        soup = get_html(base_url)
        names = get_professor_names(soup)
    
    print(f"Found {len(names)} total professors to scrape individual profiles for...")
    
    all_professors_info = []
    failed_scrapes = []

    for i, name in enumerate(names, 1):
        try:
            if i % 10 == 0:  # Print progress every 10 professors
                print(f"Progress: {i}/{len(names)} professors scraped...")
            
            prof_info = get_var_from_prof(name)
            if prof_info:
                all_professors_info.append(prof_info)
            else:
                failed_scrapes.append(name)
                
        except Exception as e:
            failed_scrapes.append(name)
            print(f"Error scraping {name}: {str(e)[:50]}...")
        
        # Small delay to be respectful to the server
        if i % 20 == 0:
            time.sleep(1)

    print(f"\nScraping completed!")
    print(f"Successfully scraped: {len(all_professors_info)} professors")
    print(f"Failed to scrape: {len(failed_scrapes)} professors")
    
    if failed_scrapes and len(failed_scrapes) <= 10:
        print(f"Failed names: {', '.join(failed_scrapes)}")

    return all_professors_info

def scrape_all_profiles_single_page(base_url):
    """ Legacy function - scrapes only the first page (for backward compatibility)
    ARGS:
        base_url: string
    RETURNS:
        all_professors_info: list of dictionaries
    """
    return scrape_all_profiles(base_url, use_pagination=False, total_pages=1)

# Step 4: Take all necessary info from each profile and put in SQL database

# Take all necessary info from each profile and put in SQL database

