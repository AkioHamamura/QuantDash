import unittest
import asyncio

from http.client import responses
from .data.data_fetcher import (write_available_tickers, fetch_cached_data, fetch_stock_data)
from .api.server import *
from .api.server import BacktestRequest
from .utils.globals import *
from .utils.s3crud import *

class S3OperationsTest(unittest.TestCase):
    """Test suite for S3 bucket operations"""

    def setUp(self):
        """Set up test data"""
        self.test_data = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        self.test_object_key = 'test.csv'
        self.read_object_key = 'cache/PLTR_max_None_None_1d_data.parquet'

    def test_list_bucket_objects(self):
        """Test listing objects in S3 bucket"""
        result = list_s3_objects_client(BUCKET_NAME)
        self.assertIsInstance(result, list, "list_s3_objects_client did not return a list")

    def test_upload_object(self):
        """Test uploading object to S3 bucket"""
        result = put_s3_objects_client(
            bucket_name=BUCKET_NAME,
            data=self.test_data.to_csv(),
            object_key=self.test_object_key
        )
        self.assertIn(result['statusCode'], [200, 201],
                     "Failed to upload object to bucket")

    def test_read_object(self):
        """Test reading object from S3 bucket"""
        result = read_s3_object_client(
            bucket_name=BUCKET_NAME,
            object_key=self.read_object_key
        )
        self.assertIn(result['statusCode'], [200, 201],
                     "Failed to read object from bucket")

class DataFetcherTest(unittest.TestCase):
    """Test suite for data fetcher functionality"""

    def test_write_available_tickers(self):
        """Test writing available tickers"""
        try:
            write_available_tickers(cache_dir=DATA_PATH)
            self.assertTrue(True)  # If we reach here, no exception was raised
        except Exception as e:
            self.fail(f"write_available_tickers raised an exception: {str(e)}")

    def test_fetch_cached_date(self):
        try:
            result = fetch_cached_data(ticker="AAPL", period="max", interval="1d")
            self.assertIsInstance(result, pd.DataFrame, "fetch_cached_data did not return a DataFrame")
            self.assertGreater(result.shape[0], 0, "fetch_cached_data returned an empty DataFrame")
        except Exception as e:
            self.fail(f"fetch_cached_data raised an exception: {str(e)}")

    def test_fetch_stock_data(self):
        try:
            result = fetch_stock_data(ticker="NVDA", period="max", interval="1d")
            self.assertIsInstance(result, pd.DataFrame, "fetch_stock_data did not return a DataFrame")
            self.assertGreater(result.shape[0], 0, "fetch_stock_data returned an empty DataFrame")
        except Exception as e:
            self.fail(f"fetch_stock_data raised an exception: {str(e)}")

class apiserverTest(unittest.TestCase):
    """Test suite for API server functionality"""
    def test_root(self):
        try:
            result = root()
            self.assertEqual(result['statusCode'], 200, "root endpoint returned an error")
        except Exception as e:
            self.fail(f"root endpoint raised an exception: {str(e)}")

    def test_get_available_tickers(self):
        #This will test if tickers can be retrieved
        try:

            result = asyncio.run(get_available_tickers())
            self.assertEqual(result['success'], True, False)

        except Exception as e:
            self.fail(f"get_available_tickers raised an exception: {str(e)}")

    def test_get_available_strategies(self):
        #Test if the strategies dict is returned properly
        try:
            result = asyncio.run(get_available_strategies())
            print(result)
            print(type(result))
            self.assertEqual(result['success'], True, False)
        except Exception as e:
            self.fail(f"get_available_strategies raised an exception: {str(e)}")

    def test_run_backtest(self):
        btrequest = {
            "route": "/test",
            "back_test_request": {
                "symbol": "AMD",
                "period": "max",
                "algorithm": "moving_average_crossover",
                "initial_cash": "10000"
            }
        }

        try:
            result = asyncio.run(run_backtest(btrequest))
            self.assertEqual(result['success'], True, False)
            self.assertIsInstance(result['data'], dict, "run_backtest did not return a dictionary")
        except Exception as e:
            self.fail(f"run_backtest raised an exception: {str(e)}")

def run_tests():
    """Run all test suites"""
    test_suites = [
        unittest.TestLoader().loadTestsFromTestCase(S3OperationsTest),
        unittest.TestLoader().loadTestsFromTestCase(DataFetcherTest),
        unittest.TestLoader().loadTestsFromTestCase(apiserverTest)
    ]
    
    combined_suite = unittest.TestSuite(test_suites)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit_code = 0 if success else 1
    exit(exit_code)