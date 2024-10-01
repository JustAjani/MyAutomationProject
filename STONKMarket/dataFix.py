import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging

class StockDataAnalyzer:
    def __init__(self, csvRoute, graphRoute):
        self.csvRoute = csvRoute
        self.graphRoute = graphRoute
        self.Stockdata = pd.read_csv(self.csvRoute)

    def checkNaNorNull(self):
        if self.Stockdata.isna().values.any():
            logging.warning(f"Data contains NaN or null values: {self.Stockdata.isna().sum()}")
            self.Stockdata.dropna(inplace=True)
        else:
            logging.info("Data contains no NaN or null values")

    def fixData(self):
        self.Stockdata['Timestamp'] = pd.to_datetime(self.Stockdata['Timestamp'], errors='coerce')
        self.Stockdata['Stock Price'] = pd.to_numeric(self.Stockdata['Stock Price'], errors='coerce')
        self.Stockdata['Price Change'] = pd.to_numeric(self.Stockdata['Price Change'], errors='coerce')
        self.Stockdata['Percentage Change'] = self.Stockdata['Percentage Change'].str.replace('(', '', regex=False).str.replace(')', '', regex=False).str.replace('%', '', regex=False).astype(float)

    def plotData(self):
        fig, ax1 = plt.subplots(figsize=(15, 8))

        ax1.plot(self.Stockdata['Timestamp'], self.Stockdata['Stock Price'], label='Stock Price', color='blue')
        ax1.set_xlabel('Date/Time')
        ax1.set_ylabel('Stock Price ($)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(self.Stockdata['Timestamp'], self.Stockdata['Price Change'], label='Price Change', color='red')
        ax2.set_ylabel('Price Change ($)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.plot(self.Stockdata['Timestamp'], self.Stockdata['Percentage Change'], label='Percentage Change', color='green')
        ax3.set_ylabel('Percentage Change (%)', color='green')
        ax3.tick_params(axis='y', labelcolor='green')

        ax1.set_title('NVDA Stock Price Over Time')
        ax1.grid(True)
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left')

        plt.savefig(self.graphRoute + '\\NVDAStockGraph.png')
        plt.show()

    def run(self):
        try:
            self.fixData()
            self.checkNaNorNull()
            self.plotData()
        except Exception as e:
            logging.exception(f"Error during data fix: {e}")
            raise
