import translators

async def translate(text, to_language, translator):
    result = translators.translate_text(text,translator,"auto",to_language)
    return result
        

"""
translate_text(query_text: str, translator: str = 'bing', from_language: str = 'auto', to_language: str = 'en', **kwargs) -> Union[str, dict]
    :param query_text: str, must.
    :param translator: str, default 'bing'.
    :param from_language: str, default 'auto'.
    :param to_language: str, default 'en'.
    :param if_use_preacceleration: bool, default False.
    :param **kwargs:
            :param is_detail_result: bool, default False.
            :param professional_field: str, default None. Support alibaba(), baidu(), caiyun(), cloudTranslation(), elia(), sysTran(), youdao(), volcEngine() only.
            :param timeout: float, default None.
            :param proxies: dict, default None.
            :param sleep_seconds: float, default 0.
            :param update_session_after_freq: int, default 1000.
            :param update_session_after_seconds: float, default 1500.
            :param if_use_cn_host: bool, default False. Support google(), bing() only.                
            :param reset_host_url: str, default None. Support google(), yandex() only.
            :param if_check_reset_host_url: bool, default True. Support google(), yandex() only.
            :param if_ignore_empty_query: bool, default False.
            :param limit_of_length: int, default 20000.
            :param if_ignore_limit_of_length: bool, default False.
            :param if_show_time_stat: bool, default False.
            :param show_time_stat_precision: int, default 2.
            :param if_print_warning: bool, default True.
            :param lingvanex_mode: str, default 'B2C', choose from ("B2C", "B2B").
            :param myMemory_mode: str, default "web", choose from ("web", "api").
    :return: str or dict
"""