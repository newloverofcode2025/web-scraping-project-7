import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os

# Base URL of the job board to scrape
base_url = 'https://www.indeed.com/jobs?q=software+developer&l=United+States&start='

# Function to scrape a single page of job listings
def scrape_jobs(page):
    url = f'{base_url}{page}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []

    # Find all job listings on the page
    for job in soup.find_all('div', class_='jobsearch-SerpJobCard'):
        title = job.find('a', class_='jobtitle').get_text()
        company = job.find('span', class_='company').get_text()
        location = job.find('div', class_='location').get_text()
        description = job.find('div', class_='summary').get_text()
        date = job.find('span', class_='date').get_text()

        jobs.append({
            'title': title.strip(),
            'company': company.strip(),
            'location': location.strip(),
            'description': description.strip(),
            'date': date.strip()
        })

    return jobs

# Function to scrape multiple pages of job listings
def scrape_multiple_pages(start_page, num_pages):
    jobs = []
    for i in range(start_page, start_page + num_pages):
        print(f'Scraping page {i+1}')
        jobs.extend(scrape_jobs(i * 10))  # Indeed paginates by 10 jobs per page
    return jobs

# Function to save job listings to a CSV file
def save_to_csv(jobs, filename):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

# Function to plot job count by location
def plot_job_count_by_location(jobs, filename):
    df = pd.DataFrame(jobs)
    if 'location' in df.columns:
        location_counts = df['location'].value_counts().head(10)
        location_counts.plot(kind='bar')
        plt.title('Top 10 Locations with Most Job Listings')
        plt.xlabel('Location')
        plt.ylabel('Number of Job Listings')
        plt.tight_layout()
        plt.savefig(filename)
        print(f'Plot saved to {filename}')
    else:
        print("No 'location' column found in the DataFrame.")

# Main function to run the scraper
def main():
    start_page = 0
    num_pages = 5  # Number of pages to scrape
    jobs = scrape_multiple_pages(start_page, num_pages)

    # Ensure the data directory exists
    output_dir = '../data'
    os.makedirs(output_dir, exist_ok=True)

    # Save the data to a CSV file
    output_file = os.path.join(output_dir, 'jobs.csv')
    save_to_csv(jobs, output_file)

    # Ensure the plots directory exists
    plots_dir = '../plots'
    os.makedirs(plots_dir, exist_ok=True)

    # Save the plot to a file
    plot_file = os.path.join(plots_dir, 'job_count_by_location.png')
    plot_job_count_by_location(jobs, plot_file)

if __name__ == '__main__':
    main()