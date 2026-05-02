from main.translations import get_translation


def i18n_and_locale(request):
    lang = request.session.get('language', 'ru')

    def t(text):
        return get_translation(text, lang)

    return {
        'get_locale': lambda: lang,
        't': t,
    }
