import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging

csvRoute = './MyAutomationProject/STONKMarket/stokedata/NVDA.csv'
graphRoute= 'MyAutomationProject\\STONKMarket\\Graph'
Stockdata = pd.read_csv(csvRoute)

def checkNaNorNull(data):
    if data.isna().values.any():
        logging.warning(f"Data contains NaN or null values: {data.isna().sum()}" )
        data.dropna(inplace=True)
    else:
        logging.info("Data contains no NaN or null values")

def fixData(data):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
    data['Stock Price'] = pd.to_numeric(data['Stock Price'], errors='coerce', )
    data['Price Change'] = pd.to_numeric(data['Price Change'], errors='coerce')
    data['Percentage Change'] = data['Percentage Change'].str.replace('(', '', regex=False).str.replace(')', '', regex=False).str.replace('%', '', regex=False).astype(float)
    return data

def plotData(data):
    fig, ax1 = plt.subplots(figsize=(15, 8))

    # Plotting Stock Price on the primary y-axis
    ax1.plot(data['Timestamp'], data['Stock Price'], label='Stock Price', color='blue')
    ax1.set_xlabel('Date/Time')
    ax1.set_ylabel('Stock Price ($)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Creating a secondary y-axis for Price Change
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(data['Timestamp'], data['Price Change'], label='Price Change', color='red')
    ax2.set_ylabel('Price Change ($)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Optional: A third y-axis can be added if needed
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))  # offset the right spine of ax3
    ax3.plot(data['Timestamp'], data['Percentage Change'], label='Percentage Change', color='green')
    ax3.set_ylabel('Percentage Change (%)', color='green')
    ax3.tick_params(axis='y', labelcolor='green')

    # Title and grid
    ax1.set_title('NVDA Stock Price Over Time')
    ax1.grid(True)

    # Handles and labels for each dataset (legend)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left')

    plt.savefig(graphRoute + '\\NVDAStockGraph.png')
    plt.show()


def run():
    try:
        data = fixData(Stockdata)
        checkNaNorNull(data)
        plotData(data)
    except Exception as e:
        logging.exception(f"Error during data fix: {e}")
        raise

if __name__ == '__main__':
    run()



    

