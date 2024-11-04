import csv
import os
import requests
from bs4 import BeautifulSoup
def remove_film_prefix(country):
    return country.replace('Phim', '').strip()

class CustomWebLoader:
    def __init__(self, url):
        self.url = url

    def load(self):
        film_data = []
        for url in self.url:
            html_docs = requests.get(url)
            soup = BeautifulSoup(html_docs.text, "html.parser")

            # Lấy các thông tin từ trang web
            title = soup.find("h1", class_="title").get_text(strip=True) if soup.find("h1", class_="title") else "N/A"
            name2_div = soup.find("div", class_="name2 fr")
            alt_title = name2_div.find("h3").get_text(strip=True) if soup.find("h3") else "N/A"
            status = soup.find("dd", class_="status").get_text(strip=True) if soup.find("dd",
                                                                                        class_="status") else "N/A"
            status = " ".join(status.split())
            actors = [actor.get_text(strip=True) for actor in soup.find_all("a", href=True) if
                      "/dien-vien/" in actor["href"]]
            genres_tags = soup.select_one(".dinfo.fr .col1")
            genres = [genre.get_text(strip=True) for genre in genres_tags.find_all("a", href=True) if
                      "/the-loai/" in genre["href"]]
            country = soup.find("a", href="/quoc-gia/phim-my").get_text(strip=True) if soup.find("a",
                                                                                                         href="/quoc-gia/phim-my") else "N/A"
            director = soup.find_all("dd")[4].get_text(strip=True) if len(soup.find_all("dd")) > 4 else "N/A"
            duration = soup.find_all("dd")[5].get_text(strip=True) if len(soup.find_all("dd")) > 5 else "N/A"
            newest_episode = soup.select_one(".episodelistinfo span a").get_text(strip=True) if soup.select_one(
                ".episodelistinfo span a") else "N/A"
            like_counts = soup.select_one(".like-stats .votes").get_text(strip=True) if soup.select_one(
                ".like-stats .votes") else "N/A"
            comments_count = soup.select_one(".wpd-thread-info .wpdtc").get_text(strip=True) if soup.select_one(
                ".wpd-thread-info .wpdtc") else "N/A"
            meta_description = soup.find("meta", attrs={"name": "description"})
            film_info = meta_description.get("content", "") if meta_description else "N/A"
            poster_img = soup.find("div", class_="poster").find("img")
            img_url = poster_img["src"]
            combined_text = (
                f"Bộ phim '{title}' còn được biết đến với tên khác là '{alt_title}'. "
                f"{'' if ', '.join(actors) == 'Đang cập nhật' else 'Phim có sự tham gia của diễn viên ' + ', '.join(actors) + '. '}"
                f"{'' if director == 'Đang cập nhật' else 'Phim do đạo diễn ' + director + ' chỉ đạo. '}"
                f"Phim thuộc thể loại '{', '.join(genres)}' và sản xuất tại {remove_film_prefix(country)}. "
                f"Thời gian chiếu là {duration}. "
                f"Tập mới nhất là {newest_episode}, nhận được {like_counts} lượt thích. "
                f"Nội dung: {film_info}."
            )
            film_data.append({
                "Tên phim": title,
                "Hình ảnh": img_url,
                "Lượt thích": like_counts,
                "Lượng bình luận": comments_count,
                "Nội dung phim": combined_text
            })

        return film_data

def extract_url(urls):
    base_url = "https://tvhayw.org"
    films = set()
    html_docs = requests.get(urls)
    soup = BeautifulSoup(html_docs.text, "html.parser")
    film_links = soup.select('ul.list-film li a')
    for film_link in film_links:
        href = film_link.get("href")
        if href:
            href = href.strip()
            if not href.startswith("http"):
                href = base_url + href
            films.add(href)
    return films
def write_to_csv(file_path, film_data, fieldnames):
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Write header only if file does not exist
        if not file_exists:
            writer.writeheader()
        for film in film_data:
            writer.writerow(film)

if __name__ == '__main__':
    urls = "https://tvhayw.org/quoc-gia/phim-my?sort=date&country_name=phim-my&page=5"
    links = extract_url(urls)
    a = list(links)
    c = CustomWebLoader(a)
    film_data = c.load()
    fieldnames = ["Tên phim", "Hình ảnh", "Lượt thích", "Lượng bình luận", "Nội dung phim"]

        # Write data to CSV
    write_to_csv("data/my.csv", film_data, fieldnames)