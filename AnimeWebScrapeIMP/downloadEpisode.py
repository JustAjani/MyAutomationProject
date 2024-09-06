import os
import time
import base64

class DownloadManager:
    def __init__(self, driver):
        self.driver = driver

    def manageDownloads(self):
        path_folder = r'C:\\Users\\ajani\\Downloads\\animeScrape'
        while True:
            if self.isBTNClick():
                self.downloadEpisode(path_folder)
            time.sleep(1)

    def ensureDirectoryExists(self, path):
        directory = os.path.dirname(path)
        print(f"Checking if directory exists: {directory}")
        if not os.path.exists(directory):
            print(f"Directory does not exist, creating: {directory}")
            os.makedirs(directory)
        else:
            print(f"Directory already exists: {directory}")

    def downloadBTN(self):
        dlBTN = """
                var dlButton = document.createElement('button');
                dlButton.innerText = 'Download Episode';
                dlButton.style.position = 'fixed';
                dlButton.style.top = '10px';
                dlButton.style.right = '10px';
                dlButton.onclick = function() { localStorage.setItem('downloadClicked', 'true'); };
                document.body.appendChild(dlButton);
                """
        self.driver.execute_script(dlBTN)

    def isBTNClick(self):
        download_clicked = self.driver.execute_script("return localStorage.getItem('downloadClicked') === 'true';")
        if download_clicked:
            self.driver.execute_script("localStorage.removeItem('downloadClicked');")  # Reset flag
            return True
        return False

    def downloadEpisode(self, destination):
        try:
            self.ensureDirectoryExists(destination)
            self.handleIframe()  # Assumes handleIframe is defined elsewhere

            timeout = time.time() + 60 * 5  # Wait up to 5 minutes for the video source to load.
            video_src = None

            while time.time() < timeout:
                video_src = self.driver.execute_script("""
                    var video = document.querySelector('#vidcloud-player > div.jw-wrapper.jw-reset > div.jw-media.jw-reset > video');
                    return video ? video.src : null;
                """)
                if video_src and video_src.startswith('blob:'):
                    print(f"Blob URL found: {video_src}")
                    break
                print("Waiting for video source...")
                time.sleep(5)  # Retry every 5 seconds

            if not video_src:
                print("Video source URL not found or not valid.")
                return

            # Handle the blob URL to download the video
            print("Handling blob URL for video.")
            data_url = self.driver.execute_async_script("""
                var blobUrl = arguments[0], callback = arguments[arguments.length - 1];
                var xhr = new XMLHttpRequest();
                xhr.open('GET', blobUrl, true);
                xhr.responseType = 'blob';
                xhr.onload = function() {
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        callback(reader.result);  // Return data URL to Selenium
                    };
                    reader.onerror = function() {
                        callback(null);
                    };
                    reader.readAsDataURL(xhr.response);
                };
                xhr.onerror = xhr.onabort = function() {
                    callback(null);  // Handle errors and aborts
                };
                xhr.send();
            """, video_src)

            if data_url and data_url.startswith('data:'):
                content_type, base64_data = data_url.split(';', 1)
                video_data = base64.b64decode(base64_data.split(',')[1])
                file_extension = content_type.split('/')[1].split(';')[0]

                file_path = os.path.join(destination, f"downloaded_video.{file_extension}")
                with open(file_path, 'wb') as file:
                    file.write(video_data)
                print(f"Video successfully downloaded to {file_path}")
            else:
                print("Failed to convert Blob URL to Data URL.")
        except Exception as e:
            print(f"An error occurred while trying to download the episode: {e}")

    def handleIframe(self):
        pass  # Define the iframe handling logic elsewhere in your main code
