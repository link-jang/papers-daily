import requests, re
from bs4 import BeautifulSoup
import bs4

paper_line_reg = re.compile("(^/papers/[0-9]+.[0-9]+$)")
huggingface_detail_prefix = "https://huggingface.co"
arxiv_prefix = "https://arxiv.org/pdf/"


class Comment:
    def __init__(self, id = None):
        self.id = id
        self.comment = []
        self.up = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Paper:
    def __init__(self, id, name, feature_data, comments):
        self.id = id
        self.arxiv = arxiv_prefix + id
        self.huggingface_url = None
        self.name = name
        self.publish_date = None
        self.vote_num = None
        self.feature_data = feature_data
        self.comments = comments

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def get_paper_list():
    url = "https://huggingface.co/papers"

    papers = {}

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all("a"):
            href = link.get('href')
            # if not link.get('href') or re.match(paper_line_reg, href) or "cursor-pointer" not in link["class"]:
            #     continue
            if href and re.match(paper_line_reg, href) and "cursor-pointer" in link["class"]:
                if link.text.strip():
                    papers[href] = link.text
    else:
        print("error response")

    return papers


def get_paper_detail(paper_id):
    url = "https://huggingface.co/papers/" + paper_id.split("/")[-1]

    feature_date = None
    comments = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # find_all(name, attrs, recursive, text, **kwargs)
        for link in soup.find_all("span"):
            if not link.a:
                continue
            href = link.a.get('href')
            if href and "/papers?date=" in href:
                feature_date = href.split("=")[-1]
                print(href)

        for link in soup.find_all("div", "py-3"):
            if not (link.div and link.div["id"]):
                continue
            id = link.div["id"]
            comment = Comment(id)

            for id_soup in link.div.children:
                if not id_soup \
                        or isinstance(id_soup, str) \
                        or "break-words" not in id_soup["class"] \
                        or not id_soup.div:
                    continue
                for id_child in id_soup.children:
                    if not id_child or not isinstance(id_child, bs4.element.Tag):
                        continue

                    if "prose" in id_child["class"]:
                        for content in id_child.children:
                            if not isinstance(content, bs4.element.Tag):
                                continue
                            comment.comment.append(content.text)
                    else:

                        for up in id_child.descendants:
                            if up and isinstance(up, bs4.element.Tag):
                                for a in up.find_all("div", attrs={"class": "absolute right-2"}):
                                    comment.up = a.text.strip()

            comments.append(comment)

    else:
        print("error response")

    paper = Paper(id=paper_id.split("/")[-1], name="", feature_data=feature_date, comments=comments)

    return paper


papers_ids = get_paper_list()

import json
papers = []
print(papers_ids)
for id, name in papers_ids.items():
    paper = get_paper_detail(id)
    paper.name = name
    papers.append(paper)

    print(paper.toJSON())
#
# print(paper.id)
# print(paper.feature_data)
# for comment in paper.comments:
#     print(comment.id, comment.up, comment.comment)



