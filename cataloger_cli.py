from cataloger import build_catalog

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv-folder')
    parser.add_argument('--sqlite')
    parser.add_argument('--sql')
    parser.add_argument('--out', default='catalog.json')
    args = parser.parse_args()
    build_catalog(csv_folder=args.csv_folder, sqlite_path=args.sqlite, sql_conn=args.sql, out_path=args.out)
    print('Catalog generation complete')
