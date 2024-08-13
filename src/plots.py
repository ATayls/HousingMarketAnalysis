import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple


def plot_property_scatter(sold_properties_df: pd.DataFrame, ncols: int = 3,
                          figsize: Optional[Tuple[int, int]] = (15, 10)) -> None:
    """
    Plots a series of scatter plots showing property prices against the date sold,
    for different property types and bedroom counts.

    :param sold_properties_df: The DataFrame containing property data.
    :type sold_properties_df: pd.DataFrame
    :param ncols: Number of columns in the subplot grid (default is 3).
    :type ncols: int
    :param figsize: Size of the overall figure (default is (15, 10)).
    :type figsize: Optional[Tuple[int, int]]
    :return: None
    :rtype: None
    """
    property_types = sold_properties_df['propertyType'].unique()
    nrows = len(property_types)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, squeeze=False)

    for row, property_type in enumerate(property_types):
        for col, bedrooms in enumerate([2, 3, 4]):
            filtered_df = sold_properties_df[
                (sold_properties_df['propertyType'] == property_type) &
                (sold_properties_df['bedrooms'] == bedrooms)
                ]

            if not filtered_df.empty:
                filtered_df.plot.scatter(ax=axes[row, col], x='dateSold', y='displayPrice', c='blue', alpha=0.5)
                axes[row, col].set_ylabel(property_type, rotation=0, size='large')
                axes[row, col].set_title(f'{bedrooms} Bedrooms')
            else:
                axes[row, col].set_visible(False)

    plt.tight_layout()
    plt.show()


def plot_property_prices_over_time(sold_properties_df: pd.DataFrame, types: Optional[List[str]] = None, ncols: int = 2,
                                   resample_period: str = '6M') -> None:
    """
    Plots the average property prices over time for different property types and bedroom counts.

    :param sold_properties_df: The DataFrame containing property data.
    :type sold_properties_df: pd.DataFrame
    :param types: List of property types to include in the plot (default is ['Semi-Detached', 'Terraced']).
    :type types: Optional[List[str]]
    :param ncols: Number of columns in the subplot grid (default is 2).
    :type ncols: int
    :param resample_period: The period for resampling the time series (default is '6M').
    :type resample_period: str
    :return: None
    :rtype: None
    """
    if types is None:
        types = ['Semi-Detached', 'Terraced']

    plotting_df = pd.DataFrame()

    for property_type in types:
        for bedrooms in [2, 3]:
            line_name = f'{bedrooms}Bed_{property_type}'
            filtered_df = sold_properties_df[
                (sold_properties_df['propertyType'] == property_type) &
                (sold_properties_df['bedrooms'] == bedrooms)
                ]

            if not filtered_df.empty:
                filtered_df = filtered_df[['displayPrice', 'dateSold']].sort_values(by='dateSold')
                filtered_df = filtered_df.groupby(by='dateSold').mean().rename(columns={'displayPrice': line_name})

                if plotting_df.empty:
                    plotting_df = filtered_df
                else:
                    plotting_df = plotting_df.join(filtered_df, how='outer')

    plotting_df = plotting_df.resample(resample_period).mean()
    plotting_df = plotting_df.interpolate(method='linear', limit_direction='forward', axis=0)

    plotting_df.plot(figsize=(10, 6))
    plt.title('Average Property Prices Over Time')
    plt.ylabel('Average Display Price')
    plt.xlabel('Date Sold')
    plt.legend(title='Property Type and Bedrooms')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
