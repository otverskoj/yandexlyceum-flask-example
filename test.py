from requests import get, post, delete


def test_api_v1():

    news_api_url = 'http://localhost:5000/api/news/'

    print(get(news_api_url).json())

    print(get(news_api_url + '1').json())

    print(get(news_api_url + '999').json())

    print(get(news_api_url + 'q').json())

    print(post(news_api_url, json={}).json())

    print(post(news_api_url, json={'title': 'Заголовок'}).json())

    print(post(news_api_url,
               json={'title': 'Заголовок',
                     'content': 'Текст новости',
                     'user_id': 1,
                     'is_private': False}).json())

    print(delete(news_api_url + '999').json())

    print(delete(news_api_url + '5').json())


def test_api_v2():

    news_api_url = 'http://localhost:5000/api/v2/news'

    print(get(news_api_url).json())

    print(get(news_api_url + '/1').json())

    print(get(news_api_url + '/999').json())

    print(get(news_api_url + '/q').json())

    print(post(news_api_url, json={}).json())

    print(post(news_api_url, json={'title': 'Заголовок'}).json())

    print(post(news_api_url,
               json={'title': 'Заголовок',
                     'content': 'Текст новости',
                     'user_id': 1,
                     'is_private': False}).json())

    print(delete(news_api_url + '/999').json())

    print(delete(news_api_url + '/5').json())


if __name__ == '__main__':
    test_api_v2()
