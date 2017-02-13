import requests
import os
import bs4
import datetime
import re
import time

def main():

    url = "https://xkcd.com"  # XKCD URL
    folder_name = "XKCD Comics"

    base_path = os.path.expanduser("~/Desktop/" + folder_name)  # Location to save images

    if not os.path.exists(base_path):
        try:
            os.mkdir(base_path)  # Folder where to save comics
        except FileExistsError:
            print("There was an error creating the directory")

    dir_items = os.listdir(base_path)

    current_amount_downloaded = 1
    prev_last_comic_number = -1

    # Grabs the last comic saved as the new starting point for downloading
    if "log.txt" in dir_items:
        log = open(os.path.join(base_path, 'log.txt'), "rb")
        print("Log already in directory")

        prev_last_comic_number = int(re.findall(r'\d+', str(log.readlines()[-10:]))[-1]) - 1

        if prev_last_comic_number < 1:
            prev_last_comic_number = -1

        log.close()

    if prev_last_comic_number != -1:
        url = "https://xkcd.com/%d/" % prev_last_comic_number

    log = open(os.path.join(base_path, 'log.txt'), 'a')

    log.write("Starting Download \n")

    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.write("%s\n" % date)
    print(date)

    print("Starting Download")

    while not url.endswith('#') or not (re.findall('/1/', url)):
        log.write("--------------------- \n")

        log.write("Download Number: %d \n" % current_amount_downloaded)
        print("Download Number: %d" % current_amount_downloaded)

        request = requests.get(url)
        request.raise_for_status()  # Stops downloading if something goes wrong with the webpage

        raw = bs4.BeautifulSoup(request.text, "html.parser")  # Passes the raw HTML data to BS4 for parsing

        comic_list = raw.select("#comic img")  # Selects the comic tag

        if len(comic_list) == 0:
            log.write("There was an error when finding the comic, moving to next comic \n")
            print("There was an error when finding the comic, moving to next comic")
            log.write("FAILED")
            prev_comic_url = raw.select('a[rel="prev"]')[0]
            url = "https://xkcd.com" + prev_comic_url.get('href')
        else:
            try:
                comic_url = "https:" + comic_list[0].get('src')
                log.write("Direct Image Link: %s \n" % comic_url)
                print("Direct Image Link: %s" % comic_url)

                ind_comic_request = requests.get(comic_url)
                ind_comic_request.raise_for_status()

                log.write("Requesting page: %s \n" % url)
                print("Requesting page %s" % url)

                if os.path.basename(comic_url) in dir_items:
                    log.write("Comic already in directory, moving to next comic \n")
                    print("Comic already in directory, moving to next comic")
                    # Gets the URL of the previous button to move to next comic
                    prev_comic_url = raw.select('a[rel="prev"]')[0]
                    url = "https://xkcd.com" + prev_comic_url.get('href')
                    continue
                else:
                    comic_image = open(os.path.join(base_path, os.path.basename(comic_url)), 'wb')

                    for chunk in ind_comic_request.iter_content(1000000):
                        comic_image.write(chunk)
                    comic_image.close()

                    # Gets the URL of the previous button to move to next comic
                    prev_comic_url = raw.select('a[rel="prev"]')[0]
                    url = "https://xkcd.com" + prev_comic_url.get('href')

                    current_amount_downloaded += 1

                    if current_amount_downloaded % 25 == 0:  # Wait every 25 downloads, ease server load
                        wait_time = 5  # Amount of time to wait between batch requests in seconds
                        print("Waiting %d seconds until next server request" % wait_time)
                        # Wait 5 seconds before getting next batch of images, easier on the server
                        time.sleep(wait_time)

                    # raw_html_file = open(os.path.join(base_path, os.path.basename(comic_url)) + ".html", 'w')
                    # print("Basename: %s" % os.path.basename(comic_url))
                    # raw_html_file.write(request.text)

            except requests.RequestException:
                log.write("Error downloading comic, moving to next comic")
                print("Error downloading comic, moving to next comic")
                prev_comic_url = raw.select('a[rel="prev"]')[0]
                url = "https://xkcd.com" + prev_comic_url.get('href')

    log.write("--------------------- \n")
    log.write("Done downloading all comics \n")
    log.close()


if __name__ == "__main__":
    main()
