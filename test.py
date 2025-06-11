from functools import lru_cache

settings = {"mode": "dark", "timeout": 30}  
@lru_cache()
def get_setting(setting_name):
    return settings.get(setting_name, "Not Found")
print(get_setting.cache_info())

print(get_setting("mode"))  
settings = {"mode": "light", "timeout": 60}
print(get_setting("mode"))  
print(get_setting.cache_info())