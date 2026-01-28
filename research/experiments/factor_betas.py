import sf_quant.data as sfd
import polars as pl
import datetime as dt
import polars_ols as pls

start = dt.date(2023, 1, 1)
end = dt.date(2024, 12, 31)

assets = sfd.load_assets(
    start=start,
    end=end,
    in_universe=True,
    columns=[
        'date',
        'barrid',
        'ticker',
        'cusip',
        'price',
        'return'
    ]
)

print(assets)

factors = sfd.load_fama_french(
    start=start,
    end=end
)

print(factors)

data = (
    assets
    .join(
        other=factors,
        on='date',
        how='left'
    )
    .with_columns(
        pl.col('return').truediv(100)
    )
    .with_columns(
        pl.col('return').sub('rf').alias('return_rf')
    )
    .select(
        'date', 'barrid', 'return_rf', 'mkt_rf', 'smb', 'hml',
    )
)

print(data)

coefficients = (
    data
    .sort('barrid', 'date')
    .with_columns(
        pl.lit(1.0).alias('const')
    )
    .with_columns(
        pl.col('return_rf')
        .least_squares
        .rolling_ols(
            pl.col('const', 'mkt_rf', 'smb', 'hml'), 
            window_size=252, 
            min_periods=252,
            mode='coefficients'
        )
        .over('barrid')
        .alias('B')
    )
    .unnest('B', separator="_")
)

print(coefficients)
print(coefficients.drop_nulls('B_const'))
