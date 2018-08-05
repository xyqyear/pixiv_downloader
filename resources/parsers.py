# -*- coding:utf-8 -*-

def parse_token_response(token_json):
    """
    从auth方法返回值中解析出token
    :param token_json: 
    :return: 
    """
    return {'access_token':token_json['response']['access_token'],
            'refresh_token':token_json['response']['refresh_token']}

def parse_image_url(response_json):
    """
    解析返回的画师数据和收藏夹数据
    :param response_json: 
    :return: list:[[url0],[url0,url1]...]
    """
    out_list = list()
    illusts = response_json['illusts']
    for i in illusts:
        urls = list()
        if i['meta_single_page']:
            url = i['meta_single_page']['original_image_url']
            urls.append(url)

        elif i['meta_pages']:
            for page in i['meta_pages']:
                url = page['image_urls']['original']
                urls.append(url)

        else:
            continue

        out_list.append(urls)
    return out_list