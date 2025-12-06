def get_dynamic_holidays():
    year = datetime.now().year

    return [

        # Christian – Orthodox (main flag: Georgia 🇬🇪)
        {
            "date": orthodox_easter(year).strftime("%m-%d"),
            "name": "Orthodox Easter",
            "countries": ["georgia"]
        },
        {
            "date": orthodox_pentecost(year).strftime("%m-%d"),
            "name": "Orthodox Pentecost",
            "countries": ["georgia"]
        },
        {
            "date": "01-07",
            "name": "Orthodox Christmas",
            "countries": ["georgia"]
        },

        # Christian – Catholic (main flag: Italy 🇮🇹)
        {
            "date": catholic_easter(year).strftime("%m-%d"),
            "name": "Catholic Easter",
            "countries": ["italy"]
        },
        {
            "date": catholic_pentecost(year).strftime("%m-%d"),
            "name": "Catholic Pentecost",
            "countries": ["italy"]
        },
        {
            "date": "12-25",
            "name": "Catholic Christmas",
            "countries": ["italy"]
        },

        # Islamic (main flag: Turkey 🇹🇷)
        {
            "date": ramadan_start(year).strftime("%m-%d"),
            "name": "Ramadan Start",
            "countries": ["turkey"]
        },
        {
            "date": eid_al_fitr(year).strftime("%m-%d"),
            "name": "Eid al-Fitr",
            "countries": ["turkey"]
        },
        {
            "date": eid_al_adha(year).strftime("%m-%d"),
            "name": "Eid al-Adha",
            "countries": ["turkey"]
        },

        # Jewish (main flag: Israel 🇮🇱)
        {
            "date": rosh_hashanah(year).strftime("%m-%d"),
            "name": "Rosh Hashanah",
            "countries": ["israel"]
        },
        {
            "date": yom_kippur(year).strftime("%m-%d"),
            "name": "Yom Kippur",
            "countries": ["israel"]
        },
        {
            "date": hanukkah_start(year).strftime("%m-%d"),
            "name": "Hanukkah Start",
            "countries": ["israel"]
        },

        # Chinese New Year 🇨🇳
        {
            "date": chinese_new_year(year).strftime("%m-%d"),
            "name": "Chinese New Year",
            "countries": ["china"]
        },

        # Diwali 🇮🇳
        {
            "date": diwali(year).strftime("%m-%d"),
            "name": "Diwali",
            "countries": ["india"]
        }
    ]
