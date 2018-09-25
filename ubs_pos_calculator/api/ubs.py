#!/usr/bin/env python
import sys
import json
from pathlib import Path
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


class PosCalculator:
    def __init__(self, source, target):
        self.source = Path(source)
        self.target = Path(target)
        if not self.source.exists():
            print("{} directory doesn't exist".format(source))
            sys.exit(1)
        elif not self.target.exists():
            print("{} directory doesn't exist, creating...".format(target), end='')
            self._create_target_directory(self.target)

        # Note: Hardcoding the filenames assuming that in reality the filename would contain timestamp/date
        # in future we can modify this program to pick the file based on given date parameter
        self.position_file = self.source.joinpath('Input_StartOfDay_Positions.txt')
        self.transactions_file = self.source.joinpath('Input_Transactions.txt')

    @staticmethod
    def _create_target_directory(target_dir):
        """
        Create output directory if it doesn't exist
        :param target_dir: path to directory
        :return: None
        """
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            print("done!")
        except Exception as e:
            print("Unable to create directory: Error: {}".format(e))
            sys.exit(1)

    def _transaction_reader(self):
        """
        Read transaction file, convert it to JSON object
        :return: JSON object of transaction file
        """
        return json.loads(self.transactions_file.read_text())

    def _position_reader(self):
        """
        Read positions file
        :return: dataframe
        """
        pos_df = pd.read_csv(self.position_file.resolve(), sep=',', encoding='utf-8')
        return pos_df

    def calculate(self):
        """
        Main method to calculate the positions
        :return: A file which contains calculated values and differences
        """
        positions_data = self._position_reader()
        transaction_data = self._transaction_reader()
        updated_data = positions_data.copy(deep=True)

        for transaction in transaction_data:
            subset = updated_data[updated_data['Instrument'] == transaction['Instrument']]
            for i, s in subset.iterrows():
                if transaction['TransactionType'] == 'B' and s['AccountType'] == 'E':
                    updated_data['Quantity'].loc[s.name] = s['Quantity'] + transaction['TransactionQuantity']
                elif transaction['TransactionType'] == 'B' and s['AccountType'] == 'I':
                    updated_data['Quantity'].loc[s.name] = s['Quantity'] - transaction['TransactionQuantity']
                elif transaction['TransactionType'] == 'S' and s['AccountType'] == 'E':
                    updated_data['Quantity'].loc[s.name] = s['Quantity'] - transaction['TransactionQuantity']
                elif transaction['TransactionType'] == 'S' and s['AccountType'] == 'I':
                    updated_data['Quantity'].loc[s.name] = s['Quantity'] + transaction['TransactionQuantity']

        updated_data['Delta'] = updated_data['Quantity'] - positions_data['Quantity']
        self.save_output(updated_data)
        self.find_max_min_vod(updated_data)

    def find_max_min_vod(self, data):
        """
        Find instruments with largest and lowest net transaction volumes for the day
        :param data:
        :return:
        """
        print("Largest net transaction is for instrument: {}".format(data['Instrument'].loc[data['Delta'].argmax()]))
        print("Lowest net transactions is for instrument: {}".format(data['Instrument'].loc[data['Delta'].argmin()]))

    def save_output(self, data):
        data.to_csv(self.target.joinpath('EndOfDay_Positions.csv'), sep=',', encoding='utf-8', index=None)
        print(data)
        print("Output saved in {}".format(self.target.resolve()))
