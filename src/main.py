from extract import get_data
from plots import plot_property_scatter, plot_property_prices_over_time

def main():
    search_area = 'Epsom'
    limit = 10

    print(f'Running Extract for {search_area}')
    sold_properties_df = get_data(search_area, limit)

    plot_property_scatter(sold_properties_df)
    plot_property_prices_over_time(sold_properties_df)

    return sold_properties_df

if __name__ == '__main__':
    main()