from ragendja.settings_post import settings
settings.add_app_media('combined-%(LANGUAGE_CODE)s.js',
    'upload/pikachoose.js',
)
settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'upload/bottom.css',
)
#settings.add_app_media('1.gif',
#    'upload/1.gif',
#)
#settings.add_app_media('2.gif',
#    'upload/2.gif',
#)
#settings.add_app_media('3.gif',
#    'upload/3.gif',
#)
#settings.add_app_media('combined-print-%(LANGUAGE_DIR)s.css',
#    'blueprintcss/print.css',
#)
#settings.add_app_media('ie.css',
#    'blueprintcss/ie.css',
#)
