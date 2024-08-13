from extract import get_data


def main():
    search_area = 'Epsom'
    limit = 10

    print(f'Running Extract for {search_area}')
    sold_properties_df = get_data(search_area, limit)

    return sold_properties_df

if __name__ == '__main__':
    main()