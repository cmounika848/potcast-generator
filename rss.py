# Get the Rss Feed 
# Get the Rss Feed from the url
import feedparser
import requests
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from requests.exceptions import RequestException
import time
import base64

def atob(data: str) -> str:
    """Decode a base64 encoded string."""
    try:
        # Decode the base64 string and return the decoded content
        return base64.b64decode(data).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error decoding base64 data: {e}")
        return data
    
def btoa(data: str) -> str:
    """Encode a string to base64."""
    try:
        # Encode the string to base64 and return the encoded content
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Error encoding data to base64: {e}")
        return data
    
def send(url):
    TOKEN = "Tnpnd05qQTBOamcyTkRwQlFVWlBNRkZuT0cxMWIwRTBURWx1YXpCMlNGbGhkVzlrVVRoTFNuRlhaVXBIV1E9PQ=="
    TOKEN = atob(atob(TOKEN))
    chat_id = "-4640170739"
    message = url
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url) # this sends the message
# Set up logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
filtered_data = []
# Set array of URLs
URLs = {
    "https://politepol.com/fd/V5buPLaIoQot.xml",
    "https://politepol.com/fd/uNTJ4RCbv385.xml",
    "https://politepol.com/fd/DcNWUYWHMmaS.xml",
    "https://politepol.com/fd/kPW2JskqeS7h.xml",
    "https://politepol.com/fd/hRHVasLAbKAK.xml",
    "https://politepol.com/fd/EJKak4yHwHoj.xml",
    "https://politepol.com/fd/LW8RCehcu2qH.xml",
    "https://politepol.com/fd/IzucFOyWeckY.xml",
    "https://politepol.com/fd/rKQCktx6iKHS.xml",
    "https://politepol.com/fd/92qskAQ0bwAJ.xml"
}

token = atob(atob("ZEc5clpXNGdaMmwwYUhWaVgzQmhkRjh4TVVKUFZGcFRNbEV3V2tkTlpVWnFXWGg1YVRkeVgwc3dPSEJXVW5CMFFYaElhWG96TkdwelQyNDRSVTlUYURsbFdub3pOblV5TjNaT1ZVRnlaelpXWm14RFRUWkpSbGhGV1c5cU5tUkhkalZQ"))
# get the data from github repository
def get_data_from_github(url: str) -> Optional[Dict[str, Any]]:
    try:
        # Set the Headers and get the sha
        headers= {
                                'Authorization': token,
                            }

        response = requests.get(url, headers=headers)
        response = response.json()

        return json.loads(atob(response['content']))
    except RequestException as e:
        logger.error(f"Error fetching data from GitHub: {e}")
        return None

applied = get_data_from_github("https://api.github.com/repos/cmounika848/potcast-generator/contents/applied.json")

def notify(article):
    url = article["link"]

    headers= {'Authorization': token}
    response = requests.get("https://api.github.com/repos/cmounika848/potcast-generator/contents/notify.json", headers=headers)
    response = response.json()
    # decode the content and load it as json
    currentNotify = json.loads(atob(response['content']))
    # get the sha of the file from github
    sha = response['sha']    
    if url in currentNotify:
        return
    else:
        company = article["company"]
        company = company.split(" | ")[0]
        company = company.replace("#", " Sharp")
        send(article["company"] + " : " + url)
        print("Sending message to telegram for local jobs")

        # update the file with the new url
        currentNotify.append(url)
        headers= {
                                'Authorization': token,
                            }
        data = {
            "message": "Update notify links",
            "content": btoa(json.dumps(currentNotify)),
            "sha": sha
        }
        response = requests.put("https://api.github.com/repos/cmounika848/potcast-generator/contents/notify.json", headers=headers, data=data)
        response = response.json()
        print(response)
print("Applied Jobs:", len(applied))
allData = None
# Define the RSS feed URL
for each in URLs:
    RSS_FEED_URL = each
    # Define the time interval for checking new articles (in hours)
    CHECK_INTERVAL_HOURS = 1
    # Define the time interval for checking new articles (in hours)
    CHECK_INTERVAL = timedelta(hours=CHECK_INTERVAL_HOURS)
    

    # Make the API request to get the RSS feed
    def fetch_rss_feed(url: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return feedparser.parse(response.content)
        except RequestException as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return None

    # Call the function to fetch and save the RSS feed
    def fetch_and_store_rss_feed() -> None:
        global allData
        feed = fetch_rss_feed(RSS_FEED_URL)
        if feed:
            allData = feed
            logger.info("RSS feed successfully fetched and stored in memory.")
        else:
            logger.error("Failed to fetch RSS feed.")
        
    fetch_and_store_rss_feed()

    # Extract the articles from the feed
    def extract_articles(feed: Dict[str, Any]) -> List[Dict[str, Any]]:
        global filtered_data
        articles = []
        for entry in feed.get("entries", []):
            article = {
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published"),
            }
            articles.append(article)
        return articles

    if allData:
        data = extract_articles(allData)
    else:
        data = []

    print("Total Jobs Found:", len(data))
    print("Applying Filter with Remote, .NET and not citizen")
    # Load each article from the feed and check if the content contains the keyword "remote" (case insensitive)
    
    for article in data:
        # get the article link before "?" substring
        if "?" in article["link"]:
            article["link"] = article["link"].split("?")[0]
        link = article["link"]
        
        # link is in applied skip
        #print(f"Checking {link}")
        #print(f"Already applied for {applied}")
        if link in applied:
            #print(f"Already applied for {link}")
            continue
        time.sleep(2)  # Sleep for 2 seconds between requests to avoid overwhelming the server
        res = requests.get(link)
        # After 5 articles exit the loop
        # if len(filtered_data) >= 1:
        #     break
        if res.status_code == 200:
            content = res.text
            if "remote" in content.lower() or "uNTJ4RCbv385" in RSS_FEED_URL or "92qskAQ0bwAJ" in RSS_FEED_URL:
                # content shouldn't include keyword "citizen"
                if "citizen" in content.lower():
                    continue
                # content should include keyword ".net" case insensitive
                if ".net" in content.lower():
                    # Print the loop count
                    
                    title = article["title"]
                    newtitile = title.split('<span class="sr-only">')[1].split('</span>')[0]
                    newtitle = newtitile.replace("\n", "").strip()
                    article["title"] = newtitle
                    #print(newtitle)
                    company = content.split("<title>")[1].split("</title")[0]
                    article["company"] = company
                    print(f"Fetching Job: {len(filtered_data)+1} : {company}")
                    if '<figcaption class="num-applicants__caption">' in content:
                        newContent = content.split('<figcaption class="num-applicants__caption">')[1].split('</figcaption>')[0]
                        newContent = newContent.split('\n')[1].strip()
                        article["applicants"] = newContent
                        # Strip all alpha characters from the string
                        applicantsNumber = ''.join(filter(str.isdigit, newContent))
                        article["applicantsNumber"] = int(applicantsNumber)

                    else:
                        if '<span class="num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet">' in content:
                            newContent = content.split('<span class="num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet">')[1].split('</span>')[0]
                            newContent = newContent.split('\n')[1].strip()
                            article["applicants"] = newContent
                            # Strip all alpha characters from the string
                            applicantsNumber = ''.join(filter(str.isdigit, newContent))
                            article["applicantsNumber"] = int(applicantsNumber)

                        else:
                            #print("No applicants found")
                            article["applicants"] = "0"
                            article["applicantsNumber"] = 0
                            #with open("content.txt", "w", encoding="utf-8") as f:
                            #    f.write(content)
                            #exit(1)
                    if "uNTJ4RCbv385" in RSS_FEED_URL or "92qskAQ0bwAJ" in RSS_FEED_URL:
                        article["type"] = "Local"

                    else:
                        article["type"] = "Remote"
                    filtered_data.append(article)
                    #print(article)
                    continue
                #print(f"Article with link {link} contains 'remote'")
                
            #else:
                #print(f"Article with link {link} does not contain 'remote'")
                # Remove from articles list if it does not contain "remote"
                #data.remove(article)
        else:
            print(f"Failed to fetch article from {link}, status code: {res.status_code}")
        #print(f"Catured jobs so far: {len(filtered_data)}")

    # Remove duplicates based on the 'link' field
unique_links = set()
filtered_data = [article for article in filtered_data if article["link"] not in unique_links and not unique_links.add(article["link"])]

# Sort the filtered data by applicants number in ascending order
filtered_data.sort(key=lambda x: x["applicantsNumber"], reverse=False)

# Create an HTML file with the filtered data using table format with all the columns
print("Filtered Jobs:", len(filtered_data))

for article in filtered_data:
    if article["type"] == "Local":
        notify(article)


def create_html_file(data: List[Dict[str, Any]], filename: str) -> None:
    html_content = """
        <html>
        <head>
            <title>Filtered Articles</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                button {
                    margin: 10px 0;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
            </style>
            <script>
                async function updateVisitedLinks() {
                    try {
                       
                        const links = document.querySelectorAll('a');
                        const visitedLinks = Array.from(links)
                            .filter(link => link.innerText === 'Visited')
                            .map(link => link.href);
                        
                        // Skip if no links are marked as visited
                        if (visitedLinks.length === 0) {
                            alert('No links are marked as visited.');
                            return;
                        }

                        // Fetch the SHA of the file from GitHub
                        const shaResponse = await fetch('https://api.github.com/repos/cmounika848/potcast-generator/contents/applied.json', {
                            headers: {
                                'Authorization': atob(atob('ZEc5clpXNGdaMmwwYUhWaVgzQmhkRjh4TVVKUFZGcFRNbEV3V2tkTlpVWnFXWGg1YVRkeVgwc3dPSEJXVW5CMFFYaElhWG96TkdwelQyNDRSVTlUYURsbFdub3pOblV5TjNaT1ZVRnlaelpXWm14RFRUWkpSbGhGV1c5cU5tUkhkalZQ')),
                                'Content-Type': 'application/json'
                            }
                        });
                        if (!shaResponse.ok) {
                            alert('Failed to fetch SHA of the file.');
                            return;
                        }
                        const shaData = await shaResponse.json();
                        
                        const appliedLinks = JSON.parse(atob(shaData.content));
                        const fileSha = shaData.sha;

                        // Update the applied links on GitHub
                        let updatedLinks = [...new Set([...visitedLinks, ...appliedLinks])];
                        //remove duplicates for updated links
                        updatedLinks = [...new Set(updatedLinks)];
        
                        const updateResponse = await fetch('https://api.github.com/repos/cmounika848/potcast-generator/contents/applied.json', {
                            method: 'PUT',
                            headers: {
                                'Authorization': atob(atob('ZEc5clpXNGdaMmwwYUhWaVgzQmhkRjh4TVVKUFZGcFRNbEV3V2tkTlpVWnFXWGg1YVRkeVgwc3dPSEJXVW5CMFFYaElhWG96TkdwelQyNDRSVTlUYURsbFdub3pOblV5TjNaT1ZVRnlaelpXWm14RFRUWkpSbGhGV1c5cU5tUkhkalZQ')),
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                message: 'Update applied links',
                                content: btoa(JSON.stringify(updatedLinks)),
                                sha: fileSha
                            })
                        });
                        if (updateResponse.ok) {
                            alert('Visited links updated successfully!');
                        } else {
                            alert('Failed to update visited links on GitHub.');
                        }
                    } catch (error) {
                        console.error('Error updating visited links:', error);
                        alert('An error occurred while updating visited links.');
                    }
                }
            </script>
        </head>
        <body>
            <h1>Latest Remote Jobs: .NET</h1>
            <button onclick="updateVisitedLinks()">Update Visited Links</button>
            <table>
                <tr>
                    <th>S.No</th>
                    <th>Posted</th>
                    <th>Title</th>
                    <th>Applicants</th>
                    <th>Type</th>
                    <th>Company</th>
                    <th>Apply</th>
                </tr>
        """

    for article in data:
            html_content += f"""
                <tr>
                <td>{data.index(article) + 1}</td>
                <td>{article['published']}</td>
                <td>{article['title']}</td>
                <td>{article['applicants']}</td>
                <td>{article['type']}</td>
                <td>{article['company']}</td>
                <td><a href="{article['link']}" target="_blank" onclick="this.style.color='gray'; this.innerText='Visited';">URL</a></td>
                </tr>
            """

    html_content += """
            </table>
        </body>
        </html>
        """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

create_html_file(filtered_data, "index.html")
