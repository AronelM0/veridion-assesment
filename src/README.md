# Running the proof of concept

From the repository root, use Python 3.12. The script uses the standard library.

```sh
python src/pilot.py report
```

To reproduce the sample and the MHRA matches from the public source files, run these commands in order.

```sh
python src/pilot.py fetch
python src/pilot.py sample
python src/pilot.py discover
python src/pilot.py report
```

`fetch` downloads the government CSV files. `sample` regenerates the 30-company draw and `discover` regenerates the MHRA candidates. `report` uses the recorded website reviews and HMRC verdicts to regenerate `data/results.csv`. To repeat a VAT check, enter the recorded candidate in the [public HMRC checker](https://www.gov.uk/check-uk-vat-number) and compare the returned business with the cited identity evidence.
