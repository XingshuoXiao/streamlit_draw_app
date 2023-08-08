from random import choice
import numpy as np
import pandas as pd
import math


class draw:
    bye_pos = {4: [2], 8: [2, 7, 4],
            16: [2, 15, 6, 11, 4, 13, 8],
            32: [2, 31, 10, 23, 6, 27, 14,
                19, 4, 29, 12, 21, 8, 25, 16],
            64: [2, 63, 18, 47, 10, 55, 26,
                39, 6, 59, 22, 43, 14, 51, 30,
                35, 4, 61, 20, 45, 12, 53, 28,
                37, 8, 57, 24, 41, 16, 49, 32]
    }


    def __init__(self, entry_file, event, n_quals = 0):
        '''
        Parameters
        ----------
        entry_file: str
            The excel file path for the entry list
        event: str
            Options: ['MS', 'WS', 'MD', 'WD', 'XD']
        '''
        self.file_path = entry_file
        # self.tournament_type = tournament_type
        self.q = n_quals
        assert event in ['MS', 'WS', 'MD', 'WD', 'XD']
        self.event = event
        self.main = pd.read_excel(self.file_path, sheet_name=self.event+'_main', index_col = 0)
        try:
            self.reserve = pd.read_excel(self.file_path, sheet_name=self.event+'_reserve', index_col = 0)
        except:
            self.reserve = pd.DataFrame(data = {}, columns=self.main.columns)

        if event in ['MD', 'WD', 'XD']:
            self.main = self.main.astype({"Member ID1": 'str', "Member ID2": "str"})
            self.main['Code1'] = self.main['Player1'].str.slice(start = 1, stop = 4)
            self.main['Code2'] = self.main['Player2'].str.slice(start = 1, stop = 4)
            self.main['Player1'] = self.main['Player1'].str.slice(start = 6)
            self.main['Player2'] = self.main['Player2'].str.slice(start = 6)

            self.reserve = self.reserve.astype({"Member ID1": 'str', "Member ID2": 'str'})
            self.reserve['Code1'] = self.reserve['Player1'].str.slice(start = 1, stop = 4)
            self.reserve['Code2'] = self.reserve['Player2'].str.slice(start = 1, stop = 4)
            self.reserve['Player1'] = self.reserve['Player1'].str.slice(start = 6)
            self.reserve['Player2'] = self.reserve['Player2'].str.slice(start = 6)

        else:
            self.main = self.main.astype({"Member ID": 'str'})
            self.main['Code'] = self.main['Player'].str.slice(start = 1, stop = 4)
            self.main['Player'] = self.main['Player'].str.slice(start = 6)

            self.reserve = self.reserve.astype({"Member ID": 'str'})
            self.reserve['Code'] = self.reserve['Player'].str.slice(start = 1, stop = 4)
            self.reserve['Player'] = self.reserve['Player'].str.slice(start = 6)

        if self.q != 0:
            self.qual = pd.read_excel(self.file_path, sheet_name=self.event+'_qual', index_col = 0)
            if event in ['MD', 'WD', 'XD']:
                self.qual = self.qual.astype({"Member ID1": 'str', "Member ID2": 'str'})
                self.qual['Code1'] = self.qual['Player1'].str.slice(start = 1, stop = 4)
                self.qual['Code2'] = self.qual['Player2'].str.slice(start = 1, stop = 4)
                self.qual['Player1'] = self.qual['Player1'].str.slice(start = 6)
                self.qual['Player2'] = self.qual['Player2'].str.slice(start = 6)
            else:
                self.qual = self.qual.astype({"Member ID": 'str'})
                self.qual['Code'] = self.main['Player'].str.slice(start = 1, stop = 4)
                self.qual['Player'] = self.qual['Player'].str.slice(start = 6)

        self.seed_list()

    def seed_list(self):
        self.main_seed = self.main[~self.main['Seed'].isna()].sort_values(by = 'Seed')
        self.main_seed.set_index(keys = "Seed", inplace = True)

        if self.q != 0:
            self.qual_seed = self.qual[~self.qual['Seed'].isna()].sort_values(by = 'Seed')
            self.qual_seed.set_index(keys = "Seed", inplace = True)


    def show_seeds(self):
        print(self.event, "Seed List")
        if self.event in ['MS', 'WS']:
            for index, row in self.main_seed.iterrows():
                print('Seed', int(index), '\t', row['Player'])

            if self.q != 0:
                for index, row in self.qual_seed.iterrows():
                    print('Qualification seed', int(index), '\t', row['Player'])

        else:
            for index, row in self.main_seed.iterrows():
                print('Seed', int(index), '\t', row['Player1'], '/', row['Player2'])
            if self.q:
                for index, row in self.qual_seed.iterrows():
                    print('Qualification seed', int(index), '\t', row['Player1'], '/', row['Player2'])


    def get_draw_size(self):
        n_main_entries = self.main.shape[0]
        if self.q != 0:
            n_main_entries += self.q
            self.qual_size = 2**math.ceil(math.log2(self.qual.shape[0]))
            self.qual_byes = self.qual_size - self.qual.shape[0]

        self.main_size = 2**math.ceil(math.log2(n_main_entries))
        self.main_byes = self.main_size - n_main_entries


    def create_draw(self, first_round_sep = False, debug = False):
        self.get_draw_size()

        # draw main
        if self.event in ['MS', 'WS']:
            self.main_draw = pd.DataFrame(data = {'BWF ID':[], 'St.':[], 'Cnty':[], 'Round 1': []})

            current_bye_pos = draw.bye_pos[self.main_size]
            seed_bye = min(self.main_seed.shape[0], self.main_byes)

            for i in range(seed_bye):
                self.main_draw.loc[current_bye_pos[i]] = ['', '', '', 'Bye ' + str(i+1)]


            self.seed_draw_single('main', debug)

            n_byes = max(self.main_byes - self.main_seed.shape[0], 0)
            # draw non-seeded
            self.regular_draw_single('main', n_byes, first_round_sep, debug)
            self.main_draw.sort_index(inplace=True)

        else:
            self.main_draw = pd.DataFrame(data = {'BWF ID':[], 'St.':[], 'Cnty':[], 'Round 1': []})

            current_bye_pos = draw.bye_pos[self.main_size]
            seed_bye = min(self.main_seed.shape[0], self.main_byes)
            if debug: print("Seed_bye", seed_bye)

            for i in range(seed_bye):
                self.main_draw.loc[current_bye_pos[i]*2] = ['', '', '', 'Bye ' + str(i+1)]
                self.main_draw.loc[current_bye_pos[i]*2-1] = ['', '', '', '']

            self.seed_draw_double('main', debug)

            if debug:
                print('Size of draw:', self.main_size)
                print('Number of byes:', self.main_byes)

            n_byes = max(self.main_byes - self.main_seed.shape[0], 0)
            # draw non-seeded
            self.regular_draw_double('main', n_byes, first_round_sep, debug)
            self.main_draw.sort_index(inplace=True)

        if self.q != 0:
            # draw qual
            if self.event in ['MS', 'WS']:
                self.qual_draw = pd.DataFrame(data = {'BWF ID':[], 'St.':[], 'Cnty':[], 'Round 1': []})

                current_bye_pos = draw.bye_pos[self.qual_size]
                seed_bye = min(self.qual_seed.shape[0], self.qual_byes)

                for i in range(seed_bye):
                    self.qual_draw.loc[current_bye_pos[i]] = ['', '', '', 'Bye ' + str(i+1)]


                self.seed_draw_single("qual")
                n_byes = max(self.qual_byes - self.qual_seed.shape[0], 0)
                self.regular_draw_single('qual', n_byes)
                self.qual_draw.sort_index(inplace=True)

            else:
                self.qual_draw = pd.DataFrame(data = {'BWF ID':[], 'St.':[], 'Cnty':[], 'Round 1': []})

                current_bye_pos = draw.bye_pos[self.qual_size]
                seed_bye = min(self.qual_seed.shape[0], self.qual_byes)

                for i in range(seed_bye):
                    self.qual_draw.loc[current_bye_pos[i*2]] = ['', '', '', 'Bye ' + str(i+1)]
                    self.qual_draw.loc[current_bye_pos[i*2]-1] = ['', '', '', '']

                self.seed_draw_double("qual")
                n_byes = max(self.qual_byes - self.qual_seed.shape[0], 0)
                self.regular_draw_double("qual", n_byes)
                self.qual_draw.sort_index(inplace=True)


    def seed_draw_single(self, option = 'main', debug = False):
        if option == 'main':
            n_seeds = self.main_seed.shape[0]
            size = self.main_size
        else:
            n_seeds = self.qual_seed.shape[0]
            size = self.qual_size

        n_rounds = math.ceil(math.log2(n_seeds))
        last_seed = 0

        for i in range(n_rounds):
            current_seeds = list(range(last_seed+1, 2**(i+1)+1))
            last_seed = 2**(i+1)

            if debug:
                print('Round '+str(i))
                print(current_seeds)

            if i == 0:
                if option == 'main':
                    self.main_draw.loc[1] = [self.main_seed.at[1, 'Member ID'], '',
                                            self.main_seed.at[1, 'Code'], self.main_seed.at[1, 'Player']]
                    self.main_draw.loc[size] = [self.main_seed.at[2, 'Member ID'], '',
                                            self.main_seed.at[2, 'Code'], self.main_seed.at[2, 'Player']]

                    self.main_draw.at[1, 'Round 1'] += ' [1]'
                    self.main_draw.at[size, 'Round 1'] += ' [2]'

                    if debug:
                        print(self.main_draw.loc[1,:], self.main_draw.loc[size,:])
                else:
                    self.qual_draw.loc[1] = [self.qual_seed.at[1, 'Member ID'], '',
                                            self.qual_seed.at[1, 'Code'], self.qual_seed.at[1, 'Player']]
                    self.qual_draw.loc[size] = [self.qual_seed.at[2, 'Member ID'], '',
                                            self.qual_seed.at[2, 'Code'], self.qual_seed.at[2, 'Player']]
                    self.qual_draw.at[1, 'Round 1'] += ' [1]'
                    self.qual_draw.at[size, 'Round 1'] += ' [2]'

                    if debug:
                        print(self.qual_draw.loc[1,:], self.qual_draw.loc[size,:])

            else:
                box_size = size//(2**(i+1))
                pos_upper = [box_size*(2*j+1)+1 for j in range(len(current_seeds)//2)]
                pos_lower = [size - box_size*(2*j+1) for j in range(len(current_seeds)//2)]
                pos = pos_upper + pos_lower

                if debug: print(pos)

                count = 0

                while len(current_seeds) > 0:
                    pick = choice(current_seeds)
                    current_seeds.remove(pick)

                    if debug:
                        print('Current pick:', self.main_seed.at[pick, 'Player'], ' [', pick, ']')
                        print('Not drawn yet:', current_seeds)

                    if option == 'main':
                        self.main_draw.loc[pos[count]] = [self.main_seed.at[pick, 'Member ID'], '',
                                            self.main_seed.at[pick, 'Code'], self.main_seed.at[pick, 'Player']]
                        self.main_draw.at[pos[count], 'Round 1'] += ' [' + str(pick) + ']'

                    else:
                        self.qual_draw.loc[pos[count]] = [self.qual_seed.at[pick, 'Member ID'], '',
                                            self.qual_seed.at[pick, 'Code'], self.qual_seed.at[pick, 'Player']]
                        self.qual_draw.at[pos[count], 'Round 1'] += ' [' + str(pick) + ']'

                    count += 1

    def regular_draw_single(self, option = 'main', n_byes = 0, first_round_sep = False, debug = False):
        if option == 'main':
            remaining_spots = set(range(1, self.main_size + 1)).difference(set(self.main_draw.index.tolist()))

            # place byes if there are extra byes
            bye_count = self.main_seed.shape[0] + 1 if n_byes > 0 else 0
            while n_byes > 0:
                bye_spot = choice(remaining_spots)
                remaining_spots.remove(bye_spot)
                self.main_draw.loc[bye_spot] = ['', '', '','Bye ' + str(bye_count)]
                bye_count += 1
                n_byes -= 1

            # draw non-seeded
            non_seeded = self.main[self.main['Seed'].isna()].index.tolist()

            if self.q != 0:
                non_seeded += ['Q' + str(i) for i in range(1, self.q + 1)]

            for spot in remaining_spots:
                pick = choice(non_seeded)
                if debug:
                    print('Spot ', spot)
                    print('Current pick: ', self.main.at[pick, 'Player'])

                if first_round_sep:
                    try:
                        team_pick = self.main.at[pick, 'Code']
                    except:
                        team_pick = ''

                    try:
                        if spot % 2 == 1:
                            team_pot_opp = self.main_draw.at[spot+1, 'Cnty']
                        else: team_pot_opp = self.main_draw.at[spot-1, 'Cnty']
                    except:
                        team_pot_opp = 'Empty'
                    if debug: print('Potential opponent pick: ', team_pot_opp)

                    while team_pick == team_pot_opp:
                        if debug: print('Current pick representing: ', team_pick)
                        pick = choice(non_seeded)
                        if debug: print('New pick: ', self.main.at[pick, 'Player'])
                        try:
                            team_pick = self.main.loc[pick, 'Code']
                        except:
                            team_pick = ''

                non_seeded.remove(pick)
                try:
                    self.main_draw.loc[spot] = [self.main.at[pick, 'Member ID'], '',
                                                self.main.at[pick, 'Code'], self.main.at[pick, 'Player']]
                except:
                    self.main_draw.loc[spot] = ['','','', pick]
                if pick == 'Wild Card':
                    self.main_draw.at[spot, 'St.'] = 'WC'

        else:
            remaining_spots = set(range(1, self.qual_size + 1)).difference(set(self.qual_draw.index.tolist()))
            bye_count = self.qual_seed.shape[0] + 1 if n_byes > 0 else 0

            while n_byes > 0:
                bye_spot = choice(list(remaining_spots))
                remaining_spots.remove(bye_spot)
                self.qual_draw.loc[bye_spot] = ['','','','Bye' + str(bye_count)]
                bye_count += 1
                n_byes -= 1

            non_seeded = self.qual[self.qual['Seed'].isna()].index.tolist()

            for spot in remaining_spots:
                pick = choice(non_seeded)
                non_seeded.remove(pick)
                self.qual_draw.loc[spot] = [self.qual.at[pick, 'Member ID'], '',
                                            self.qual.at[pick, 'Code'], self.qual.at[pick, 'Player']]
                if pick == 'Wild Card':
                    self.qual_draw.at[spot, 'St.'] = 'WC'


    def seed_draw_double(self, option = 'main', debug = False):
        if option == 'main':
            n_seeds = self.main_seed.shape[0]
            size = self.main_size
            byes = self.main_byes
        else:
            n_seeds = self.qual_seed.shape[0]
            size = self.qual_size
            byes = self.qual_byes

        n_rounds = math.ceil(math.log2(n_seeds))
        last_seed = 0

        if debug:
            print('Draw seeds... number of byes = ', byes)

        for i in range(n_rounds):
            current_seeds = list(range(last_seed+1, 2**(i+1)+1))
            last_seed = 2**(i+1)

            if debug:
                print('Round '+str(i))
                print(current_seeds)

            if i == 0:
                if option == 'main':
                    self.main_draw.loc[1] = [self.main_seed.at[1, 'Member ID1'], '',
                                            self.main_seed.at[1, 'Code1'], self.main_seed.at[1, 'Player1']]

                    self.main_draw.at[1, 'Round 1'] += ' [1]'
                    self.main_draw.loc[2] = [self.main_seed.at[1, 'Member ID2'], '',
                                            self.main_seed.at[1, 'Code2'], self.main_seed.at[1, 'Player2']]

                    self.main_draw.loc[size*2-1] = [self.main_seed.at[2, 'Member ID1'], '',
                                            self.main_seed.at[2, 'Code1'], self.main_seed.at[2, 'Player1']]
                    self.main_draw.at[size*2-1, 'Round 1'] += ' [2]'
                    self.main_draw.loc[size*2] = [self.main_seed.at[2, 'Member ID2'], '',
                                            self.main_seed.at[2, 'Code2'], self.main_seed.at[2, 'Player2']]
                    if debug:
                        print(self.main_draw.loc[1,'Round 1'], self.main_draw.loc[2,'Round 1'])
                        print(self.main_draw.loc[size*2-1,'Round 1'], self.main_draw.loc[size*2,'Round 1'])
                else:
                    self.qual_draw.loc[1] = [self.qual_seed.at[1, 'Member ID1'], '',
                                            self.qual_seed.at[1, 'Code1'], self.qual_seed.at[1, 'Player1']]

                    self.qual_draw.at[1, 'Round 1'] += ' [1]'
                    self.qual_draw.loc[2] = [self.qual_seed.at[1, 'Member ID2'], '',
                                            self.qual_seed.at[1, 'Code2'], self.qual_seed.at[1, 'Player2']]
                    self.qual_draw.loc[size*2-1] = [self.qual_seed.at[2, 'Member ID1'], '',
                                            self.qual_seed.at[2, 'Code1'], self.qual_seed.at[2, 'Player1']]
                    self.qual_draw.at[size*2-1, 'Round 1'] += ' [2]'
                    self.qual_draw.loc[size*2] = [self.qual_seed.at[2, 'Member ID2'], '',
                                            self.qual_seed.at[2, 'Code2'], self.qual_seed.at[2, 'Player2']]
                    if debug:
                        print(self.qual_draw.loc[1,'Round 1'], self.qual_draw.loc[2,'Round 1'])
                        print(self.qual_draw.loc[size*2-1,'Round 1'], self.qual_draw.loc[size*2,'Round 1'])
            else:
                box_size = size//(2**(i+1))
                pos_upper = [box_size*(2*j+1)+1 for j in range(len(current_seeds)//2)]
                pos_lower = [size - box_size*(2*j+1) for j in range(len(current_seeds)//2)]
                pos = pos_upper + pos_lower

                count = 0

                while len(current_seeds) > 0:
                    pick = choice(current_seeds)
                    current_seeds.remove(pick)

                    if debug:
                        print('Current pick:', self.main_seed.at[pick, 'Player1'], '/',
                                self.main_seed.at[pick, 'Player2'], '['+str(pick)+']')
                        print('Not drawn yet:', current_seeds)

                    if option == 'main':
                        self.main_draw.loc[pos[count]*2 - 1] = [self.main_seed.at[pick, 'Member ID1'], '',
                                                                self.main_seed.at[pick, 'Code1'], self.main_seed.at[pick, 'Player1']]
                        self.main_draw.at[pos[count]*2 - 1, 'Round 1'] += ' [' + str(pick) + ']'
                        self.main_draw.loc[pos[count]*2] = [self.main_seed.at[pick, 'Member ID2'], '',
                                                                self.main_seed.at[pick, 'Code2'], self.main_seed.at[pick, 'Player2']]
                    else:
                        self.qual_draw.loc[pos[count]*2 - 1] = [self.qual_seed.at[pick, 'Member ID1'], '',
                                                                self.qual_seed.at[pick, 'Code1'], self.qual_seed.at[pick, 'Player1']]
                        self.qual_draw.at[pos[count]*2 - 1, 'Round 1'] += ' [' + str(pick) + ']'
                        self.qual_draw.loc[pos[count]*2] = [self.qual_seed.at[pick, 'Member ID2'], '',
                                                                self.qual_seed.at[pick, 'Code2'], self.qual_seed.at[pick, 'Player2']]

                    count += 1

    def regular_draw_double(self, option = 'main', n_byes = 0, first_round_sep = False, debug = False):
        if option == 'main':
            # byes
            # remaining_spots = [k for k,v in self.main_draw.items() if v == '' and k%2 == 1]
            occupied_spots = {i//2 for i in self.main_draw.index.tolist() if i % 2 == 0}
            remaining_spots = set(range(1, self.main_size + 1)).difference(occupied_spots)

            if debug:
                print(occupied_spots)
                print(remaining_spots)

            bye_count = self.main_seed.shape[0] + 1 if n_byes > 0 else 0

            while n_byes > 0:
                bye_spot = choice(list(remaining_spots))
                remaining_spots.remove(bye_spot)
                self.main_draw.loc[bye_spot*2 - 1] = ['', '', '', '']
                self.main_draw.loc[bye_spot*2] = ['', '', '', 'Bye ' + str(bye_count)]
                bye_count += 1
                n_byes -= 1

            non_seeded = self.main[self.main['Seed'].isna()].index.tolist()

            if self.q != 0:
                non_seeded += ['Q' + str(i) for i in range(1, self.q + 1)]

            for spot in remaining_spots:
                pick = choice(non_seeded)

                if debug:
                    print('Spot:', spot)
                    try:
                        print('Current pick:', self.main.loc[pick, ['Player1', 'Player2']])
                    except:
                        print('Current pick:', pick)

                if first_round_sep:
                    try:
                        team_pick = {self.main.loc[pick, 'Code1'], self.main.loc[pick, 'Code2']}
                    except:
                        team_pick = set()

                    try:
                        if spot % 2 == 1:
                            team_pot_opp = {self.main_draw.at[(spot+1)*2, 'Cnty'],
                                    self.main_draw.at[(spot+1)*2-1, 'Cnty']}
                        else:
                            team_pot_opp = {self.main_draw.at[(spot-1)*2, 'Cnty'],
                                    self.main_draw.at[(spot-1)*2-1, 'Cnty']}
                    except:
                        team_pot_opp = set()

                    if debug:
                        print('Current pick representing:', team_pick)
                        print('Potential opponents representing:', team_pot_opp)

                    while len(team_pick.intersection(team_pot_opp)) > 0:
                        pick = choice(non_seeded)
                        try:
                            team_pick = {self.main.loc[pick, 'Code1'], self.main.loc[pick, 'Code2']}
                        except:
                            team_pick = set()
                        if debug: print('New pick:', self.main.loc[pick, ['Player1', 'Player2']],
                                        'representing', team_pick)


                non_seeded.remove(pick)
                try:
                    self.main_draw.loc[spot*2-1] = [self.main.at[pick, 'Member ID1'], '',
                                                self.main.at[pick, 'Code1'], self.main.at[pick, 'Player1']]
                    self.main_draw.loc[spot*2] = [self.main.at[pick, 'Member ID2'], '',
                                                self.main.at[pick, 'Code2'], self.main.at[pick, 'Player2']]
                except:
                    self.main_draw.loc[spot*2-1] = ["", "", "", ""]
                    self.main_draw.loc[spot*2] = ['', '', '', pick]

                if pick == 'Wild Card':
                    self.main_draw.at[spot*2-1, 'St.'] = 'WC'
                    self.main_draw.at[spot*2, 'St.'] = 'WC'


        else:
            occupied_spots = {i//2 for i in self.qual_draw.index.tolist()}
            remaining_spots = list(set(range(1, self.qual_size + 1)).difference(occupied_spots))

            bye_count = self.qual_seed.shape[0] + 1 if n_byes > 0 else 0

            while n_byes > 0:
                bye_spot = choice(list(remaining_spots))
                remaining_spots.remove(bye_spot)
                self.qual_draw.loc[bye_spot*2 - 1] = ['', '', '', '']
                self.qual_draw.loc[bye_spot*2] = ['', '', '', 'Bye ' + str(bye_count)]
                bye_count += 1
                n_byes -= 1

            non_seeded = self.qual[self.qual['Seed'].isna()].index.tolist()

            for spot in remaining_spots:
                pick = choice(non_seeded)
                non_seeded.remove(pick)
                self.qual_draw.loc[spot*2-1] = [self.qual.at[pick, 'Member ID1'], '',
                                                self.qual.at[pick, 'Code1'], self.qual.at[pick, 'Player1']]
                self.qual_draw.loc[spot*2] = [self.qual.at[pick, 'Member ID2'], '',
                                                self.qual.at[pick, 'Code2'], self.qual.at[pick, 'Player2']]

                if pick == 'Wild Card':
                    self.qual_draw.at[spot*2-1, 'St.'] = 'WC'
                    self.qual_draw.at[spot*2, 'St.'] = 'WC'

    def save_to_excel(self):
        main = pd.Series(self.main_draw)
        writer = pd.ExcelWriter(self.event + '.xlsx')
        main.to_excel(writer,'Main')
        if self.q != 0:
            qual = pd.Series(self.qual_draw)
            qual.to_excel(writer, 'Qualification')
        writer.save()