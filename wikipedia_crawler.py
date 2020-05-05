from requests import get
from bs4 import BeautifulSoup, element
import regex
import json
import os
import urllib.request

# url = 'https://de.wikipedia.org/wiki/42_(Antwort)'
default_url = 'https://en.wikipedia.org/wiki/Phrases_from_The_Hitchhiker%27s_Guide_to_the_Galaxy#Answer_to_the_Ultimate_Question_of_Life,_the_Universe,_and_Everything_(42)'
url = str(input('Wikipedia URL to scrape: ') or default_url)
response = get(url)
html_soup = BeautifulSoup(response.text, 'html.parser')
print('Getting title...')
heading = html_soup.find('h1', class_='firstHeading')
content = html_soup.find('div', class_='mw-content-ltr')

print('Scraping text...')
p = content.findAll(['p', 'dl'])
text = ''
for item in p:
    # print(type(item), item.name, item.get('class'), item.get('id'))
    # print(item.text)
    if item.name == 'dl':
        maths = item.findAll('math')
        for math in maths:
            text += math.get('alttext')[15:-1] + '\n'
    else:
        math_elements = item.findAll(class_='mwe-math-element')
        if math_elements:
            matches = regex.findall(' \\n\\n[−\\/\\(\\)\\|\\=\\+\\-A-Z0-9a-z\s\\p{Greek}]+{\\\displaystyle .+}', item.text)
            temp2 = ''
            from_counter = 0
            for match in matches:
                temp = item.text[from_counter:item.text.find(match)]
                temp += ' ' + regex.search('{\\\displaystyle .+}', match)[0][15:-1]
                from_counter = (item.text.find(match) + len(match) + 2)
                temp2 += temp
            temp2 += item.text[from_counter:]
            text += temp2
        else:
            text += item.text

print('Downloading images...')
images = html_soup.findAll('img', {'src':regex.compile('[.jpg|.png]')})
image_url_list = []
for image in images:
    if image.get('src').startswith('/static'):
        images.remove(image)
    elif 'https:' not in image.get('src'):
        image_url_list.append('https:' + image.get('src'))
    else:
        image_url_list.append(image.get('src'))
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/' + heading.text):
    os.makedirs('data/' + heading.text)
image_paths = []
for image_url in image_url_list:
    image_path = 'data/' + heading.text + '/' + str(image_url[image_url.rfind('/') + 1:])
    urllib.request.urlretrieve(image_url, image_path)
    image_paths.append(image_path)
print('Getting URL\'s...')
url_list = []
base_url = url[:url.find('/wiki')]
for link in html_soup.findAll('a'):
    temp_url = link.get('href', '')
    if temp_url.startswith('/wiki/'):
        url_list.append(base_url + temp_url)

output = {
    'heading': heading.text,
    'text': text,
    'image_paths': image_paths,
    'urls': url_list
}
print('Writing output file: data/' + heading.text + '.json')
with open('data/' + heading.text + '.json', 'w') as outf:
    json.dump(output, outf)
