# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


class EnLocalizationStrings(object):
    ERROR_LOAD_FILE_TITLE = "Error from load file"
    ERROR_SAVE_FILE_TITLE = "Error from save file"
    ERROR_PARSE_POINTS_TITLE = "Error in initial points"
    ERROR_PARSE_THETA_TITLE = "Error in theta list"
    ERROR_PARSE_DIFF_SYS_TITLE = "Error in diff system"
    ERROR_PARSE_IMP_OPER_TITLE = "Error in impulse operator"
    ERROR_THETA_MUST_ABOVE_ZERO = "Theta must be above 0: %s = %s"
    ERROR_IN_CALCULATIONS = "Error in calculations"
    
    
class RuLocalizationStrings(EnLocalizationStrings):
    ERROR_LOAD_FILE_TITLE = "Ошибка при чтении файла"
    ERROR_SAVE_FILE_TITLE = "Ошибка при записи файла"
    ERROR_PARSE_POINTS_TITLE = "Ошибка в начальных точках"
    ERROR_PARSE_THETA_TITLE = "Ошибка в списке промежутков"
    ERROR_PARSE_DIFF_SYS_TITLE = "Ошибка в дифф системе"
    ERROR_PARSE_IMP_OPER_TITLE = "Ошибка в импульсном операторе"
    ERROR_THETA_MUST_ABOVE_ZERO = "Промежуток должен быть больше 0: %s = %s"
    ERROR_IN_CALCULATIONS = "Ошибка при вычислениях"


class LangManagerDelegate(object):
    def on_language_chaged(self):
        pass


class LangManagerSingleton(object):
    RU = 'ru'
    EN = 'en'
    
    __instance = None
    def __init__(self, isfirstinit=False):
        if not isfirstinit:
            raise Exception("This is singleton")
        self.__lang = None
        self.__localization = None
        self.__delegates = []
        self.setlanguage(self.RU)
        
    @staticmethod
    def getinstance():
        if not LangManagerSingleton.__instance:
            LangManagerSingleton.__instance = LangManagerSingleton(True)
        return LangManagerSingleton.__instance
    
    def setlanguage(self, lang):
        if lang == LangManagerSingleton.RU:
            self.__setlang(lang, RuLocalizationStrings)
        elif lang == LangManagerSingleton.EN:
            self.__setlang(lang, EnLocalizationStrings)
        else:
            raise Exception("Language not found")
    
    def __setlang(self, lang, langclass):
        self.__lang = lang
        self.__localization = langclass()
    
    def language(self):
        return self.__lang
    
    def __get_localization(self):
        return self.__localization
    
    @staticmethod
    def localization():
        return LangManagerSingleton.getinstance().__get_localization()
    
    def add_delegate(self, delegate):
        if not delegate in self.__delegates:
            self.__delegates.append(delegate)
    
    def remove_delegate(self, delegate):
        if delegate in self.__delegates:
            self.__delegates.remove(delegate)
    
    def __lang_changed(self):
        for delegate in self.__delegates:
            try:
                delegate.on_language_chaged()
            except Exception as ex:
                print(ex)

