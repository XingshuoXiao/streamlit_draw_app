import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import xlsxwriter
from io import BytesIO
from draw import draw

flag_emoji_code = {
    "UAE": ":flag-ae: ", "ARG": ":flag-ar: ", "AUS": ":flag-au: ",
    "AUT": ":flag-at: ", "AZE": ":flag-az: ", "BLR": ":flag-by: ",
    "BEL": ":flag-be: ", "BRA": ":flag-br: ", "BGR": ":flag-bg: ",
    "CAN": ":flag-ca: ", "CHN": ":flag-cn: ", "COL": ":flag-co: ",
    "CZE": ":flag-cz: ", "DEN": ":flag-dn: ", "EGY": ":flag-eg: ",
    "EST": ":flag-ee: ", "FIN": ":flag-fi: ", "FRA": ":flag-fr: ",
    "GER": ":flag-de: ", "HKG": ":flag-hk: ", "HUN": ":flag-hu: ",
    "IND": ":flag-in: ", "INA": ":flag-id: ", "IRL": ":flag-ie: ",
    "ISR": ":flag-il: ", "ITA": ":flag-it: ", "JPN": ":flag-jp: ",
    "MAC": ":flag-mo: ", "MAS": ":flag-my: ", "NED": ":flag-nl: ",
    "NZL": ":flag-nz: ", "NOR": ":flag-no: ", "PHI": ":flag-ph: ",
    "POL": ":flag-pl: ", "ROU": ":flag-ro: ", "RUS": ":flag-ru: ",
    "SGP": ":flag-sg: ", "KOR": ":flag-kr: ", "ESP": ":flag-es: ",
    "SRI": ":flag-lk: ", "SUI": ":flag-ch: ", "THA": ":flag-th: ",
    "UKR": ":flag-ua: ", "USA": ":flag-us: ", "VIE": ":flag-vn: ",
    "ENG": ":flag-england: ", "SCO": ":flag-scotland: "
}

def show_flag(code):
    if code in flag_emoji_code:
        return flag_emoji_code[code]
    else:
        return ":triangular_flag_on_post: "


def show_seed(draw, event, qual = False):
    st.markdown("##### " + event + " - Main Draw")
    if event in ["MS", "WS"]:
        for idx, row in draw.main_seed.iterrows():
            name = row.Player[row.Player.find("]")+1:]
            # flag = show_flag(row.Player[1:4])
            flag = row.Player[:row.Player.find("]")+1]
            st.markdown("**" + str(int(idx)) + ".** " + name + " " + flag)
        st.divider()
        if qual:
            st.markdown("##### " + event + " - Qualifying")
            for idx, row in draw.main_seed.iterrows():
                name = row.Player[row.Player.find("]")+1:]
                # flag = show_flag(row.Player[1:4])
                flag = row.Player[:row.Player.find("]")+1]
                st.markdown("**" + str(int(idx)) + ".** " + name + " " + flag)

    else:
        for idx, row in draw.main_seed.iterrows():
            name1 = row.Player1[row.Player1.find("]")+1:]
            name2 = row.Player2[row.Player2.find("]")+1:]
            # flag1 = show_flag(row.Player1[1:4])
            # flag2 = show_flag(row.Player2[1:4])
            flag1 = row.Player1[:row.Player1.find("]")+1]
            flag2 = row.Player2[:row.Player2.find("]")+1]
            st.markdown("**" + str(int(idx)) + ".** &nbsp; " + name1 + " " + flag1)
            st.markdown("&ensp; &ensp; " + name2 + " " + flag2)
        st.markdown("---")
        if qual:
            st.markdown("##### " + event + " - Qualifying")
            for idx, row in draw.main_seed.iterrows():
                name1 = row.Player1[row.Player1.find("]")+1:]
                name2 = row.Player2[row.Player2.find("]")+1:]
                #flag1 = show_flag(row.Player1[1:4])
                #flag2 = show_flag(row.Player2[1:4])
                flag1 = row.Player1[:row.Player1.find("]")+1]
                flag2 = row.Player2[:row.Player2.find("]")+1]
                st.markdown("**" + str(int(idx)) + ".** " + name1 + " " + flag1)
                st.markdown("&nbsp; &nbsp;" + name2 + " " + flag2)


geolocator = Nominatim(user_agent="MyApp")
calendar = st.file_uploader("Upload tournament calendar file",type = "csv")
if calendar is not None:
    calendar_df = pd.read_csv(calendar, encoding = "cp1252", index_col = 'Tournament')
    show_df = st.checkbox("Show calendar")
    if show_df:
        st.dataframe(calendar_df, use_container_width = True)

    st.divider()
    tournament = st.selectbox("Choose the tournament you want to make the draw",
                            options = calendar_df.index)
    st.divider()
    # show information
    tournament_info = calendar_df.loc[tournament, :]
    st.markdown("<h4 style='text-align: center;'>Tournament Information </h4>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["General Info", "Map"])
    with tab1:
        st.markdown(":badminton_racquet_and_shuttlecock: " + tournament + " | " + tournament_info['Category'])
        st.markdown(":round_pushpin: " + tournament_info["City"] + ", " + tournament_info["Country/Region"])
        st.markdown(":date: " + tournament_info["Dates"])
    location = None

    with tab2:
        if tournament_info["City"] != 'TBD':
            location = geolocator.geocode(tournament_info["City"])

        elif tournament_info['Country/Region'] != 'TBD':
            location = geolocator.geocode(tournament_info['Country/Region'])

        else: location = geolocator.geocode('Kuala Lumpur Malaysia')

        st.map(pd.DataFrame({'lat': [location.latitude], 'lon': [location.longitude]}), zoom = 4, size = 100, color = "#E10101", use_container_width = True)

    support_tournaments = ["BWF Super 1000", "BWF Super 750", "BWF Super 500",
                           "BWF Super 300", "Grade 1 individual tournament",
                           "BWF World Tour Finals"]
    st.divider()
    if tournament_info["Category"] in support_tournaments:
        st.markdown(":green[**You can start making a draw of your selected tournament...**]")
        response = st.checkbox("Do you want to start making a draw?")
        if response:
            st.write("start now...")
            entry = st.file_uploader("Upload entry file in excel form", type = "xlsx")
            qual = st.text_input("Enter number of entries from qualification: ")
            if entry is not None and qual != "":
                MS = draw(entry, 'MS', int(qual))
                WS = draw(entry, 'WS', int(qual))
                MD = draw(entry, 'MD', int(qual))
                WD = draw(entry, 'WD', int(qual))
                XD = draw(entry, 'XD', int(qual))

                col1, col2 = st.columns(2)
                with col1:
                    show_seeds = st.radio("Choose the event you want to see the seed entries",
                                      options = ["None", "MS", "WS", "MD", "WD", "XD"])
                with col2:
                    if int(qual) > 0:
                        qual_seeds = st.checkbox("Show qualification seeds?")
                    else: qual_seeds = False

                if show_seeds != "None":
                    if show_seeds == "MS": show_seed(MS, show_seeds, qual_seeds)
                    elif show_seeds == "WD": show_seed(WD, show_seeds, qual_seeds)
                    elif show_seeds == "WS": show_seed(WS, show_seeds, qual_seeds)
                    elif show_seeds == "MD": show_seed(MD, show_seeds, qual_seeds)
                    else: show_seed(XD, show_seeds, qual_seeds)

                st.divider()

                col3, col4 = st.columns(2)
                with col3:
                    show_entries = st.radio("Choose the event you want to see the entry list",
                                        options = ["None", "MS", "WS", "MD", "WD", "XD"])
                with col4:
                    if int(qual) > 0:
                        show_cat = st.radio("Select:", options = ["Main", "Reserve"])
                    else:
                        show_cat = st.radio("Select:", options = ["Main", "Qualification", "Reserve"])

                if show_entries != "None":
                    if show_entries == "MS":
                        if show_cat == "Main": st.dataframe(MS.main, use_container_width = True)
                        elif show_cat == "Qualification": st.dataframe(MS.qual, use_container_width = True)
                        else: st.dataframe(MS.reserve, use_container_width = True)
                    elif show_entries == "WS":
                        if show_cat == "Main": st.dataframe(WS.main, use_container_width = True)
                        elif show_cat == "Qualification": st.dataframe(WS.qual, use_container_width = True)
                        else: st.dataframe(WS.reserve, use_container_width = True)
                    elif show_entries == "MD":
                        if show_cat == "Main": st.dataframe(MD.main, use_container_width = True)
                        elif show_cat == "Qualification": st.dataframe(MD.qual, use_container_width = True)
                        else: st.dataframe(MD.reserve)
                    elif show_entries == "WD":
                        if show_cat == "Main": st.dataframe(WD.main, use_container_width = True)
                        elif show_cat == "Qualification": st.dataframe(WD.qual, use_container_width = True)
                        else: st.dataframe(WD.reserve, use_container_width = True)
                    else:
                        if show_cat == "Main": st.dataframe(XD.main, use_container_width = True)
                        elif show_cat == "Qualification": st.dataframe(XD.qual, use_container_width = True)
                        else: st.dataframe(XD.reserve, use_container_width = True)

                st.divider()

                st.markdown("<h4 style='text-align: center;'>Make draws </h4>", unsafe_allow_html=True)
                first_round_sep = st.checkbox("First round separation?")
                START_DRAW = st.button("Start Draw")
                if START_DRAW:
                    MS.create_draw(first_round_sep)
                    WS.create_draw(first_round_sep)
                    MD.create_draw(first_round_sep)
                    WD.create_draw(first_round_sep)
                    XD.create_draw(first_round_sep)

                    if int(qual) > 0:
                        left, right = st.columns(2)
                        with left:
                            st.markdown("<h4 style='text-align: center;'>MS - Main Draw </h4>", unsafe_allow_html=True)
                            st.table(MS.main_draw)
                            st.markdown("<h4 style='text-align: center;'>WS - Main Draw </h4>", unsafe_allow_html=True)
                            st.table(WS.main_draw)
                            st.markdown("<h4 style='text-align: center;'>MD - Main Draw </h4>", unsafe_allow_html=True)
                            st.table(MD.main_draw)
                            st.markdown("<h4 style='text-align: center;'>WD - Main Draw </h4>", unsafe_allow_html=True)
                            st.table(WD.main_draw)
                            st.markdown("<h4 style='text-align: center;'>XD - Main Draw </h4>", unsafe_allow_html=True)
                            st.table(XD.main_draw)
                        with right:
                            st.markdown("<h4 style='text-align: center;'>MS - Qualification </h4>", unsafe_allow_html=True)
                            st.table(MS.qual_draw)
                            st.markdown("<h4 style='text-align: center;'>WS - Qualification </h4>", unsafe_allow_html=True)
                            st.table(WS.qual_draw)
                            st.markdown("<h4 style='text-align: center;'>MD - Qualification </h4>", unsafe_allow_html=True)
                            st.table(MD.qual_draw)
                            st.markdown("<h4 style='text-align: center;'>WD - Qualification </h4>", unsafe_allow_html=True)
                            st.table(WD.qual_draw)
                            st.markdown("<h4 style='text-align: center;'>XD - Qualification </h4>", unsafe_allow_html=True)
                            st.table(XD.qual_draw)
                    else:
                        st.markdown("<h4 style='text-align: center;'>MS - Main Draw </h4>", unsafe_allow_html=True)
                        st.table(MS.main_draw)
                        st.markdown("<h4 style='text-align: center;'>WS - Main Draw </h4>", unsafe_allow_html=True)
                        st.table(WS.main_draw)
                        st.markdown("<h4 style='text-align: center;'>MD - Main Draw </h4>", unsafe_allow_html=True)
                        st.table(MD.main_draw)
                        st.markdown("<h4 style='text-align: center;'>WD - Main Draw </h4>", unsafe_allow_html=True)
                        st.table(WD.main_draw)
                        st.markdown("<h4 style='text-align: center;'>XD - Main Draw </h4>", unsafe_allow_html=True)
                        st.table(XD.main_draw)

                    output = BytesIO()
                    file_writer = pd.ExcelWriter(output, engine='xlsxwriter')
                    MS.main_draw.to_excel(file_writer, sheet_name = 'MS_main')
                    WS.main_draw.to_excel(file_writer, sheet_name = 'WS_main')
                    MD.main_draw.to_excel(file_writer, sheet_name = 'MD_main')
                    WD.main_draw.to_excel(file_writer, sheet_name = 'WD_main')
                    XD.main_draw.to_excel(file_writer, sheet_name = 'XD_main')
                    if int(qual) > 0:
                        MS.qual_draw.to_excel(file_writer, sheet_name = 'MS_qual')
                        WS.qual_draw.to_excel(file_writer, sheet_name = 'WS_qual')
                        MD.qual_draw.to_excel(file_writer, sheet_name = 'MD_qual')
                        WD.qual_draw.to_excel(file_writer, sheet_name = 'WD_qual')
                        XD.qual_draw.to_excel(file_writer, sheet_name = 'XD_qual')

                    file_writer.close()
                    draw_file = output.getvalue()
                    st.download_button("Download current draw", data = draw_file, file_name = tournament + ".xlsx")
